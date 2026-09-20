from jose import jwt
from datetime import datetime, timedelta
import urllib.request
import urllib.error

SECRET_KEY = "super_secret_key_change_me_in_prod"
ALGORITHM = "HS256"
to_encode = {"sub": "1"} # OWNER user_id
expire = datetime.utcnow() + timedelta(minutes=15)
to_encode.update({"exp": expire})
encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

req = urllib.request.Request("http://localhost:8000/api/v1/attendance/pending")
req.add_header("Authorization", f"Bearer {encoded_jwt}")
try:
    with urllib.request.urlopen(req) as response:
        print("Response:", response.getcode(), response.read().decode())
except urllib.error.HTTPError as e:
    print("Error:", e.code, e.read().decode())
