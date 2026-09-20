import re

with open("app/schemas/schemas.py", "r") as f:
    content = f.read()

old_schema = """class ShiftReportResponse(BaseModel):
    id: int
    worker_id: int
    worker_name: Optional[str] = None
    amount: float
    files: List[str]
    status: str
    created_at: datetime
    class Config:"""

new_schema = """class ShiftReportResponse(BaseModel):
    id: int
    worker_id: int
    worker_name: Optional[str] = None
    amount: float
    files: List[str]
    status: str
    worker_amount: Optional[float] = None
    admin_amount: Optional[float] = None
    admin_name: Optional[str] = None
    created_at: datetime
    class Config:"""

content = content.replace(old_schema, new_schema)

with open("app/schemas/schemas.py", "w") as f:
    f.write(content)
