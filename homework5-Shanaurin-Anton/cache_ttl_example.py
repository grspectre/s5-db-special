import time
from functools import wraps

from common import get_redis

r = get_redis()

def redis_cache_ttl(ttl_seconds: int):
    """Декоратор: кеширование результатов функции в Redis с TTL."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Формируем ключ по имени функции и аргументам (упрощённо)
            key = f"cache:{func.__name__}:{args}:{tuple(sorted(kwargs.items()))}"

            # 1. Пытаемся прочитать из кеша
            cached = r.get(key)
            if cached is not None:
                print(f"[CACHE HIT] key={key}")
                return cached  # здесь строка, если нужно — сериализация/десериализация (json, pickle и т.п.)

            print(f"[CACHE MISS] key={key}, вычисляем...")
            # 2. Вычисляем значение
            result = func(*args, **kwargs)

            # 3. Кладём в Redis с TTL
            # если result не строка, нужно привести к строке или сериализовать
            r.setex(key, ttl_seconds, str(result))

            return str(result)
        return wrapper
    return decorator


@redis_cache_ttl(ttl_seconds=5)
def slow_function(x: int) -> str:
    """Имитация тяжёлой функции."""
    time.sleep(2)
    return f"Результат для x={x}"


if __name__ == "__main__":
    print(slow_function(10))  # первая попытка — MISS (2 секунды)
    print(slow_function(10))  # вторая — HIT (почти мгновенно)
    time.sleep(6)             # ждём, пока TTL истечёт
    print(slow_function(10))  # снова MISS
