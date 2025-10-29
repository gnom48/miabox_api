import time
import random
import requests
from concurrent.futures import ThreadPoolExecutor

# Параметры нагрузки
REQUESTS_PER_USER = 20   # Сколько раз каждый поток выполнит запросы
API_URL_SIGNIN = 'https://gnom48.ru/auth/api/Authentication/SignIn'
API_URL_SIGNOUT = 'https://gnom48.ru/auth/api/Authentication/SignIn'
USERNAMES = {
    'gnom48': 'pswd',
    'string': 'string',
    'no': 'no',
}  # список имен пользователей
# Количество одновременно работающих потоков-пользователей
NUM_USERS = len(USERNAMES)


def send_request(username, password):
    """Отправляет последовательные запросы signin и signout."""

    headers = {'Content-Type': 'application/json'}
    data_signin = {"login": username, "password": password}

    try:
        # Отправляем запрос на signin
        response_signin = requests.post(
            API_URL_SIGNIN, json=data_signin, headers=headers)

        if response_signin.status_code != 201:
            print(
                f"[Error {response_signin.status_code}] SignIn failed for user {username}: {response_signin.content.decode()}")
        else:
            print(
                f"User '{username}' completed signin successfully.")

    except Exception as e:
        print(f"Request error for user '{username}': {e}")


if __name__ == "__main__":
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=NUM_USERS) as executor:
        futures = []
        for _ in range(REQUESTS_PER_USER * NUM_USERS):
            user_data = random.choice(list(USERNAMES.items()))
            future = executor.submit(send_request, user_data[0], user_data[1])
            futures.append(future)

    end_time = time.time()
    total_requests = len(futures)
    elapsed_time = round(end_time - start_time, 2)
    avg_latency = round(elapsed_time / total_requests, 2)

    print("\nLoad test summary:")
    print(f"- Total Requests Sent: {total_requests}")
    print(f"- Elapsed Time: {elapsed_time:.2f} seconds")
    print(f"- Average Latency per Request: {avg_latency:.2f} seconds")
