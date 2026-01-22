from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    로그인 시 입력한 비밀번호와 DB에 저장된 비밀번호 해시 비교
    """
    return pwd_context.verify(plain_password, hashed_password)
