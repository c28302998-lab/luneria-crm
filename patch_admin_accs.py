import re

with open("backend/app/api/telegram_admin.py", "r") as f:
    content = f.read()

# Patch get_accounts
old_get = """@router.get("/accounts")
def get_accounts(db: Session = Depends(get_db), current_user: User = Depends(check_owner)):
    return db.query(TelegramAccount).filter(TelegramAccount.is_deleted == False).order_by(TelegramAccount.id.asc()).all()"""

new_get = """@router.get("/accounts")
def get_accounts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role not in ["OWNER", "ADMIN"]:
        raise HTTPException(status_code=403, detail="Not allowed")
    
    query = db.query(TelegramAccount).filter(TelegramAccount.is_deleted == False)
    if current_user.role == "ADMIN":
        query = query.filter(TelegramAccount.assigned_user_id == current_user.id)
        
    # We might want to return the assigned worker name to the frontend.
    # But since frontend just sees the whole object, it's fine.
    # Let's just return all fields.
    return query.order_by(TelegramAccount.id.asc()).all()"""

content = content.replace(old_get, new_get)

# Patch AssignAccountRequest
old_assign_req = """class AssignAccountRequest(BaseModel):
    user_id: Optional[int]"""

new_assign_req = """class AssignAccountRequest(BaseModel):
    user_id: Optional[int]
    worker_id: Optional[int] = None
    worker_note: Optional[str] = None"""

content = content.replace(old_assign_req, new_assign_req)

# Patch assign_account
old_assign = """@router.patch("/accounts/{acc_id}/assign")
async def assign_account(acc_id: int, req: AssignAccountRequest, db: Session = Depends(get_db), current_user: User = Depends(check_owner)):
    try:
        acc = db.query(TelegramAccount).filter(TelegramAccount.id == acc_id).first()
        if not acc:
            raise HTTPException(status_code=404, detail="Account not found")
            
        old_user = acc.assigned_user_id
        acc.assigned_user_id = req.user_id
        db.commit()"""

new_assign = """@router.patch("/accounts/{acc_id}/assign")
async def assign_account(acc_id: int, req: AssignAccountRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        if current_user.role not in ["OWNER", "ADMIN"]:
            raise HTTPException(status_code=403, detail="Not allowed")
            
        acc = db.query(TelegramAccount).filter(TelegramAccount.id == acc_id).first()
        if not acc:
            raise HTTPException(status_code=404, detail="Account not found")
            
        if current_user.role == "ADMIN" and acc.assigned_user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not assigned to you")
            
        old_user = acc.assigned_user_id
        if current_user.role == "OWNER":
            acc.assigned_user_id = req.user_id
        
        acc.assigned_worker_id = req.worker_id
        if req.worker_note is not None:
            acc.worker_note = req.worker_note
            
        db.commit()"""

content = content.replace(old_assign, new_assign)

with open("backend/app/api/telegram_admin.py", "w") as f:
    f.write(content)
