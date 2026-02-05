from app.core.config import settings
from app.db.redis.client import redis_client


def save_refresh_token(user_id: str, jti: str) -> None:
    """
    Refresh Token 저장
    """
    redis_client.set(
        name=f"refresh:jti:{jti}",
        value=user_id,
        ex=60 * 60 * 24 * settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    redis_client.sadd(f"refresh:user:{user_id}", jti)


def exists_refresh_jti(jti: str) -> bool:
    """
    Refresh Token jti 존재 여부 확인
    """
    return redis_client.exists(f"refresh:jti:{jti}") == 1


def delete_refresh_token(user_id: str, jti: str) -> None:
    """
    Refresh Token 삭제 (rotation)
    """
    redis_client.delete(f"refresh:jti:{jti}")
    redis_client.srem(f"refresh:user:{user_id}", jti)


def delete_all_refresh_tokens(user_id: str) -> None:
    """
    재사용 공격 감지 시: 해당 유저의 모든 refresh token 무효화
    """
    key = f"refresh:user:{user_id}"
    jtis = redis_client.smembers(key)

    if not jtis:
        return

    pipe = redis_client.pipeline()
    for jti in jtis:
        pipe.delete(f"refresh:jti:{jti}")
    pipe.delete(key)
    pipe.execute()
