import requests

login_res = requests.post(
    "https://lunery-x-backend.onrender.com/api/v1/auth/login",
    data={"username": "owner@lunery.local", "password": "password123"},
    headers={"Content-Type": "application/x-www-form-urlencoded"}
)
print("Login:", login_res.status_code, login_res.text)
if login_res.status_code == 200:
    token = login_res.json().get("access_token")
    res = requests.post(
        "https://lunery-x-backend.onrender.com/api/v1/sources/",
        json={"title": "Test Source", "content": "Test Content"},
        headers={"Authorization": f"Bearer {token}"}
    )
    print("Create Source:", res.status_code, res.text)
