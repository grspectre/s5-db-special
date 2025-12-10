# Отчёт по домашнему заданию №8  
**Дисциплина:** Спецглавы баз данных  
**Тема:** SQL‑инъекции, безопасность и защита  

---

## Цель работы

Научиться реализовывать базовые способы защиты баз данных:

1. Показать пример SQL‑инъекции в «сырой» SQL‑запрос и её предотвращение с помощью параметризации (psycopg2 / SQLAlchemy).
2. Настроить права доступа для пользователя в PostgreSQL (отключить возможность удаления таблиц).
3. Настроить базовую аутентификацию в MongoDB.

---

## 1. SQL‑инъекции и защита параметризацией

### 1.1. Описание стенда

- СУБД: PostgreSQL  
- Язык: Python  
- Библиотеки: `psycopg2`, `sqlalchemy`  
- Тестовая БД: `testdb`  
- Таблица:

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT,
    password TEXT
);
```

В таблицу заранее добавлены тестовые данные, например:

```sql
INSERT INTO users (username, password)
VALUES 
    ('admin', 'admin_pass'),
    ('user1', 'user1_pass');
```

---

### 1.2. Пример уязвимого кода (psycopg2, «сырой» SQL)

```python
import psycopg2

conn = psycopg2.connect(
    dbname="testdb",
    user="testuser",
    password="testpass",
    host="localhost",
    port=5432
)

cur = conn.cursor()

user_input = input("Введите имя пользователя: ")   # пример вредоносного ввода: admin' OR '1'='1

# УЯЗВИМЫЙ ВАРИАНТ: конкатенация строки запроса
query = f"SELECT * FROM users WHERE username = '{user_input}';"
print("Выполняем запрос:", query)
cur.execute(query)

rows = cur.fetchall()
for row in rows:
    print(row)

cur.close()
conn.close()
```

#### Демонстрация SQL‑инъекции

Вводим в консоли:

```text
admin' OR '1'='1
```

Фактически выполняется запрос:

```sql
SELECT * FROM users WHERE username = 'admin' OR '1'='1';
```

Условие `OR '1'='1'` всегда истинно, поэтому возвращаются все записи из таблицы `users`. Это демонстрирует уязвимость к SQL‑инъекции.

---

### 1.3. Безопасный вариант с параметризацией (psycopg2)

```python
import psycopg2

conn = psycopg2.connect(
    dbname="testdb",
    user="testuser",
    password="testpass",
    host="localhost",
    port=5432
)

cur = conn.cursor()

user_input = input("Введите имя пользователя: ")

# БЕЗОПАСНЫЙ ВАРИАНТ: используется параметризация (%s)
query = "SELECT * FROM users WHERE username = %s;"
cur.execute(query, (user_input,))  # параметры передаются отдельным аргументом

rows = cur.fetchall()
for row in rows:
    print(row)

cur.close()
conn.close()
```

#### Результат

При том же вводе:

```text
admin' OR '1'='1
```

библиотека `psycopg2` экранирует значение параметра, и оно воспринимается как обычная строка, а не как часть SQL‑кода. Запрос ищет пользователя с именем `"admin' OR '1'='1"`, которого в БД нет, и возвращает пустой результат. SQL‑инъекция не срабатывает.

---

### 1.4. Безопасный вариант через SQLAlchemy (Core)

```python
from sqlalchemy import create_engine, text

# строка подключения к PostgreSQL
engine = create_engine("postgresql+psycopg2://testuser:testpass@localhost:5432/testdb", echo=True)

user_input = input("Введите имя пользователя: ")

# БЕЗОПАСНО: text + именованные параметры
with engine.connect() as conn:
    result = conn.execute(
        text("SELECT * FROM users WHERE username = :username"),
        {"username": user_input}
    )
    for row in result:
        print(row)
```

SQLAlchemy также передаёт параметры отдельно от текста запроса, что предотвращает SQL‑инъекцию.

---

### 1.5. Вывод по разделу 1

Использование «сырой» конкатенации строк при формировании SQL‑запросов приводит к возможности SQL‑инъекций. Переход на параметризацию (psycopg2 `execute(query, params)` или SQLAlchemy `text(...)` + словарь параметров) позволяет эффективно защититься от подобного рода атак.

---

## 2. Настройка прав доступа в PostgreSQL (запрет DROP TABLE)

### 2.1. Задача

Создать в PostgreSQL пользователя с ограниченными правами, который:

- может подключаться к БД;
- может выполнять `SELECT`, `INSERT`, `UPDATE`, `DELETE` над конкретной таблицей;
- не может удалять таблицы (`DROP TABLE`).

---

### 2.2. Создание пользователя и выдача базовых прав

Работа под суперпользователем PostgreSQL (обычно роль `postgres`).

```sql
-- Создание роли (пользователя)
CREATE ROLE limited_user WITH LOGIN PASSWORD 'strong_password';

