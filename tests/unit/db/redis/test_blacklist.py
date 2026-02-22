from unittest.mock import MagicMock
from app.db.redis import blacklist


def test_add_blacklisted_access_token_ttl_positive(monkeypatch):
    mock_redis = MagicMock()
    monkeypatch.setattr(blacklist, "redis_client", mock_redis)

    jti = "jti-123"
    exp = 9999999999

    blacklist.add_blacklisted_access_token(jti, exp)

    mock_redis.set.assert_called_once()
    set_args, set_kwargs = mock_redis.set.call_args

    assert set_kwargs["name"] == f"blacklist:access:{jti}"
    assert set_kwargs["value"] == "1"
    assert "ex" in set_kwargs


def test_add_blacklisted_access_token_ttl_negative(monkeypatch):
    mock_redis = MagicMock()
    monkeypatch.setattr(blacklist, "redis_client", mock_redis)

    jti = "jti-123"
    exp = 1

    blacklist.add_blacklisted_access_token(jti, exp)

    mock_redis.set.assert_not_called()
