from app.db.database import engine, Base
from app.models import models, telegram, email
Base.metadata.create_all(bind=engine)
print("Tables created successfully!")
