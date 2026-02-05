from unittest.mock import MagicMock

from app.db.redis import refresh_token


def test_save_refresh_token(monkeypatch):
    mock_redis = MagicMock()
    monkeypatch.setattr(refresh_token, "redis_client", mock_redis)

    user_id = "1"
    jti = "jti-123"

    refresh_token.save_refresh_token(user_id, jti)

    mock_redis.set.assert_called_once()
    set_args, set_kwargs = mock_redis.set.call_args

    assert set_kwargs["name"] == f"refresh:jti:{jti}"
    assert set_kwargs["value"] == user_id
    assert "ex" in set_kwargs

    mock_redis.sadd.assert_called_once_with(
        f"refresh:user:{user_id}",
        jti
    )


def test_exists_refresh_jti_true(monkeypatch):
    mock_redis = MagicMock()
    mock_redis.exists.return_value = 1

    monkeypatch.setattr(refresh_token, "redis_client", mock_redis)

    jti = "jti-123"
    
    result = refresh_token.exists_refresh_jti(jti)

    assert result is True
    mock_redis.exists.assert_called_once_with(f"refresh:jti:{jti}")

def test_exists_refresh_jti_false(monkeypatch):
    mock_redis = MagicMock()
    mock_redis.exists.return_value = 0

    monkeypatch.setattr(refresh_token, "redis_client", mock_redis)

    result = refresh_token.exists_refresh_jti("jti-123")

    assert result is False


def test_delete_refresh_token(monkeypatch):
    mock_redis = MagicMock()

    monkeypatch.setattr(refresh_token, "redis_client", mock_redis)

    user_id = "1"
    jti = "jti-123"

    refresh_token.delete_refresh_token(user_id, jti)

    mock_redis.delete.assert_called_once_with(f"refresh:jti:{jti}")
    mock_redis.srem.assert_called_once_with(
        f"refresh:user:{user_id}",
        jti
    )


def test_delete_all_refresh_tokens_success(monkeypatch):
    mock_pipe = MagicMock()
    mock_redis = MagicMock()

    jti_1 = "jti-1"
    jti_2 = "jti-2"

    mock_redis.smembers.return_value = {jti_1, jti_2}
    mock_redis.pipeline.return_value = mock_pipe

    monkeypatch.setattr(refresh_token, "redis_client", mock_redis)

    user_id = "1"

    refresh_token.delete_all_refresh_tokens(user_id)

    mock_redis.pipeline.assert_called_once()

    mock_pipe.delete.assert_any_call(f"refresh:jti:{jti_1}")
    mock_pipe.delete.assert_any_call(f"refresh:jti:{jti_2}")

    mock_pipe.delete.assert_any_call(f"refresh:user:{user_id}")
    mock_pipe.execute.assert_called_once()


def test_delete_all_refresh_tokens_no_jti(monkeypatch):
    mock_redis = MagicMock()
    mock_redis.smembers.return_value = set()

    monkeypatch.setattr(refresh_token, "redis_client", mock_redis)

    refresh_token.delete_all_refresh_tokens("1")

    mock_redis.pipeline.assert_not_called()
