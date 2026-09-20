import sqlite3

# 1. Update DB schema
conn = sqlite3.connect('backend/sql_app.db')
c = conn.cursor()
try:
    c.execute("ALTER TABLE attendance ADD COLUMN status VARCHAR DEFAULT 'APPROVED'")
    conn.commit()
    print("Column added.")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("Column already exists.")
    else:
        raise
conn.close()

# 2. Update models.py
with open("backend/app/models/models.py", "r") as f:
    models_content = f.read()

if "status = Column(String, default=\"APPROVED\")" not in models_content:
    models_content = models_content.replace(
        "is_present = Column(Boolean, default=False)",
        "is_present = Column(Boolean, default=False)\n    status = Column(String, default=\"APPROVED\")"
    )
    with open("backend/app/models/models.py", "w") as f:
        f.write(models_content)

# 3. Update schemas.py
with open("backend/app/schemas/schemas.py", "r") as f:
    schemas_content = f.read()

if "status: Optional[str] = \"APPROVED\"" not in schemas_content:
    schemas_content = schemas_content.replace(
        "is_present: bool",
        "is_present: bool\n    status: Optional[str] = \"APPROVED\""
    )
    with open("backend/app/schemas/schemas.py", "w") as f:
        f.write(schemas_content)

# 4. Update attendance.py
with open("backend/app/api/attendance.py", "r") as f:
    api_content = f.read()

if "start-shift" not in api_content:
    imports = "from app.models.models import Candidate\nfrom pydantic import BaseModel\n\nclass VerifyShiftRequest(BaseModel):\n    is_present: bool\n"
    api_content = api_content.replace("router = APIRouter()", imports + "router = APIRouter()")
    
    new_endpoints = """

@router.get("/pending", response_model=List[AttendanceSchema])
def get_pending_attendance(db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["ADMIN", "OWNER"]))):
    if current_user.role == "ADMIN":
        workers = db.query(Worker).filter(Worker.admin_id == current_user.id).all()
        worker_ids = [w.id for w in workers]
        return db.query(Attendance).filter(Attendance.status == "PENDING", Attendance.worker_id.in_(worker_ids)).all()
    else:
        return db.query(Attendance).filter(Attendance.status == "PENDING").all()

@router.post("/start-shift", response_model=AttendanceSchema)
def start_shift(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "WORKER":
        raise HTTPException(status_code=403, detail="Only workers can start shift")
        
    candidate = db.query(Candidate).filter(Candidate.email == current_user.email).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found for your email")
        
    worker = db.query(Worker).filter(Worker.candidate_id == candidate.id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
        
    today = date.today()
    record = db.query(Attendance).filter(Attendance.worker_id == worker.id, Attendance.date == today).first()
    if record:
        raise HTTPException(status_code=400, detail="Shift already started or marked today")
        
    record = Attendance(
        worker_id=worker.id,
        date=today,
        is_present=False,
        status="PENDING",
        updated_by=current_user.id
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

@router.put("/{attendance_id}/verify", response_model=AttendanceSchema)
def verify_shift(attendance_id: int, req: VerifyShiftRequest, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["ADMIN", "OWNER"]))):
    record = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
        
    worker = db.query(Worker).filter(Worker.id == record.worker_id).first()
    if current_user.role == "ADMIN" and worker.admin_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your worker")
        
    record.is_present = req.is_present
    record.status = "APPROVED" if req.is_present else "REJECTED"
    record.updated_by = current_user.id
    db.commit()
    db.refresh(record)
    return record
"""
    api_content += new_endpoints
    with open("backend/app/api/attendance.py", "w") as f:
        f.write(api_content)

print("Backend attendance patched successfully.")
