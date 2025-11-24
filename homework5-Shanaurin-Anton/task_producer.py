import time
from common import get_redis

QUEUE_NAME = "task_queue"

if __name__ == "__main__":
    r = get_redis()
    i = 0
    print(f"Отправляю задачи в очередь '{QUEUE_NAME}' (Ctrl+C для выхода)")
    try:
        while True:
            task = f"task-{i}"
            # LPUSH кладёт в начало списка
            r.lpush(QUEUE_NAME, task)
            print(f"[ENQUEUE] {task}")
            i += 1
            time.sleep(1)
    except KeyboardInterrupt:
        print("Остановка продюсера")
