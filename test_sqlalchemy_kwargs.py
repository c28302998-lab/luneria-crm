from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class MyModel(Base):
    __tablename__ = 'my_table'
    id = Column(Integer, primary_key=True)
    title = Column(String)

try:
    m = MyModel(title="test", notes=None)
    print("Success")
except Exception as e:
    print("Error:", type(e), e)
