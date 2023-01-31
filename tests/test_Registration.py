import pytest
from models import User

def test_home(client):
    response = client.get("/")
    assert b"<title>Home</title>" in response.data

def test_registration(client, app):
    response = client.post("/register", data={"email": "test@test.com", "password": "testpassword"})

    with app.app_context():
        assert User.query.count() == 1
        assert User.query.first().email == "test@test.com"