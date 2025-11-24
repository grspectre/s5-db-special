from common import get_redis

CHANNEL_NAME = "my_channel"

if __name__ == "__main__":
    r = get_redis()
    pubsub = r.pubsub()
    pubsub.subscribe(CHANNEL_NAME)

    print(f"Подписан на канал '{CHANNEL_NAME}'. Ожидаю сообщения... (Ctrl+C для выхода)")
    try:
        for message in pubsub.listen():
            # message может содержать типы 'subscribe', 'message' и т.д.
            if message["type"] == "message":
                data = message["data"]
                print(f"[RECEIVED] {data}")
    except KeyboardInterrupt:
        print("Остановка подписчика")
