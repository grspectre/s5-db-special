import time
from common import get_redis

CHANNEL_NAME = "my_channel"

if __name__ == "__main__":
    r = get_redis()
    i = 0
    print(f"Публикую сообщения в канал '{CHANNEL_NAME}' (Ctrl+C для выхода)")
    try:
        while True:
            msg = f"Сообщение #{i}"
            r.publish(CHANNEL_NAME, msg)
            print(f"[PUBLISH] {msg}")
            i += 1
            time.sleep(1)
    except KeyboardInterrupt:
        print("Остановка публикатора")
