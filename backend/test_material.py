from app.db.database import SessionLocal
from app.schemas.schemas import MaterialCreate
from app.models.models import Material

material_in = MaterialCreate(title="Test", content="Test")
try:
    material = Material(**material_in.dict())
    print("Success")
except Exception as e:
    print(f"Error: {e}")
