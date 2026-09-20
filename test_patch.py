from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
# Actually, I don't have auth. I can't test it directly unless I mock auth.
