from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from project import api


def main():
    engine = create_engine('sqlite:///:memory:')
    Session = sessionmaker(bind=engine)
    db = Session()

    test_insert_password()
    test_get_password()
    test_get_password_nonexistent()
    test_delete_password()
    test_check_password_strength()


# Create a client for api testing
client = TestClient(api)

def test_insert_password():
    site = "example.com"
    pwd = "MySecurePassword"
    response = client.post(f"/insert_pwd?site={site}&pwd={pwd}")
    assert response.status_code == 200
    assert response.json()["site"] == site.lower()
    assert response.json()["pwd"] != pwd

def test_get_password():
    site = "example.com"
    pwd = "MySecurePassword"
    client.post(f"/insert_pwd?site={site}&pwd={pwd}")

    response = client.get(f"/get_pwd/{site}")
    assert response.status_code == 200
    assert response.json() == pwd

def test_get_password_nonexistent():
    site = "nonexistent.com"
    response = client.get(f"/get_pwd/{site}")
    assert response.status_code == 200
    assert response.json() == "Site does not exists"

def test_delete_password():
    site = "example.com"
    pwd = "MySecurePassword"
    client.post(f"/insert_pwd?site={site}&pwd={pwd}")

    response = client.get(f"/delete_site/{site}")
    assert response.status_code == 200
    assert response.json() == f"Deleted {site}"

def test_generate_key():
    response = client.get("/gen_key")
    assert response.status_code == 200
    assert len(response.json()) >= 44

def test_check_password_strength():
    strong_pwd = "S3cur3P@ssw0rd!"
    weak_pwd = "abc123"

    response_strong = client.get(f"/check_pwd_strength/{strong_pwd}")
    assert response_strong.status_code == 200
    assert response_strong.json() == "Your password is secure"

    response_weak = client.get(f"/check_pwd_strength/{weak_pwd}")
    assert response_weak.status_code == 200
    assert response_weak.json() == "Your password is not secure"


if __name__ == "__main__":
    main()