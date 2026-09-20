with open("app/api/account_requests.py", "r") as f:
    content = f.read()

import re

# We will modify update_status
func_replacement = """@router.patch("/{req_id}/status", response_model=AccountRequestResponse)
def update_status(req_id: int, update: AccountRequestUpdate, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER", "CURATOR"]))):
    try:
        from app.models.models import Account
        import random
        import string
        
        req = db.query(AccountRequest).filter(AccountRequest.id == req_id).first()
        if not req:
            raise HTTPException(status_code=404, detail="Request not found")
            
        if update.partner_id is not None:
            req.partner_id = update.partner_id
        if update.issued_account_name is not None:
            req.issued_account_name = update.issued_account_name
            
        if update.status:
            req.status = update.status
            # Если статус меняется на ISSUED и есть кандидат, автоматически переводим его в работники
            if update.status == "ISSUED":
                worker = None
                if req.candidate_id:
                    worker = db.query(Worker).filter(Worker.candidate_id == req.candidate_id).first()
                    if not worker:
                        worker = Worker(
                            candidate_id=req.candidate_id,
                            admin_id=req.admin_id,
                            partner_id=req.partner_id
                        )
                        db.add(worker)
                        candidate = db.query(Candidate).filter(Candidate.id == req.candidate_id).first()
                        if candidate:
                            candidate.status = "WORKER"
                        db.flush() # get worker.id
                
                # При выдаче аккаунта, генерируем новый пароль и привязываем
                if req.issued_account_name:
                    acc = db.query(Account).filter(Account.login == req.issued_account_name).first()
                    if acc:
                        new_pass = "Lunery_" + "".join(random.choices(string.ascii_letters + string.digits, k=8))
                        acc.gmail_password = new_pass
                        acc.status = "IN_USE"
                        if worker:
                            acc.worker_id = worker.id

        db.commit()
        db.refresh(req)
        # Manual serialization to catch Pydantic errors
        try:
            resp = AccountRequestResponse.from_orm(req)
            return resp
        except Exception as e:
            raise Exception(f"Serialization error: {str(e)}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")"""

content = re.sub(r'@router\.patch\("/\{req_id\}/status", response_model=AccountRequestResponse\)\ndef update_status.*?raise HTTPException\(status_code=500, detail=f"Server error: \{str\(e\)\}"\)', func_replacement, content, flags=re.DOTALL)

with open("app/api/account_requests.py", "w") as f:
    f.write(content)
