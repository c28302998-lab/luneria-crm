import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.db.database import Base, engine
import app.models.models
import app.models.telegram
import app.models.email

Base.metadata.create_all(bind=engine)
print("Tables created successfully")
