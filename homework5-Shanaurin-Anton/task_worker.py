import time
from common import get_redis

QUEUE_NAME = "task_queue"

def process_task(task: str):
    """Простой обработчик задачи."""
    print(f"[PROCESS] Начинаю обработку: {task}")
    # имитация какой-то работы
    time.sleep(2)
    print(f"[PROCESS] Завершил: {task}")


if __name__ == "__main__":
    r = get_redis()
    print(f"Воркер запущен, слушаю очередь '{QUEUE_NAME}' (Ctrl+C для выхода)")
    try:
        while True:
            # BRPOP: блокирующее чтение с конца списка
            # Возвращает (queue_name, task) или None по таймауту
            item = r.brpop(QUEUE_NAME, timeout=5)
            if item is None:
                # за 5 секунд задач не появилось — можно что-то логировать или просто продолжать
                continue

            queue_name, task = item
            print(f"[DEQUEUE] Получена задача из {queue_name}: {task}")
            process_task(task)
    except KeyboardInterrupt:
        print("Остановка воркера")
