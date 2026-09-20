import requests
from jose import jwt
from datetime import datetime, timedelta

from sqlalchemy import create_engine, text
engine = create_engine("postgresql://neondb_owner:npg_omMf6bdDV7sY@ep-flat-lab-b17zvgp3-pooler.c-5.eu-central-1.aws.neon.tech/neondb?sslmode=require")
with engine.connect() as conn:
    res = conn.execute(text("SELECT id FROM users WHERE email='owner@luneryx';"))
    user_id = res.scalar()

SECRET_KEY = "super_secret_key_change_me_in_prod" 
to_encode = {"exp": datetime.utcnow() + timedelta(minutes=60), "sub": str(user_id)}
token = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

res = requests.post(
    "https://lunery-x-backend.onrender.com/api/v1/sources/",
    json={"title": "Test Source", "content": "Test Content"},
    headers={"Authorization": f"Bearer {token}"}
)
print("Create Source:", res.status_code, res.text)
if res.status_code == 200:
    source_id = res.json()["id"]
    with open("test.txt", "w") as f:
        f.write("hello world")
    
    with open("test.txt", "rb") as f:
        res = requests.post(
            f"https://lunery-x-backend.onrender.com/api/v1/sources/{source_id}/files",
            files={"file": ("test.txt", f, "text/plain")},
            headers={"Authorization": f"Bearer {token}"}
        )
    print("Upload File:", res.status_code, res.text)
