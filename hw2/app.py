import os
import sys
from typing import List, Dict, Any

from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    Integer,
    String,
    select,
    insert,
    update,
    delete,
    text,
)
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError, SQLAlchemyError, DBAPIError

PG_USER = os.getenv("PG_USER", "app")
PG_PASSWORD = os.getenv("PG_PASSWORD", "app")
PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = int(os.getenv("PG_PORT", "5435"))
PG_DB = os.getenv("PG_DB", "appdb")

DATABASE_URL = f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}"

metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(100), nullable=False),
    Column("email", String(255), nullable=False, unique=True),
    Column("age", Integer, nullable=True),
)

def get_engine() -> Engine:
    return create_engine(
        DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        future=True,
    )

def create_schema(engine: Engine) -> None:
    print(">> Создаем схему (create_all if not exists)")
    metadata.create_all(engine, checkfirst=True)

def drop_all_data(engine: Engine) -> None:
    print(">> Очищаем таблицу users")
    try:
        with engine.begin() as conn:
            conn.execute(delete(users))
        print("   OK: очищено")
    except SQLAlchemyError as e:
        print("   ROLLBACK: ошибка при очистке:", repr(e))

def read_all(engine: Engine) -> List[Dict[str, Any]]:
    print(">> Чтение всех пользователей")
    with engine.connect() as conn:
        result = conn.execute(select(users).order_by(users.c.id)).mappings().all()
    rows = [dict(r) for r in result]
    for r in rows:
        print("   row:", r)
    if not rows:
        print("   (пусто)")
    return rows

def create_users(engine: Engine, rows: List[Dict[str, Any]]) -> None:
    print(">> Вставка пользователей")
    try:
        with engine.begin() as conn:
            conn.execute(insert(users), rows)
        print("   OK: добавлены записи:", len(rows))
    except (IntegrityError, SQLAlchemyError) as e:
        print("   ROLLBACK: ошибка при вставке:", repr(e))

def update_user_email(engine: Engine, user_id: int, new_email: str) -> None:
    print(f">> Обновление email пользователя id={user_id} -> {new_email}")
    try:
        with engine.begin() as conn:
            res = conn.execute(
                update(users)
                .where(users.c.id == user_id)
                .values(email=new_email)
                .returning(users.c.id, users.c.email)
            ).mappings().all()
        if res:
            print("   OK:", res[0])
        else:
            print("   Нет такого пользователя")
    except (IntegrityError, SQLAlchemyError) as e:
        print("   ROLLBACK: ошибка при обновлении:", repr(e))

def delete_user(engine: Engine, user_id: int) -> None:
    print(f">> Удаление пользователя id={user_id}")
    try:
        with engine.begin() as conn:
            res = conn.execute(
                delete(users)
                .where(users.c.id == user_id)
                .returning(users.c.id)
            ).mappings().all()
        if res:
            print("   OK: удален id", res[0]["id"])
        else:
            print("   Нет такого пользователя")
    except SQLAlchemyError as e:
        print("   ROLLBACK: ошибка при удалении:", repr(e))

def demonstrate_exceptions(engine: Engine) -> None:
    print(">> Демонстрация исключений")
    # 1) Нарушение уникальности email
    try:
        with engine.begin() as conn:
            print("   Пытаемся вставить дубликат email...")
            conn.execute(insert(users), [
                {"name": "Dup1", "email": "dup@example.com", "age": 25},
                {"name": "Dup2", "email": "dup@example.com", "age": 30},
            ])
        print("   ОШИБКА: ожидалось нарушение уникальности, но транзакция прошла")
    except IntegrityError as e:
        print("   OK: поймали IntegrityError (уникальность):", str(e.orig))
    except SQLAlchemyError as e:
        print("   Поймали другой SQLAlchemyError:", repr(e))

    # 2) Ошибка в SQL (синтаксис)
    try:
        with engine.begin() as conn:
            print("   Плохой SQL для демонстрации DBAPIError...")
            conn.execute(text("INSER INTO users(name, email) VALUES ('A','B')"))  # опечатка
    except DBAPIError as e:
        print("   OK: поймали DBAPIError:", str(e.orig))
    except SQLAlchemyError as e:
        print("   Поймали SQLAlchemyError:", repr(e))

def main():
    print("DATABASE_URL:", DATABASE_URL)
    engine = get_engine()

    # 1) Создать таблицу, если нет
    create_schema(engine)

    # 2) Очистить таблицу
    drop_all_data(engine)

    # 3) Добавить данные
    create_users(engine, [
        {"name": "Alice", "email": "alice@example.com", "age": 28},
        {"name": "Bob", "email": "bob@example.com", "age": 35},
        {"name": "Charlie", "email": "charlie@example.com", "age": 22},
    ])

    # 4) Прочитать и показать
    read_all(engine)

    # 5) Найти Bob и обновить email
    with engine.connect() as conn:
        bob_id = conn.execute(
            select(users.c.id).where(users.c.email == "bob@example.com")
        ).scalar_one_or_none()
    if bob_id is not None:
        update_user_email(engine, bob_id, "robert@example.com")
    else:
        print(">> Bob не найден, пропускаем обновление")

    # 6) Прочитать и показать
    read_all(engine)

    # 7) Удалить Charlie
    with engine.connect() as conn:
        charlie_id = conn.execute(
            select(users.c.id).where(users.c.name == "Charlie")
        ).scalar_one_or_none()
    if charlie_id is not None:
        delete_user(engine, charlie_id)

    # 8) Прочитать и показать
    read_all(engine)

    # 9) Демонстрация исключений
    demonstrate_exceptions(engine)

    # 10) В конце удалить все данные
    drop_all_data(engine)
    read_all(engine)

    print("Готово.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Необработанное исключение:", repr(e))
        sys.exit(1)