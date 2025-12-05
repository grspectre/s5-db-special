"""Конфигурация pytest и фикстуры"""

import pytest
import psycopg2
from faker import Faker
from models import (
    CREATE_USERS_TABLE, 
    CREATE_PRODUCTS_TABLE, 
    CREATE_ORDERS_TABLE,
    DROP_TABLES
)

fake = Faker('ru_RU')

# Конфигурация подключения к БД
DB_CONFIG = {
    'host': 'localhost',
    'port': 5436,
    'database': 'testdb',
    'user': 'testuser',
    'password': 'testpass'
}


@pytest.fixture(scope='session')
def db_connection():
    """Создание соединения с БД на уровне сессии"""
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = False
    yield conn
    conn.close()


@pytest.fixture(scope='function')
def db_cursor(db_connection):
    """Курсор с откатом изменений после каждого теста"""
    cursor = db_connection.cursor()
    
    # Создание таблиц перед тестом
    cursor.execute(DROP_TABLES)
    cursor.execute(CREATE_USERS_TABLE)
    cursor.execute(CREATE_PRODUCTS_TABLE)
    cursor.execute(CREATE_ORDERS_TABLE)
    db_connection.commit()
    
    yield cursor
    
    # Откат всех изменений после теста
    db_connection.rollback()
    cursor.close()


@pytest.fixture
def fake_user():
    """Генерация данных для пользователя"""
    return {
        'username': fake.user_name(),
        'email': fake.email(),
        'age': fake.random_int(min=18, max=80)
    }


@pytest.fixture
def fake_users():
    """Генерация списка пользователей"""
    return [
        {
            'username': fake.unique.user_name(),
            'email': fake.unique.email(),
            'age': fake.random_int(min=18, max=80)
        }
        for _ in range(5)
    ]


@pytest.fixture
def fake_product():
    """Генерация данных для продукта"""
    return {
        'name': fake.catch_phrase(),
        'price': round(fake.random.uniform(10.0, 1000.0), 2),
        'stock': fake.random_int(min=0, max=100),
        'description': fake.text(max_nb_chars=200)
    }


@pytest.fixture
def fake_products():
    """Генерация списка продуктов"""
    return [
        {
            'name': fake.unique.catch_phrase(),
            'price': round(fake.random.uniform(10.0, 1000.0), 2),
            'stock': fake.random_int(min=0, max=100),
            'description': fake.text(max_nb_chars=200)
        }
        for _ in range(5)
    ]


@pytest.fixture
def inserted_user(db_cursor, fake_user):
    """Вставка пользователя в БД"""
    from models import INSERT_USER
    db_cursor.execute(
        INSERT_USER,
        (fake_user['username'], fake_user['email'], fake_user['age'])
    )
    user_id = db_cursor.fetchone()[0]
    db_cursor.connection.commit()
    return {'id': user_id, **fake_user}


@pytest.fixture
def inserted_product(db_cursor, fake_product):
    """Вставка продукта в БД"""
    from models import INSERT_PRODUCT
    db_cursor.execute(
        INSERT_PRODUCT,
        (fake_product['name'], fake_product['price'], 
         fake_product['stock'], fake_product['description'])
    )
    product_id = db_cursor.fetchone()[0]
    db_cursor.connection.commit()
    return {'id': product_id, **fake_product}