-- Разрешаем подключение к БД testdb
GRANT CONNECT ON DATABASE testdb TO limited_user;
```

Переходим в БД:

```sql
\c testdb
```

---

### 2.3. Настройка прав на схему и таблицы

Предполагаем, что таблица `users` находится в схеме `public`.

```sql
-- Разрешаем пользователю использовать схему public
GRANT USAGE ON SCHEMA public TO limited_user;

-- Разрешаем стандартные DML‑операции с таблицей users
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.users TO limited_user;
```

Важно: чтобы запретить `DROP TABLE`, необходимо, чтобы пользователь **не был владельцем** таблицы или схемы.

Проверка владельца таблицы:

```sql
SELECT table_schema, table_name, tableowner
FROM pg_tables
WHERE tablename = 'users';
```

Если владельцем является `limited_user`, меняем его:

```sql
ALTER TABLE public.users OWNER TO postgres;  -- или другая административная роль
```

Дополнительно можно убрать права на создание объектов в схеме:

```sql
REVOKE CREATE ON SCHEMA public FROM limited_user;
```

---

### 2.4. Проверка ограничения на DROP TABLE

Под пользователем `limited_user` выполняем:

```sql
DROP TABLE public.users;
```

Ожидаемый результат — ошибка:

```text
ERROR:  must be owner of relation users
```

или аналогичное сообщение о недостатке прав. Это подтверждает, что пользователь не может удалять таблицы.

---

### 2.5. Вывод по разделу 2

Путём настройки ролей и прав в PostgreSQL можно гибко ограничивать доступ пользователей. Лишив пользователя владения объектами и не выдавая ему привилегий на создание/удаление таблиц, мы предотвращаем удаление критичных структур БД, сохраняя при этом возможность работы с данными.

---

## 3. Базовая аутентификация в MongoDB

### 3.1. Задача

Включить авторизацию в MongoDB и создать пользователей:

- администратора с полными правами;
- прикладного пользователя с правами `readWrite` для конкретной БД.

---

### 3.2. Включение авторизации в конфигурации MongoDB

Открываем конфигурационный файл `mongod`:

- Linux (пример): `/etc/mongod.conf`  
- Windows (пример): `C:\Program Files\MongoDB\Server\<версия>\bin\mongod.cfg`

Добавляем (или раскомментируем) блок:

```yaml
security:
  authorization: enabled
```

Перезапускаем службу MongoDB:

- Linux (systemd):

  ```bash
  sudo systemctl restart mongod
  ```

- Windows: через `services.msc` или `net stop/start MongoDB`.

---

### 3.3. Создание администратора (пользователь с ролью root)

Первоначально, если авторизация ещё не включена или пользователей нет, подключаемся к `mongosh` без авторизации (первый запуск). Далее:

```javascript
use admin

db.createUser({
  user: "rootAdmin",
  pwd: "StrongPassword123!",
  roles: [ { role: "root", db: "admin" } ]
})
```

После создания администратора рекомендуется перезапустить MongoDB (если авторизация только что была включена). Далее для административных действий требуется аутентификация:

```bash
mongosh -u rootAdmin -p "StrongPassword123!" --authenticationDatabase admin
```

---

### 3.4. Создание прикладного пользователя для БД

Например, БД приложения: `mydb`. Под админом выполняем:

```javascript
use mydb

db.createUser({
  user: "appUser",
  pwd: "AppUserPassword123!",
  roles: [
    { role: "readWrite", db: "mydb" }
  ]
})
```

Теперь можно подключаться к MongoDB под пользователем приложения:

```text
mongodb://appUser:AppUserPassword123!@localhost:27017/mydb?authSource=mydb
```

Используя этого пользователя, можно читать и изменять данные в `mydb`, но нельзя, например, управлять пользователями или системными настройками сервера.

---

### 3.5. Проверка работы аутентификации

1. Подключение без указания пользователя и пароля:

   - Ожидаемый результат: большинство операций (кроме, возможно, некоторых команд, разрешённых анонимно, в зависимости от конфигурации) будут запрещены, появятся ошибки “not authorized”.

2. Подключение под `appUser` к БД `mydb`:

   - Доступны операции чтения/записи в `mydb`.
   - Нет доступа к административным командам и другим БД (кроме, возможно, минимального набора системных команд).

3. Подключение под `rootAdmin`:

   - Доступны все операции (управление пользователями, базами, коллекциями и т.д.).

---

## Заключение

В ходе выполнения работы были рассмотрены и реализованы три важных аспекта безопасности баз данных:

1. Продемонстрирована SQL‑инъекция при использовании «сырого» SQL и показано, как параметризация запросов в `psycopg2` и SQLAlchemy защищает приложение от инъекций.
2. В PostgreSQL настроены роли и права так, чтобы пользователь мог работать с данными, но не имел возможности удалять таблицы, что повышает защищённость структуры БД.
3. В MongoDB включен режим авторизации, создан администратор и прикладной пользователь с ограниченными правами, что обеспечивает контроль доступа к данным и административным операциям.

Полученные навыки являются основой для дальнейшей работы с безопасностью в реляционных и документно‑ориентированных СУБД.