from app.models.user import User


def test_회원가입_성공(client, db):
    email = "test@example.com"
    name = "tester"

    response = client.post(
        "/user/signup",
        json={
            "email": email,
            "password": "password123",
            "name": name
        }
    )

    assert response.status_code == 200
    data = response.json()

    assert data["email"] == email
    assert data["name"] == name
    assert "password" not in data
    assert "id" in data

    user = db.query(User).filter(User.email == email).first()
    assert user is not None
    assert user.name == name
    assert user.email == email


def test_중복된_이메일로_회원가입(client):
    email = "test@example.com"
    
    # 첫 번째 가입
    client.post(
        "/user/signup",
        json={
            "email": email,
            "password": "password123",
            "name": "tester"
        }
    )

    # 중복된 이메일로 두 번째 가입
    response = client.post(
        "/user/signup",
        json={
            "email": email,
            "password": "password123",
            "name": "tester2"
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already exists"
