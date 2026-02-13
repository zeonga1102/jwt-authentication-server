from datetime import datetime

from app.db.redis.client import redis_client


def add_blacklisted_access_token(jti: str, exp: int) -> None:
    """
    Access Token을 블랙리스트에 등록
    TTL은 토큰 만료 시간까지
    """
    now = datetime.now().timestamp()
    ttl = int(exp - now)

    if ttl > 0:
        redis_client.set(
            name=f"blacklist:access:{jti}",
            value="1",
            ex=ttl
        )


def exists_blacklisted_access_token(jti: str) -> bool:
    """
    Accesso Token이 블랙리스트에 존재하는지 확인
    """
    return redis_client.exists(f"blacklist:access:{jti}") == 1
