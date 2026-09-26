import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app, init_db


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["DATABASE"] = "test_tasks.db"

    if os.path.exists("test_tasks.db"):
        os.remove("test_tasks.db")

    with app.test_client() as client:

        with app.app_context():
            init_db()

        yield client

    if os.path.exists("test_tasks.db"):
        os.remove("test_tasks.db")


def test_home(client):
    response = client.get("/")

    assert response.status_code == 200


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json["status"] == "ok"


def test_add_task(client):
    response = client.post(
        "/add",
        data={"title": "Test Task"},
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Test Task" in response.data


def test_complete_task(client):
    client.post(
        "/add",
        data={"title": "Complete Me"}
    )

    response = client.get("/complete/1")

    assert response.status_code == 302


def test_delete_task(client):
    client.post(
        "/add",
        data={"title": "Delete Me"}
    )

    response = client.get("/delete/1")

    assert response.status_code == 302


def test_edit_task(client):
    client.post(
        "/add",
        data={"title": "Old Task"}
    )

    response = client.post(
        "/edit/1",
        data={"title": "Updated Task"}
    )

    assert response.status_code == 302