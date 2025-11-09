from datetime import datetime, timedelta
import random
import string
from pymongo import MongoClient

def random_string(n=8):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(n))

def random_email():
    domains = ["example.com", "test.org", "mail.net"]
    return f"{random_string(6).lower()}@{random.choice(domains)}"

def random_date(start_year=2020, end_year=2025):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days),
                             seconds=random.randint(0, 86400))

def generate_documents(n=100):
    docs = []
    for i in range(n):
        doc = {
            "user_id": i + 1,                              # число (int)
            "name": random_string(10),                     # строка
            "email": random_email(),                       # строка
            "age": random.randint(18, 70),                 # число (int)
            "balance": round(random.uniform(0, 10000), 2), # число (float)
            "is_active": random.choice([True, False]),     # булево
            "created_at": random_date(),                   # дата/время
            "tags": random.sample(["new", "vip", "trial", "beta", "staff"], 
                                  k=random.randint(1, 3)), # массив строк
            "address": {                                   # вложенный документ
                "city": random.choice(["Moscow", "SPB", "Kazan", "Novosibirsk"]),
                "street": f"{random.randint(1, 300)} {random.choice(['Lenina', 'Mira', 'Gagarina', 'Pushkina'])}",
                "zip": "".join(random.choice(string.digits) for _ in range(6))
            },
        }
        docs.append(doc)
    return docs

def main():
    # Если у вас включена аутентификация, используйте строку вида:
    # client = MongoClient("mongodb://root:example@localhost:27017")
    client = MongoClient("mongodb://root:example@localhost:27017")

    db = client["test_db"]
    collection = db["users_generated"]

    # Очистим коллекцию перед вставкой (необязательно)
    collection.delete_many({})

    docs = generate_documents(100)
    result = collection.insert_many(docs)

    print(f"Inserted {len(result.inserted_ids)} documents into {db.name}.{collection.name}")

    # Пример простого чтения и вывода 3 документов
    for doc in collection.find({}, {"_id": 0}).limit(3):
        print(doc)

if __name__ == "__main__":
    main()