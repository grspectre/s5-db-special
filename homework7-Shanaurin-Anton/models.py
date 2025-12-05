"""Модели и SQL-запросы для тестирования"""

CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    age INTEGER CHECK (age >= 0 AND age <= 150),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_PRODUCTS_TABLE = """
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) CHECK (price >= 0),
    stock INTEGER DEFAULT 0 CHECK (stock >= 0),
    description TEXT
);
"""

CREATE_ORDERS_TABLE = """
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
    quantity INTEGER CHECK (quantity > 0),
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

DROP_TABLES = """
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS users CASCADE;
"""

# CRUD запросы для Users
INSERT_USER = "INSERT INTO users (username, email, age) VALUES (%s, %s, %s) RETURNING id;"
SELECT_USER_BY_ID = "SELECT * FROM users WHERE id = %s;"
SELECT_ALL_USERS = "SELECT * FROM users;"
UPDATE_USER = "UPDATE users SET username = %s, email = %s, age = %s WHERE id = %s;"
DELETE_USER = "DELETE FROM users WHERE id = %s;"

# CRUD запросы для Products
INSERT_PRODUCT = "INSERT INTO products (name, price, stock, description) VALUES (%s, %s, %s, %s) RETURNING id;"
SELECT_PRODUCT_BY_ID = "SELECT * FROM products WHERE id = %s;"
SELECT_ALL_PRODUCTS = "SELECT * FROM products;"
UPDATE_PRODUCT = "UPDATE products SET name = %s, price = %s, stock = %s WHERE id = %s;"
DELETE_PRODUCT = "DELETE FROM products WHERE id = %s;"

# CRUD запросы для Orders
INSERT_ORDER = "INSERT INTO orders (user_id, product_id, quantity) VALUES (%s, %s, %s) RETURNING id;"
SELECT_ORDER_BY_ID = "SELECT * FROM orders WHERE id = %s;"
SELECT_ORDERS_BY_USER = "SELECT * FROM orders WHERE user_id = %s;"
DELETE_ORDER = "DELETE FROM orders WHERE id = %s;"
