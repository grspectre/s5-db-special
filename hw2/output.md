# Вывод программы

```
DATABASE_URL: postgresql+psycopg2://app:app@localhost:5435/appdb
>> Создаем схему (create_all if not exists)
>> Очищаем таблицу users
   OK: очищено
>> Вставка пользователей
   OK: добавлены записи: 3
>> Чтение всех пользователей
   row: {'id': 7, 'name': 'Alice', 'email': 'alice@example.com', 'age': 28}
   row: {'id': 8, 'name': 'Bob', 'email': 'bob@example.com', 'age': 35}
   row: {'id': 9, 'name': 'Charlie', 'email': 'charlie@example.com', 'age': 22}
>> Обновление email пользователя id=8 -> robert@example.com
   ROLLBACK: ошибка при обновлении: InvalidRequestError("This connection has already initialized a SQLAlchemy Transaction() object via begin() or autobegin; can't call begin() here unless rollback() or commit() is called first.")
>> Чтение всех пользователей
   row: {'id': 7, 'name': 'Alice', 'email': 'alice@example.com', 'age': 28}
   row: {'id': 8, 'name': 'Bob', 'email': 'bob@example.com', 'age': 35}
   row: {'id': 9, 'name': 'Charlie', 'email': 'charlie@example.com', 'age': 22}
>> Удаление пользователя id=9
   ROLLBACK: ошибка при удалении: InvalidRequestError("This connection has already initialized a SQLAlchemy Transaction() object via begin() or autobegin; can't call begin() here unless rollback() or commit() is called first.")
>> Чтение всех пользователей
   row: {'id': 7, 'name': 'Alice', 'email': 'alice@example.com', 'age': 28}
   row: {'id': 8, 'name': 'Bob', 'email': 'bob@example.com', 'age': 35}
   row: {'id': 9, 'name': 'Charlie', 'email': 'charlie@example.com', 'age': 22}
>> Демонстрация исключений
   Поймали другой SQLAlchemyError: InvalidRequestError("This connection has already initialized a SQLAlchemy Transaction() object via begin() or autobegin; can't call begin() here unless rollback() or commit() is called first.")
   Поймали SQLAlchemyError: InvalidRequestError("This connection has already initialized a SQLAlchemy Transaction() object via begin() or autobegin; can't call begin() here unless rollback() or commit() is called first.")
>> Очищаем таблицу users
   ROLLBACK: ошибка при очистке: InvalidRequestError("This connection has already initialized a SQLAlchemy Transaction() object via begin() or autobegin; can't call begin() here unless rollback() or commit() is called first.")
>> Чтение всех пользователей
   row: {'id': 7, 'name': 'Alice', 'email': 'alice@example.com', 'age': 28}
   row: {'id': 8, 'name': 'Bob', 'email': 'bob@example.com', 'age': 35}
   row: {'id': 9, 'name': 'Charlie', 'email': 'charlie@example.com', 'age': 22}
Готово.
(venv) PS C:\work\source\python\s5-db-special\hw2> python .\app.py
DATABASE_URL: postgresql+psycopg2://app:app@localhost:5435/appdb
>> Создаем схему (create_all if not exists)
>> Очищаем таблицу users
   OK: очищено
>> Вставка пользователей
   OK: добавлены записи: 3
>> Чтение всех пользователей
   row: {'id': 10, 'name': 'Alice', 'email': 'alice@example.com', 'age': 28}
   row: {'id': 11, 'name': 'Bob', 'email': 'bob@example.com', 'age': 35}
   row: {'id': 12, 'name': 'Charlie', 'email': 'charlie@example.com', 'age': 22}
>> Обновление email пользователя id=11 -> robert@example.com
   OK: {'id': 11, 'email': 'robert@example.com'}
>> Чтение всех пользователей
   row: {'id': 10, 'name': 'Alice', 'email': 'alice@example.com', 'age': 28}
   row: {'id': 11, 'name': 'Bob', 'email': 'robert@example.com', 'age': 35}
   row: {'id': 12, 'name': 'Charlie', 'email': 'charlie@example.com', 'age': 22}
>> Удаление пользователя id=12
   OK: удален id 12
>> Чтение всех пользователей
   row: {'id': 10, 'name': 'Alice', 'email': 'alice@example.com', 'age': 28}
   row: {'id': 11, 'name': 'Bob', 'email': 'robert@example.com', 'age': 35}
>> Демонстрация исключений
   Пытаемся вставить дубликат email...
   OK: поймали IntegrityError (уникальность): duplicate key value violates unique constraint "users_email_key"
DETAIL:  Key (email)=(dup@example.com) already exists.

   Плохой SQL для демонстрации DBAPIError...
   OK: поймали DBAPIError: syntax error at or near "INSER"
LINE 1: INSER INTO users(name, email) VALUES ('A','B')
        ^

>> Очищаем таблицу users
   OK: очищено
>> Чтение всех пользователей
   (пусто)
Готово.
```