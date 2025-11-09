# Вывод консоли и программы

```bash
(venv) PS C:\work\source\python\s5-db-special\homework3-Shanaurin-Anton> alembic revision --autogenerate -m "init users and posts"
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.autogenerate.compare] Detected added table 'users'
INFO  [alembic.autogenerate.compare] Detected added index 'ix_users_email' on '('email',)'
INFO  [alembic.autogenerate.compare] Detected added table 'posts'
INFO  [alembic.autogenerate.compare] Detected added index 'ix_posts_user_id' on '('user_id',)'
Generating C:\work\source\python\s5-db-special\homework3-Shanaurin-Anton\alembic\versions\8795c7145133_init_users_and_posts.py ...  done

(venv) PS C:\work\source\python\s5-db-special\homework3-Shanaurin-Anton> alembic upgrade head
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 8795c7145133, init users and posts

(venv) PS C:\work\source\python\s5-db-special\homework3-Shanaurin-Anton> alembic revision --autogenerate -m "add post.status"
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.ddl.postgresql] Detected sequence named 'users_id_seq' as owned by integer column 'users(id)', assuming SERIAL and omitting
INFO  [alembic.ddl.postgresql] Detected sequence named 'posts_id_seq' as owned by integer column 'posts(id)', assuming SERIAL and omitting
INFO  [alembic.autogenerate.compare] Detected added column 'posts.status'
Generating C:\work\source\python\s5-db-special\homework3-Shanaurin-Anton\alembic\versions\d52f7f946dca_add_post_status.py ...  done

(venv) PS C:\work\source\python\s5-db-special\homework3-Shanaurin-Anton> alembic upgrade head
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade 8795c7145133 -> d52f7f946dca, add post.status
```

## Вывод тестового скрипта

```bash
python .\app.py
2025-11-09 21:52:45,256 INFO sqlalchemy.engine.Engine select pg_catalog.version()
2025-11-09 21:52:45,256 INFO sqlalchemy.engine.Engine [raw sql] {}
2025-11-09 21:52:45,259 INFO sqlalchemy.engine.Engine select current_schema()
2025-11-09 21:52:45,259 INFO sqlalchemy.engine.Engine [raw sql] {}
2025-11-09 21:52:45,262 INFO sqlalchemy.engine.Engine show standard_conforming_strings
2025-11-09 21:52:45,262 INFO sqlalchemy.engine.Engine [raw sql] {}
2025-11-09 21:52:45,265 INFO sqlalchemy.engine.Engine BEGIN (implicit)
2025-11-09 21:52:45,266 INFO sqlalchemy.engine.Engine TRUNCATE TABLE posts, users RESTART IDENTITY CASCADE
2025-11-09 21:52:45,266 INFO sqlalchemy.engine.Engine [generated in 0.00031s] {}
2025-11-09 21:52:45,315 INFO sqlalchemy.engine.Engine COMMIT
2025-11-09 21:52:45,329 INFO sqlalchemy.engine.Engine BEGIN (implicit)
2025-11-09 21:52:45,332 INFO sqlalchemy.engine.Engine INSERT INTO users (email, full_name) VALUES (%(email)s, %(full_name)s) RETURNING users.id, users.created_at
2025-11-09 21:52:45,332 INFO sqlalchemy.engine.Engine [generated in 0.00039s] {'email': 'alice@example.com', 'full_name': 'Alice'}
2025-11-09 21:52:45,340 INFO sqlalchemy.engine.Engine INSERT INTO posts (user_id, title, content, status) SELECT p0::INTEGER, p1::VARCHAR, p2::TEXT, p3::post_status FROM (VALUES (%(user_id__0)s, %(title__0)s, %(content__0)s, %(status__0)s, 0), (%(user_id__1)s, %(title__1)s, %(content__1)s, %(status__1)s, 1)) AS imp_sen(p0, p1, p2, p3, sen_counter) ORDER BY sen_counter RETURNING posts.id, posts.created_at, posts.id AS id__1
2025-11-09 21:52:45,340 INFO sqlalchemy.engine.Engine [generated in 0.00013s (insertmanyvalues) 1/1 (ordered)] {'content__0': 'World', 'user_id__0': 1, 'status__0': 'published', 'title__0': 'Hello', 'content__1': 'Text', 'user_id__1': 1, 'status__1': 'draft', 'title__1': 'Draft'}
2025-11-09 21:52:45,351 INFO sqlalchemy.engine.Engine SELECT users.id, users.email, users.full_name, users.created_at
FROM users
WHERE users.id = %(pk_1)s
2025-11-09 21:52:45,351 INFO sqlalchemy.engine.Engine [generated in 0.00036s] {'pk_1': 1}
2025-11-09 21:52:45,354 INFO sqlalchemy.engine.Engine COMMIT
User id: 1
2025-11-09 21:52:45,358 INFO sqlalchemy.engine.Engine BEGIN (implicit)
2025-11-09 21:52:45,361 INFO sqlalchemy.engine.Engine SELECT users.id, users.email, users.full_name, users.created_at
FROM users
WHERE users.id = %(id_1)s
2025-11-09 21:52:45,361 INFO sqlalchemy.engine.Engine [generated in 0.00040s] {'id_1': 1}
2025-11-09 21:52:45,367 INFO sqlalchemy.engine.Engine SELECT posts.user_id AS posts_user_id, posts.id AS posts_id, posts.title AS posts_title, posts.content AS posts_content, posts.created_at AS posts_created_at, posts.status AS posts_status
FROM posts
WHERE posts.user_id IN (%(primary_keys_1)s)
2025-11-09 21:52:45,368 INFO sqlalchemy.engine.Engine [generated in 0.00047s] {'primary_keys_1': 1}
2025-11-09 21:52:45,370 INFO sqlalchemy.engine.Engine COMMIT
Posts: [(1, 'Hello', <PostStatus.published: 'published'>), (2, 'Draft', <PostStatus.draft: 'draft'>)]
2025-11-09 21:52:45,372 INFO sqlalchemy.engine.Engine BEGIN (implicit)
2025-11-09 21:52:45,374 INFO sqlalchemy.engine.Engine SELECT posts.id, posts.user_id, posts.title, posts.content, posts.created_at, posts.status
FROM posts
WHERE posts.status = %(status_1)s ORDER BY posts.created_at DESC
 LIMIT %(param_1)s OFFSET %(param_2)s
2025-11-09 21:52:45,374 INFO sqlalchemy.engine.Engine [generated in 0.00033s] {'status_1': 'published', 'param_1': 50, 'param_2': 0}
2025-11-09 21:52:45,385 INFO sqlalchemy.engine.Engine COMMIT
Published: ['Hello']
2025-11-09 21:52:45,387 INFO sqlalchemy.engine.Engine BEGIN (implicit)
2025-11-09 21:52:45,388 INFO sqlalchemy.engine.Engine DELETE FROM users WHERE users.id = %(id_1)s
2025-11-09 21:52:45,389 INFO sqlalchemy.engine.Engine [generated in 0.00030s] {'id_1': 1}
2025-11-09 21:52:45,392 INFO sqlalchemy.engine.Engine COMMIT
Delete user: True
```
