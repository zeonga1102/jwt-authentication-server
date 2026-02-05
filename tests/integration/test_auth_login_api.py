from app.core.security import hash_password
from app.models.user import User

def test_로그인_성공(client, db, monkeypatch):
    password = "password"
    email = "test@example.com"
    user = User(
        email=email,
        password=hash_password(password),
        name="tester"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    monkeypatch.setattr(
        "app.services.auth_service.save_refresh_token",
        lambda user_id, jti: None
    )

    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password
        }
    )

    assert response.status_code == 200

    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"

    cookies = response.cookies
    assert "refresh_token" in cookies


def test_잘못된_비밀번호로_로그인_실패(client, db):
    email = "test@example.com"
    user = User(
        email=email,
        password=hash_password("correct-password"),
        name="tester"
    )
    db.add(user)
    db.commit()

    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "wrong-password"
        }
    )

    assert response.status_code == 401


def test_존재하지_않는_사용자로_로그인_실패(client):
    response = client.post(
        "/auth/login",
        json={
            "email": "nope@example.com",
            "password": "password"
        }
    )

    assert response.status_code == 401
