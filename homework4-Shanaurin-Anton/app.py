from datetime import datetime
from pprint import pprint
from typing import Optional

from pymongo import MongoClient, ASCENDING, DESCENDING


class OrdersRepository:
    """
    Пример репозитория для коллекции orders.
    Структура документа (пример):

    {
        "_id": ObjectId,
        "customer": {
            "customer_id": "C001",
            "name": "Иван Иванов",
            "email": "ivan@example.com",
            "segment": "b2c"
        },
        "items": [
            {
                "sku": "SKU-1001",
                "name": "Ноутбук",
                "category": "electronics",
                "price": 60000,
                "quantity": 1
            },
            ...
        ],
        "shipping": {
            "address": {
                "city": "Москва",
                "street": "Тверская, 1",
                "zip": "125009"
            },
            "method": "courier",
            "cost": 500
        },
        "payment": {
            "method": "card",
            "status": "paid"
        },
        "order_date": datetime,
        "status": "delivered" / "cancelled" / "processing",
        "total_amount": 60500
    }
    """

    def __init__(self, mongo_uri="mongodb://localhost:27017", db_name="shop_db"):
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.collection = self.db["orders"]

        # Создаём индексы на часто используемых полях
        self._ensure_indexes()

    def _ensure_indexes(self):
        """
        Создание индексов.
        Предположим, что часто фильтруем по:
            - customer.customer_id
            - order_date
            - status
            - items.category
            - shipping.address.city
        """
        self.collection.create_index(
            [("customer.customer_id", ASCENDING)], name="idx_customer_id"
        )
        self.collection.create_index(
            [("order_date", DESCENDING)], name="idx_order_date"
        )
        self.collection.create_index([("status", ASCENDING)], name="idx_status")
        # Многозначное поле items.category — будет мультииндекс (multi-key)
        self.collection.create_index(
            [("items.category", ASCENDING)], name="idx_items_category"
        )
        self.collection.create_index(
            [("shipping.address.city", ASCENDING)], name="idx_city"
        )

    # ---------------- Базовые методы работы с коллекцией ----------------

    def insert_order(self, order_data: dict):
        """
        Вставка одного заказа.
        """
        return self.collection.insert_one(order_data).inserted_id

    def insert_many_orders(self, orders: list[dict]):
        """
        Массовая вставка заказов.
        """
        result = self.collection.insert_many(orders)
        return result.inserted_ids

    def get_order_by_id(self, order_id):
        """
        Получение заказа по _id.
        """
        return self.collection.find_one({"_id": order_id})

    def get_orders_by_customer(self, customer_id: str, limit: int = 10):
        """
        Использует индекс idx_customer_id.
        """
        cursor = (
            self.collection.find({"customer.customer_id": customer_id})
            .sort("order_date", DESCENDING)
            .limit(limit)
        )
        return list(cursor)

    def update_order_status(self, order_id, new_status: str):
        """
        Обновление статуса заказа.
        """
        return self.collection.update_one(
            {"_id": order_id}, {"$set": {"status": new_status}}
        )

    def delete_order(self, order_id):
        """
        Удаление заказа.
        """
        return self.collection.delete_one({"_id": order_id})

    # --------------- Агрегационные аналитические запросы ---------------

    def total_revenue_by_city(self, start_date: datetime, end_date: datetime):
        """
        Посчитать выручку по городам за период.
        Использует индексы:
            - order_date (idx_order_date)
            - shipping.address.city (idx_city)
        """
        pipeline = [
            {
                "$match": {
                    "order_date": {"$gte": start_date, "$lte": end_date},
                    "status": "delivered",
                }
            },
            {
                "$group": {
                    "_id": "$shipping.address.city",
                    "total_revenue": {"$sum": "$total_amount"},
                    "orders_count": {"$sum": 1},
                }
            },
            {"$sort": {"total_revenue": -1}},
        ]
        return list(self.collection.aggregate(pipeline))

    def avg_check_by_segment(self, start_date: datetime, end_date: datetime):
        """
        Средний чек по сегментам клиентов (b2c/b2b и т.п.) за период.
        Индексы:
          - order_date (idx_order_date)
          - customer.segment можно проиндексировать дополнительно при необходимости.
        """
        # при желании можно добавить индекс:
        # self.collection.create_index([("customer.segment", ASCENDING)], name="idx_segment")

        pipeline = [
            {
                "$match": {
                    "order_date": {"$gte": start_date, "$lte": end_date},
                    "status": "delivered",
                }
            },
            {
                "$group": {
                    "_id": "$customer.segment",
                    "avg_check": {"$avg": "$total_amount"},
                    "orders_count": {"$sum": 1},
                }
            },
            {"$sort": {"avg_check": -1}},
        ]
        return list(self.collection.aggregate(pipeline))

    def top_categories(self, limit: int = 5):
        """
        Топ категорий товаров по выручке за всё время.
        Использует индекс по items.category (idx_items_category).
        """
        pipeline = [
            {"$unwind": "$items"},
            {
                "$group": {
                    "_id": "$items.category",
                    "revenue": {
                        "$sum": {"$multiply": ["$items.price", "$items.quantity"]}
                    },
                    "items_sold": {"$sum": "$items.quantity"},
                }
            },
            {"$sort": {"revenue": -1}},
            {"$limit": limit},
        ]
        return list(self.collection.aggregate(pipeline))

    def monthly_revenue_by_status(self):
        """
        Помесячная выручка в разрезе статусов заказов.
        Использует индекс order_date и status.
        """
        pipeline = [
            {
                "$group": {
                    "_id": {
                        "year": {"$year": "$order_date"},
                        "month": {"$month": "$order_date"},
                        "status": "$status",
                    },
                    "total_revenue": {"$sum": "$total_amount"},
                    "orders_count": {"$sum": 1},
                }
            },
            {"$sort": {"_id.year": 1, "_id.month": 1, "_id.status": 1}},
        ]
        return list(self.collection.aggregate(pipeline))

    def get_orders_with_filter(
        self,
        city: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 20,
    ):
        """
        Пример произвольного фильтра, который максимально использует индексы:
          - по городу (shipping.address.city)
          - по категории товара (items.category)
          - по статусу (status)
        """
        query = {}
        if city:
            query["shipping.address.city"] = city
        if category:
            query["items.category"] = category
        if status:
            query["status"] = status

        cursor = self.collection.find(query).sort("order_date", DESCENDING).limit(limit)
        return list(cursor)


