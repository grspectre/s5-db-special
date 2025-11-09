from typing import Sequence
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload

from .db import SessionLocal
from .models import User, Post, PostStatus

from contextlib import contextmanager

@contextmanager
def get_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

# Create: пользователь с постами
def create_user_with_posts(email: str, full_name: str | None, posts: list[dict]) -> User:
    """
    posts: список словарей с ключами: title, content, status(optional)
    """
    user = User(email=email, full_name=full_name)
    for p in posts:
        post = Post(
            title=p["title"],
            content=p["content"],
            status=p.get("status", PostStatus.draft),
        )
        user.posts.append(post)
    with get_session() as s:
        s.add(user)
        # благодаря cascade="all" посты тоже вставятся
        s.flush()  # чтобы получить id
        s.refresh(user)
        # подгрузим посты для возврата
        s.expunge(user)
    return user

# Read: получить пользователя с постами
def get_user_with_posts(user_id: int) -> User | None:
    with get_session() as s:
        stmt = (
            select(User)
            .options(selectinload(User.posts))
            .where(User.id == user_id)
        )
        res = s.execute(stmt).scalar_one_or_none()
        if res:
            s.expunge(res)
        return res

# Read: пагинация постов по статусу
def list_posts_by_status(status: PostStatus, limit: int = 50, offset: int = 0) -> Sequence[Post]:
    with get_session() as s:
        stmt = (
            select(Post)
            .where(Post.status == status)
            .order_by(Post.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        res = s.execute(stmt).scalars().all()
        for p in res:
            s.expunge(p)
        return res

# Update: частичное обновление пользователя
def update_user(user_id: int, *, email: str | None = None, full_name: str | None = None) -> bool:
    with get_session() as s:
        values = {}
        if email is not None:
            values["email"] = email
        if full_name is not None:
            values["full_name"] = full_name
        if not values:
            return False
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(**values)
        )
        res = s.execute(stmt)
        return res.rowcount > 0

# Update: обновить пост
def update_post(post_id: int, *, title: str | None = None, content: str | None = None, status: PostStatus | None = None) -> bool:
    with get_session() as s:
        values = {}
        if title is not None:
            values["title"] = title
        if content is not None:
            values["content"] = content
        if status is not None:
            values["status"] = status
        if not values:
            return False
        stmt = update(Post).where(Post.id == post_id).values(**values)
        res = s.execute(stmt)
        return res.rowcount > 0

# Delete: удалить пост
def delete_post(post_id: int) -> bool:
    with get_session() as s:
        stmt = delete(Post).where(Post.id == post_id)
        res = s.execute(stmt)
        return res.rowcount > 0

# Delete: удалить пользователя (каскад удалит все его посты)
def delete_user(user_id: int) -> bool:
    with get_session() as s:
        # Вариант 1: доверяем БД (ondelete=CASCADE + passive_deletes=True)
        stmt = delete(User).where(User.id == user_id)
        res = s.execute(stmt)
        return res.rowcount > 0
