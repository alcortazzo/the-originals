import random
from pprint import pprint

import requests


def try_to_create_task_with_no_token():
    print("Trying to create a task with no token...")
    response = requests.post("http://localhost:8000/v1/create_task")
    print(f"    Response: {response.status_code=} {response.json()=}\n")


def try_to_create_task_with_expired_token():
    print("Trying to create a task with expired token...")
    response = requests.post(
        "http://localhost:8000/v1/create_task",
        headers={"authorization": "token2", "role": "admin"},
    )
    print(f"    Response: {response.status_code=} {response.json()=}\n")


def try_to_create_task_with_valid_token_but_wrong_role():
    print("Trying to create a task with valid token, but wrong role...")
    response = requests.post(
        "http://localhost:8000/v1/create_task",
        headers={"authorization": "token3", "role": "admin"},
    )
    print(f"    Response: {response.status_code=} {response.json()=}\n")


def try_to_create_task_with_valid_token_and_role():
    random_int = random.randint(1, 10000)

    print(f"Trying to create a task ({random_int}) with valid token and role...")
    response = requests.post(
        "http://localhost:8000/v1/create_task",
        headers={"authorization": "token", "role": "admin"},
        json={
            "name": f"Task{random_int}",
            "description": f"Task {random_int} description",
            "coordinator": "462467bb-bdd2-4b33-bcd0-fcfcd9b134c2",
            "assignees": ["4a1e30bb-7589-421c-95b2-0250dcd9e24e"],
            "status": "TODO",
            "priority": 1,
        },
    )
    print(f"    Response: {response.status_code=} {response.json()=}\n")


def get_list_of_tasks():
    print("Trying to get list of tasks...")
    response = requests.get(
        "http://localhost:8000/v1/get_tasks",
        headers={"authorization": "token", "role": "admin"},
    )
    print(f"    Response: {response.status_code=}\n")
    pprint(response.json())


if __name__ == "__main__":
    try_to_create_task_with_no_token()
    try_to_create_task_with_expired_token()
    try_to_create_task_with_valid_token_but_wrong_role()
    try_to_create_task_with_valid_token_and_role()
    get_list_of_tasks()