def seed_data(repo: OrdersRepository):
    """
    Пример заполнения коллекции тестовыми данными.
    Запускайте один раз или с очисткой коллекции.
    """
    repo.collection.delete_many({})  # очистка для удобства

    orders = [
        {
            "customer": {
                "customer_id": "C001",
                "name": "Иван Иванов",
                "email": "ivan@example.com",
                "segment": "b2c",
            },
            "items": [
                {
                    "sku": "SKU-1001",
                    "name": "Ноутбук",
                    "category": "electronics",
                    "price": 60000,
                    "quantity": 1,
                },
                {
                    "sku": "SKU-2001",
                    "name": "Мышь",
                    "category": "accessories",
                    "price": 1500,
                    "quantity": 2,
                },
            ],
            "shipping": {
                "address": {"city": "Москва", "street": "Тверская, 1", "zip": "125009"},
                "method": "courier",
                "cost": 500,
            },
            "payment": {"method": "card", "status": "paid"},
            "order_date": datetime(2024, 10, 1, 14, 30),
            "status": "delivered",
            "total_amount": 60000 + 1500 * 2 + 500,
        },
        {
            "customer": {
                "customer_id": "C002",
                "name": "ООО Ромашка",
                "email": "info@romashka.ru",
                "segment": "b2b",
            },
            "items": [
                {
                    "sku": "SKU-3001",
                    "name": "Принтер",
                    "category": "electronics",
                    "price": 20000,
                    "quantity": 3,
                }
            ],
            "shipping": {
                "address": {
                    "city": "Санкт-Петербург",
                    "street": "Невский проспект, 10",
                    "zip": "191025",
                },
                "method": "pickup",
                "cost": 0,
            },
            "payment": {"method": "invoice", "status": "pending"},
            "order_date": datetime(2024, 10, 5, 11, 0),
            "status": "processing",
            "total_amount": 20000 * 3,
        },
        {
            "customer": {
                "customer_id": "C001",
                "name": "Иван Иванов",
                "email": "ivan@example.com",
                "segment": "b2c",
            },
            "items": [
                {
                    "sku": "SKU-4001",
                    "name": "Книга",
                    "category": "books",
                    "price": 800,
                    "quantity": 4,
                }
            ],
            "shipping": {
                "address": {"city": "Москва", "street": "Арбат, 12", "zip": "119002"},
                "method": "post",
                "cost": 300,
            },
            "payment": {"method": "card", "status": "paid"},
            "order_date": datetime(2024, 10, 7, 9, 15),
            "status": "delivered",
            "total_amount": 800 * 4 + 300,
        },
    ]

    repo.insert_many_orders(orders)


if __name__ == "__main__":
    repo = OrdersRepository()

    # 1. Наполнить коллекцию тестовыми данными
    seed_data(repo)

    # 2. Примеры вызова методов репозитория и агрегаций

    print("Заказы клиента C001:")
    pprint(repo.get_orders_by_customer("C001"))

    print("\nВыручка по городам за 2024-10-01..2024-10-31:")
    pprint(repo.total_revenue_by_city(datetime(2024, 10, 1), datetime(2024, 10, 31)))

    print("\nСредний чек по сегментам:")
    pprint(repo.avg_check_by_segment(datetime(2024, 10, 1), datetime(2024, 10, 31)))

    print("\nТоп категорий по выручке:")
    pprint(repo.top_categories())

    print("\nПомесячная выручка по статусам:")
    pprint(repo.monthly_revenue_by_status())

    print("\nФильтр: город Москва, статус delivered:")
    pprint(repo.get_orders_with_filter(city="Москва", status="delivered"))
