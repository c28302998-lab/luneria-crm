import requests

login_res = requests.post(
    "https://lunery-x-backend.onrender.com/api/v1/auth/login",
    data={"username": "owner@luneryx", "password": "password123"},
    headers={"Content-Type": "application/x-www-form-urlencoded"}
)
token = login_res.json().get("access_token")

res = requests.post(
    "https://lunery-x-backend.onrender.com/api/v1/sources/",
    json={"title": "Test Source", "content": "Test Content"},
    headers={"Authorization": f"Bearer {token}"}
)
print("Create Source:", res.status_code, res.text)
source_id = res.json()["id"]

# Now upload file as multipart
with open("test.txt", "w") as f:
    f.write("hello world")

with open("test.txt", "rb") as f:
    res = requests.post(
        f"https://lunery-x-backend.onrender.com/api/v1/sources/{source_id}/files",
        files={"file": ("test.txt", f, "text/plain")},
        headers={"Authorization": f"Bearer {token}"}
    )
print("Upload File:", res.status_code, res.text)
