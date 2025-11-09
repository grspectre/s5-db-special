from app.crud import create_user_with_posts, get_user_with_posts, delete_user, list_posts_by_status
from app.models import PostStatus
from app.db import SessionLocal
from sqlalchemy import text

def truncate_all():
    # порядок важен: сначала дочерние, затем родительские.
    # Но с CASCADE можно одной командой:
    with SessionLocal() as s:
        s.execute(text("TRUNCATE TABLE posts, users RESTART IDENTITY CASCADE"))
        s.commit()

truncate_all()

u = create_user_with_posts(
    email="alice@example.com",
    full_name="Alice",
    posts=[
        {"title": "Hello", "content": "World", "status": PostStatus.published},
        {"title": "Draft", "content": "Text"},
    ],
)
print("User id:", u.id)

u2 = get_user_with_posts(u.id)
print("Posts:", [(p.id, p.title, p.status) for p in u2.posts])

print("Published:", [p.title for p in list_posts_by_status(PostStatus.published)])

print("Delete user:", delete_user(u.id))
