def test_회원가입_성공(client):
    response = client.post(
        "/user/signup",
        json={
            "email": "test@example.com",
            "password": "password123",
            "name": "tester"
        }
    )

    assert response.status_code == 200
    data = response.json()

    assert data["email"] == "test@example.com"
    assert data["name"] == "tester"
    assert "id" in data


def test_중복된_이메일로_회원가입(client):
    # 첫 번째 가입
    client.post(
        "/user/signup",
        json={
            "email": "test@example.com",
            "password": "password123",
            "name": "tester"
        }
    )

    # 중복된 이메일로 두 번째 가입
    response = client.post(
        "/user/signup",
        json={
            "email": "test@example.com",
            "password": "password123",
            "name": "tester2"
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already exists"
