with open("backend/app/api/attendance.py", "r") as f:
    api_content = f.read()

new_endpoint = """
@router.get("/today-status")
def get_today_status(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "WORKER":
        return {"status": "NOT_WORKER"}
    
    from app.models.models import Candidate, Worker
    candidate = db.query(Candidate).filter(Candidate.email == current_user.email).first()
    if not candidate:
        return {"status": "NO_CANDIDATE"}
        
    worker = db.query(Worker).filter(Worker.candidate_id == candidate.id).first()
    if not worker:
        return {"status": "NO_WORKER"}
        
    today = date.today()
    record = db.query(Attendance).filter(Attendance.worker_id == worker.id, Attendance.date == today).first()
    
    if not record:
        return {"status": "NOT_STARTED"}
    
    return {
        "status": record.status,
        "is_present": record.is_present
    }
"""

if "/today-status" not in api_content:
    api_content = api_content.replace("@router.get(\"/pending\"", new_endpoint + "\n@router.get(\"/pending\"")
    with open("backend/app/api/attendance.py", "w") as f:
        f.write(api_content)
