from app.core.security import hash_password


def test_비밀번호_해시():
    password = "plain-password"
    hashed = hash_password(password)

    assert hashed != password
    assert hashed.startswith("$2b$")
