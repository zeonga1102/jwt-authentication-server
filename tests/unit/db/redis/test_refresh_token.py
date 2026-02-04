from unittest.mock import MagicMock

from app.db.redis import refresh_token


def test_save_refresh_jti(monkeypatch):
    mock_redis = MagicMock()

    monkeypatch.setattr(
        refresh_token,
        "redis_client",
        mock_redis
    )

    user_id = "1"
    jti = "jti-123"

    refresh_token.save_refresh_jti(user_id, jti)

    mock_redis.set.assert_called_once()
    args, kwargs = mock_redis.set.call_args

    assert kwargs["name"] == f"refresh:{user_id}:{jti}"
    assert kwargs["value"] == "valid"
    assert "ex" in kwargs


def test_exists_refresh_jti_true(monkeypatch):
    mock_redis = MagicMock()
    mock_redis.exists.return_value = 1

    monkeypatch.setattr(
        refresh_token,
        "redis_client",
        mock_redis
    )

    user_id = "1"
    jti = "jti-123"
    
    result = refresh_token.exists_refresh_jti(user_id, jti)

    assert result is True
    mock_redis.exists.assert_called_once_with(f"refresh:{user_id}:{jti}")

def test_exists_refresh_jti_false(monkeypatch):
    mock_redis = MagicMock()
    mock_redis.exists.return_value = 0

    monkeypatch.setattr(
        refresh_token,
        "redis_client",
        mock_redis
    )

    result = refresh_token.exists_refresh_jti("1", "jti-123")

    assert result is False


def test_delete_refresh_jti(monkeypatch):
    mock_redis = MagicMock()

    monkeypatch.setattr(
        refresh_token,
        "redis_client",
        mock_redis
    )

    user_id = "1"
    jti = "jti-123"

    refresh_token.delete_refresh_jti(user_id, jti)

    mock_redis.delete.assert_called_once_with(f"refresh:{user_id}:{jti}")
