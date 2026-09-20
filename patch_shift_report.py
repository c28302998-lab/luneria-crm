with open("backend/app/api/shift_reports.py", "r") as f:
    content = f.read()

import re

if "BackgroundTasks" not in content:
    content = content.replace("from fastapi import APIRouter, Depends, HTTPException", "from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks")

if "sync_account_to_sheets" not in content and "set_shift_date_for_accounts" not in content:
    content = content.replace("from app.db.database import get_db", "from app.db.database import get_db\nfrom app.services.google_sheets import set_shift_date_for_accounts")

if "def create_report(report_in: ShiftReportCreate" in content and "bg_tasks: BackgroundTasks" not in content:
    content = content.replace(
        "def create_report(report_in: ShiftReportCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):",
        "def create_report(report_in: ShiftReportCreate, bg_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):"
    )

old_commit = """    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    return new_report"""

new_commit = """    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    
    # Try to find telegram accounts assigned to this worker and update their shift date in sheets
    try:
        from app.models.telegram import TelegramAccount
        import datetime
        accs = db.query(TelegramAccount).filter(TelegramAccount.assigned_worker_id == current_user.id).all()
        acc_ids = [a.id for a in accs]
        if acc_ids:
            now_str = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
            bg_tasks.add_task(set_shift_date_for_accounts, acc_ids, now_str)
    except Exception as e:
        print(f"Failed to schedule shift date update: {e}")
        
    return new_report"""

content = content.replace(old_commit, new_commit)

with open("backend/app/api/shift_reports.py", "w") as f:
    f.write(content)
