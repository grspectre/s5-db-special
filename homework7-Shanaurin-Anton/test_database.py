import pytest
import psycopg2
from psycopg2.extras import RealDictCursor
from faker import Faker
from datetime import datetime, timedelta
import random

fake = Faker('ru_RU')

# Параметры подключения
DB_CONFIG = {
    'host': 'localhost',
    'port': 5436,
    'database': 'testdb',
    'user': 'testuser',
    'password': 'testpass'
}

@pytest.fixture(scope='function')
def db_connection():
    """Фикстура для подключения к БД с транзакцией"""
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = False
    yield conn
    conn.rollback()
    conn.close()

@pytest.fixture(scope='function')
def cursor(db_connection):
    """Фикстура для курсора"""
    cur = db_connection.cursor(cursor_factory=RealDictCursor)
    yield cur
    cur.close()

@pytest.fixture(scope='session', autouse=True)
def setup_database():
    """Создание таблиц перед всеми тестами"""
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    cur = conn.cursor()
    
    # Удаление таблиц если существуют
    cur.execute("DROP TABLE IF EXISTS orders CASCADE")
    cur.execute("DROP TABLE IF EXISTS products CASCADE")
    cur.execute("DROP TABLE IF EXISTS users CASCADE")
    
    # Создание таблиц
    cur.execute("""
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            name VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cur.execute("""
        CREATE TABLE products (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            price DECIMAL(10, 2) NOT NULL CHECK (price >= 0),
            stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0)
        )
    """)
    
    cur.execute("""
        CREATE TABLE orders (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            product_id INTEGER NOT NULL REFERENCES products(id),
            quantity INTEGER NOT NULL CHECK (quantity > 0),
            total_price DECIMAL(10, 2) NOT NULL,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cur.close()
    conn.close()
    yield
    
    # Очистка после всех тестов
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS orders CASCADE")
    cur.execute("DROP TABLE IF EXISTS products CASCADE")
    cur.execute("DROP TABLE IF EXISTS users CASCADE")
    cur.close()
    conn.close()

# ============== ПОЗИТИВНЫЕ ТЕСТЫ ==============

class TestUsersPositive:
    """Позитивные тесты для таблицы users"""
    
    def test_create_user(self, cursor, db_connection):
        """Тест: создание пользователя"""
        email = fake.email()
        name = fake.name()
        
        cursor.execute(
            "INSERT INTO users (email, name) VALUES (%s, %s) RETURNING id, email, name",
            (email, name)
        )
        result = cursor.fetchone()
        
        assert result['email'] == email
        assert result['name'] == name
        assert result['id'] is not None
    
    def test_read_user(self, cursor, db_connection):
        """Тест: чтение пользователя"""
        email = fake.email()
        name = fake.name()
        
        cursor.execute("INSERT INTO users (email, name) VALUES (%s, %s) RETURNING id", (email, name))
        user_id = cursor.fetchone()['id']
        
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        result = cursor.fetchone()
        
        assert result['id'] == user_id
        assert result['email'] == email
        assert result['name'] == name
    
    def test_update_user(self, cursor, db_connection):
        """Тест: обновление пользователя"""
        cursor.execute("INSERT INTO users (email, name) VALUES (%s, %s) RETURNING id", 
                      (fake.email(), fake.name()))
        user_id = cursor.fetchone()['id']
        
        new_name = fake.name()
        cursor.execute("UPDATE users SET name = %s WHERE id = %s", (new_name, user_id))
        
        cursor.execute("SELECT name FROM users WHERE id = %s", (user_id,))
        result = cursor.fetchone()
        
        assert result['name'] == new_name
    
    def test_delete_user(self, cursor, db_connection):
        """Тест: удаление пользователя"""
        cursor.execute("INSERT INTO users (email, name) VALUES (%s, %s) RETURNING id", 
                      (fake.email(), fake.name()))
        user_id = cursor.fetchone()['id']
        
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        result = cursor.fetchone()
        
        assert result is None

class TestProductsPositive:
    """Позитивные тесты для таблицы products"""
    
    def test_create_product(self, cursor, db_connection):
        """Тест: создание товара"""
        name = fake.word()
        price = round(random.uniform(10, 1000), 2)
        stock = random.randint(0, 100)
        
        cursor.execute(
            "INSERT INTO products (name, price, stock) VALUES (%s, %s, %s) RETURNING id, name, price, stock",
            (name, price, stock)
        )
        result = cursor.fetchone()
        
        assert result['name'] == name
        assert float(result['price']) == price
        assert result['stock'] == stock
    
    def test_read_product(self, cursor, db_connection):
        """Тест: чтение товара"""
        name = fake.word()
        price = round(random.uniform(10, 1000), 2)
        
        cursor.execute("INSERT INTO products (name, price) VALUES (%s, %s) RETURNING id", (name, price))
        product_id = cursor.fetchone()['id']
        
        cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
        result = cursor.fetchone()
        
        assert result['id'] == product_id
        assert result['name'] == name
        assert float(result['price']) == price
    
    def test_update_product(self, cursor, db_connection):
        """Тест: обновление товара"""
        cursor.execute("INSERT INTO products (name, price) VALUES (%s, %s) RETURNING id", 
                      (fake.word(), 100.00))
        product_id = cursor.fetchone()['id']
        
        new_price = 150.50
        cursor.execute("UPDATE products SET price = %s WHERE id = %s", (new_price, product_id))
        
        cursor.execute("SELECT price FROM products WHERE id = %s", (product_id,))
        result = cursor.fetchone()
        
        assert float(result['price']) == new_price
    
    def test_delete_product(self, cursor, db_connection):
        """Тест: удаление товара"""
        cursor.execute("INSERT INTO products (name, price) VALUES (%s, %s) RETURNING id", 
                      (fake.word(), 100.00))
        product_id = cursor.fetchone()['id']
        
        cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
        cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
        result = cursor.fetchone()
        
        assert result is None

class TestOrdersPositive:
    """Позитивные тесты для таблицы orders"""
    
    def test_create_order(self, cursor, db_connection):
        """Тест: создание заказа"""
        # Создаем пользователя и товар
        cursor.execute("INSERT INTO users (email, name) VALUES (%s, %s) RETURNING id", 
                      (fake.email(), fake.name()))
        user_id = cursor.fetchone()['id']
        
        price = 100.00
        cursor.execute("INSERT INTO products (name, price) VALUES (%s, %s) RETURNING id", 
                      (fake.word(), price))
        product_id = cursor.fetchone()['id']
        
        quantity = 3
        total_price = price * quantity
        
        cursor.execute(
            "INSERT INTO orders (user_id, product_id, quantity, total_price) VALUES (%s, %s, %s, %s) RETURNING id",
            (user_id, product_id, quantity, total_price)
        )
        result = cursor.fetchone()
        
        assert result['id'] is not None
    
    def test_read_order(self, cursor, db_connection):
        """Тест: чтение заказа"""
        cursor.execute("INSERT INTO users (email, name) VALUES (%s, %s) RETURNING id", 
                      (fake.email(), fake.name()))
        user_id = cursor.fetchone()['id']
        
        cursor.execute("INSERT INTO products (name, price) VALUES (%s, %s) RETURNING id", 
                      (fake.word(), 100.00))
        product_id = cursor.fetchone()['id']
        
        cursor.execute(
            "INSERT INTO orders (user_id, product_id, quantity, total_price) VALUES (%s, %s, %s, %s) RETURNING id",
            (user_id, product_id, 2, 200.00)
        )
        order_id = cursor.fetchone()['id']
        
        cursor.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
        result = cursor.fetchone()
        
        assert result['id'] == order_id
        assert result['user_id'] == user_id
        assert result['product_id'] == product_id
    
    def test_update_order(self, cursor, db_connection):
        """Тест: обновление заказа"""
        cursor.execute("INSERT INTO users (email, name) VALUES (%s, %s) RETURNING id", 
                      (fake.email(), fake.name()))
        user_id = cursor.fetchone()['id']
        
        cursor.execute("INSERT INTO products (name, price) VALUES (%s, %s) RETURNING id", 
                      (fake.word(), 100.00))
        product_id = cursor.fetchone()['id']
        
        cursor.execute(
            "INSERT INTO orders (user_id, product_id, quantity, total_price) VALUES (%s, %s, %s, %s) RETURNING id",
            (user_id, product_id, 2, 200.00)
        )
        order_id = cursor.fetchone()['id']
        
        new_quantity = 5
        new_total = 500.00
        cursor.execute("UPDATE orders SET quantity = %s, total_price = %s WHERE id = %s", 
                      (new_quantity, new_total, order_id))
        
        cursor.execute("SELECT quantity, total_price FROM orders WHERE id = %s", (order_id,))
        result = cursor.fetchone()
        
        assert result['quantity'] == new_quantity
        assert float(result['total_price']) == new_total
    
    def test_delete_order(self, cursor, db_connection):
        """Тест: удаление заказа"""
        cursor.execute("INSERT INTO users (email, name) VALUES (%s, %s) RETURNING id", 
                      (fake.email(), fake.name()))
        user_id = cursor.fetchone()['id']
        
        cursor.execute("INSERT INTO products (name, price) VALUES (%s, %s) RETURNING id", 
                      (fake.word(), 100.00))
        product_id = cursor.fetchone()['id']
        
        cursor.execute(
            "INSERT INTO orders (user_id, product_id, quantity, total_price) VALUES (%s, %s, %s, %s) RETURNING id",
            (user_id, product_id, 2, 200.00)
        )
        order_id = cursor.fetchone()['id']
        
        cursor.execute("DELETE FROM orders WHERE id = %s", (order_id,))
        cursor.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
        result = cursor.fetchone()
        
        assert result is None

# ============== НЕГАТИВНЫЕ ТЕСТЫ ==============

class TestUsersNegative:
    """Негативные тесты для таблицы users"""
    
    def test_duplicate_email(self, cursor, db_connection):
        """Тест: дублирование email (должно вызвать ошибку)"""
        email = fake.email()
        cursor.execute("INSERT INTO users (email, name) VALUES (%s, %s)", (email, fake.name()))
        
        with pytest.raises(psycopg2.IntegrityError):
            cursor.execute("INSERT INTO users (email, name) VALUES (%s, %s)", (email, fake.name()))
    
    def test_null_email(self, cursor, db_connection):
        """Тест: email = NULL (должно вызвать ошибку)"""
        with pytest.raises(psycopg2.IntegrityError):
            cursor.execute("INSERT INTO users (email, name) VALUES (NULL, %s)", (fake.name(),))
    
    def test_null_name(self, cursor, db_connection):
        """Тест: name = NULL (должно вызвать ошибку)"""
        with pytest.raises(psycopg2.IntegrityError):
            cursor.execute("INSERT INTO users (email, name) VALUES (%s, NULL)", (fake.email(),))

class TestProductsNegative:
    """Негативные тесты для таблицы products"""
    
    def test_negative_price(self, cursor, db_connection):
        """Тест: отрицательная цена (должно вызвать ошибку)"""
        with pytest.raises(psycopg2.IntegrityError):
            cursor.execute("INSERT INTO products (name, price) VALUES (%s, %s)", (fake.word(), -10.00))
    
    def test_negative_stock(self, cursor, db_connection):
        """Тест: отрицательный остаток (должно вызвать ошибку)"""
        with pytest.raises(psycopg2.IntegrityError):
            cursor.execute("INSERT INTO products (name, price, stock) VALUES (%s, %s, %s)", 
                          (fake.word(), 100.00, -5))
    
    def test_null_price(self, cursor, db_connection):
        """Тест: price = NULL (должно вызвать ошибку)"""
        with pytest.raises(psycopg2.IntegrityError):
            cursor.execute("INSERT INTO products (name, price) VALUES (%s, NULL)", (fake.word(),))

class TestOrdersNegative:
    """Негативные тесты для таблицы orders"""
    
    def test_invalid_user_id(self, cursor, db_connection):
        """Тест: несуществующий user_id (должно вызвать ошибку)"""
        cursor.execute("INSERT INTO products (name, price) VALUES (%s, %s) RETURNING id", 
                      (fake.word(), 100.00))
        product_id = cursor.fetchone()['id']
        
        with pytest.raises(psycopg2.IntegrityError):
            cursor.execute(
                "INSERT INTO orders (user_id, product_id, quantity, total_price) VALUES (%s, %s, %s, %s)",
                (99999, product_id, 1, 100.00)
            )
    
    def test_invalid_product_id(self, cursor, db_connection):
        """Тест: несуществующий product_id (должно вызвать ошибку)"""
        cursor.execute("INSERT INTO users (email, name) VALUES (%s, %s) RETURNING id", 
                      (fake.email(), fake.name()))
        user_id = cursor.fetchone()['id']
        
        with pytest.raises(psycopg2.IntegrityError):
            cursor.execute(
                "INSERT INTO orders (user_id, product_id, quantity, total_price) VALUES (%s, %s, %s, %s)",
                (user_id, 99999, 1, 100.00)
            )
    
    def test_zero_quantity(self, cursor, db_connection):
        """Тест: quantity = 0 (должно вызвать ошибку)"""
        cursor.execute("INSERT INTO users (email, name) VALUES (%s, %s) RETURNING id", 
                      (fake.email(), fake.name()))
        user_id = cursor.fetchone()['id']
        
        cursor.execute("INSERT INTO products (name, price) VALUES (%s, %s) RETURNING id", 
                      (fake.word(), 100.00))
        product_id = cursor.fetchone()['id']
        
        with pytest.raises(psycopg2.IntegrityError):
            cursor.execute(
                "INSERT INTO orders (user_id, product_id, quantity, total_price) VALUES (%s, %s, %s, %s)",
                (user_id, product_id, 0, 0.00)
            )
    
    def test_cascade_delete(self, cursor, db_connection):
        """Тест: каскадное удаление заказов при удалении пользователя"""
        cursor.execute("INSERT INTO users (email, name) VALUES (%s, %s) RETURNING id", 
                      (fake.email(), fake.name()))
        user_id = cursor.fetchone()['id']
        
        cursor.execute("INSERT INTO products (name, price) VALUES (%s, %s) RETURNING id", 
                      (fake.word(), 100.00))
        product_id = cursor.fetchone()['id']
        
        cursor.execute(
            "INSERT INTO orders (user_id, product_id, quantity, total_price) VALUES (%s, %s, %s, %s) RETURNING id",
            (user_id, product_id, 1, 100.00)
        )
        order_id = cursor.fetchone()['id']
        
        # Удаляем пользователя
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        
        # Проверяем, что заказ тоже удалился
        cursor.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
        result = cursor.fetchone()
        
        assert result is None
    