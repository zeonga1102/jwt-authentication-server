from app.core.config import settings
from app.db.redis.client import redis_client


def save_refresh_jti(user_id: str, jti: str) -> None:
    """
    Refresh Token jti 저장
    """
    redis_client.set(
        name=f"refresh:{user_id}:{jti}",
        value="valid",
        ex=60 * 60 * 24 * settings.REFRESH_TOKEN_EXPIRE_DAYS
    )


def exists_refresh_jti(user_id: str, jti: str) -> bool:
    """
    Refresh Token jti 존재 여부 확인
    """
    return redis_client.exists(f"refresh:{user_id}:{jti}") == 1


def delete_refresh_jti(user_id: str, jti: str) -> None:
    """
    Refresh Token jti 삭제 (rotation)
    """
    redis_client.delete(f"refresh:{user_id}:{jti}")
