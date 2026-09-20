from app.db.database import Base, engine
import app.models.models
import app.models.telegram
import app.models.email

Base.metadata.create_all(bind=engine)
