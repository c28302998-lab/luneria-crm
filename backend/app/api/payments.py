import uuid
import os, shutil
from fastapi import UploadFile, File
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
import os
import shutil
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.models import FileUpload, User, Payment, Worker, Expense
from app.schemas.schemas import Payment as PaymentSchema, PaymentCreate, Expense as ExpenseSchema, ExpenseCreate
from app.core.dependencies import get_current_user, RoleChecker
from app.crud.audit import log_audit

router = APIRouter()

@router.get("/", response_model=List[PaymentSchema])
def read_payments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER", "FINANCE"]))):
    return db.query(Payment).filter(Payment.is_deleted == False).order_by(Payment.date.desc()).offset(skip).limit(limit).all()

@router.post("/", response_model=PaymentSchema)
def create_payment(payment_in: PaymentCreate, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER", "FINANCE"]))):
    worker = db.query(Worker).filter(Worker.id == payment_in.worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
        
    if not worker.partner_id:
        raise HTTPException(status_code=400, detail="Worker has no partner assigned")
        
    payment = Payment(
        worker_id=worker.id,
        admin_id=worker.admin_id,
        partner_id=worker.partner_id,
        amount=payment_in.amount,
        amount_company=payment_in.amount_company,
        amount_worker=payment_in.amount_worker,
        amount_admin=payment_in.amount_admin
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    log_audit(db, current_user.id, "CREATE", "Payment", payment.id, {"amount": payment.amount})
    return payment

@router.get("/expenses", response_model=List[ExpenseSchema])
def read_expenses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER", "FINANCE"]))):
    return db.query(Expense).filter(Expense.is_deleted == False).order_by(Expense.date.desc()).offset(skip).limit(limit).all()

@router.post("/expenses", response_model=ExpenseSchema)
def create_expense(expense_in: ExpenseCreate, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER", "FINANCE"]))):
    expense = Expense(
        reason=expense_in.reason,
        amount=expense_in.amount,
        created_by=current_user.id
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    log_audit(db, current_user.id, "CREATE", "Expense", expense.id, {"amount": expense.amount, "reason": expense.reason})
    return expense

@router.get("/stats")
def get_payment_stats(db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER", "FINANCE"]))):
    payments = db.query(Payment).filter(Payment.is_deleted == False).all()
    expenses = db.query(Expense).filter(Expense.is_deleted == False).all()
    
    total_revenue = sum(p.amount for p in payments)
    company_revenue = sum(p.amount_company for p in payments)
    worker_revenue = sum(p.amount_worker for p in payments)
    admin_revenue = sum(p.amount_admin for p in payments)
    
    total_expenses = sum(e.amount for e in expenses)
    net_profit = company_revenue - total_expenses
    
    return {
        "total_revenue": total_revenue,
        "company_revenue": company_revenue,
        "worker_revenue": worker_revenue,
        "admin_revenue": admin_revenue,
        "total_expenses": total_expenses,
        "net_profit": net_profit,
        "payments_count": len(payments),
        "expenses_count": len(expenses)
    }

@router.delete("/{payment_id}")
def delete_payment(payment_id: int, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER"]))):
    payment = db.query(Payment).filter(Payment.is_deleted == False).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    payment.is_deleted = True
    import datetime
    payment.deleted_at = datetime.datetime.utcnow()
    log_audit(db, current_user.id, "DELETE", "Payment", payment_id, {})
    db.commit()
    return {"status": "success"}

@router.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["OWNER"]))):
    expense = db.query(Expense).filter(Expense.is_deleted == False).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    expense.is_deleted = True
    import datetime
    expense.deleted_at = datetime.datetime.utcnow()
    log_audit(db, current_user.id, "DELETE", "Expense", expense_id, {})
    db.commit()
    return {"status": "success"}


UPLOAD_DIR_EXPENSES = "uploads/expenses"
os.makedirs(UPLOAD_DIR_EXPENSES, exist_ok=True)

@router.post("/expenses/{expense_id}/files")
def upload_expense_file(
    expense_id: int, 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db), 
    current_user: User = Depends(RoleChecker(["OWNER", "FINANCE"]))
):
    expense = db.query(Expense).filter(Expense.id == expense_id, Expense.is_deleted == False).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
        
    file_path = os.path.join(UPLOAD_DIR_EXPENSES, f"{expense_id}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    file_url = f"/uploads/expenses/{expense_id}_{file.filename}"
    
    files_list = list(expense.files) if expense.files else []
    files_list.append(file_url)
    expense.files = files_list
    
    db.commit()
    return {"ok": True, "url": file_url}


UPLOAD_DIR_PAYMENTS = "uploads/payments"
os.makedirs(UPLOAD_DIR_PAYMENTS, exist_ok=True)

@router.post("/{payment_id}/files")
def upload_payment_file(
    payment_id: int, 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db), 
    current_user: User = Depends(RoleChecker(["OWNER", "FINANCE"]))
):
    payment = db.query(Payment).filter(Payment.id == payment_id, Payment.is_deleted == False).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
        
    file_path = os.path.join(UPLOAD_DIR_PAYMENTS, f"{payment_id}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    file_url = f"/uploads/payments/{payment_id}_{file.filename}"
    
    files_list = list(payment.files) if payment.files else []
    files_list.append(file_url)
    payment.files = files_list
    
    db.commit()
    return {"ok": True, "url": file_url}
