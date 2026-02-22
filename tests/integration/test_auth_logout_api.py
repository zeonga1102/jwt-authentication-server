def test_logout_성공(client, monkeypatch):
    monkeypatch.setattr(
        "app.api.auth.logout_user",
        lambda access, refresh: None
    )

    client.cookies.set("refresh_token", "valid.refresh")
    response = client.post(
        "/auth/logout",
        headers={"Authorization": "Bearer valid.access"}
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Logged out successfully"

    set_cookie = response.headers["set-cookie"]

    assert "refresh_token=" in set_cookie
    assert "Max-Age=0" in set_cookie or "expires=" in set_cookie.lower()


def test_logout_access_token_없어도_성공(client, monkeypatch):
    monkeypatch.setattr(
        "app.api.auth.logout_user",
        lambda access, refresh: None
    )

    client.cookies.set("refresh_token", "valid.refresh")

    response = client.post("/auth/logout")

    assert response.status_code == 200
    assert response.json()["message"] == "Logged out successfully"


def test_logout_refresh_없음_실패(client):
    response = client.post("/auth/logout")

    assert response.status_code == 401
    assert response.json()["detail"] == "Refresh token missing"
