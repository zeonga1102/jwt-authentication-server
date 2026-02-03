from unittest.mock import MagicMock

from app.core.security import create_refresh_token

def test_refresh_token_재발급_성공(client, monkeypatch):
    user_id = "1"
    refresh_token, jti = create_refresh_token(user_id)

    mock_redis = MagicMock()
    mock_redis.exists.return_value = True

    monkeypatch.setattr(
        "app.services.auth_service.redis_client",
        mock_redis
    )

    client.cookies.set(
        "refresh_token",
        refresh_token
    )
    response = client.post("/auth/refresh")

    assert response.status_code == 200

    body = response.json()
    assert "access_token" in body
    assert "refresh_token=" in response.headers["set-cookie"]

def test_refresh_token_재발급_쿠키_없음_실패(client):
    response = client.post("/auth/refresh")

    assert response.status_code == 401
    assert response.json()["detail"] == "Refresh token missing"
