with open("backend/app/api/telegram_admin.py", "r") as f:
    content = f.read()

import re

# Add imports if not present
if "from app.services.google_sheets" not in content:
    content = content.replace(
        "from fastapi import APIRouter, Depends, HTTPException, Query",
        "from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks\nfrom app.services.google_sheets import sync_account_to_sheets\nimport datetime"
    )

# 1. assign_account
if "async def assign_account(acc_id: int, req: AssignAccountRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user), bg_tasks: BackgroundTasks = BackgroundTasks()):" not in content:
    content = re.sub(
        r"async def assign_account\(acc_id: int, req: AssignAccountRequest, db: Session = Depends\(get_db\), current_user: User = Depends\(get_current_user\)\):",
        r"async def assign_account(acc_id: int, req: AssignAccountRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user), bg_tasks: BackgroundTasks = BackgroundTasks()):",
        content
    )

    assign_hook = """        db.commit()
        
        # Google Sheets Sync
        w_name = acc.assigned_worker.name if acc.assigned_worker else "Свободен"
        a_name = acc.assigned_user.name if acc.assigned_user else "Без админа"
        bg_tasks.add_task(
            sync_account_to_sheets,
            account_id=acc.id,
            account_name=acc.first_name,
            phone=acc.phone,
            password=acc.two_fa_password,
            worker_name=w_name,
            admin_name=a_name,
            start_date=datetime.datetime.now().strftime("%d.%m.%Y %H:%M"),
            action="Передача аккаунта"
        )
"""
    content = content.replace("        db.commit()\n        return {\"ok\": True}", assign_hook + "        return {\"ok\": True}", 1)


# 2. edit_2fa_password_admin
if "def edit_2fa_password_admin(acc_id: int, req: EditPasswordRequest, db: Session = Depends(get_db), current_user: User = Depends(check_owner), bg_tasks: BackgroundTasks = BackgroundTasks()):" not in content:
    content = re.sub(
        r"def edit_2fa_password_admin\(acc_id: int, req: EditPasswordRequest, db: Session = Depends\(get_db\), current_user: User = Depends\(check_owner\)\):",
        r"def edit_2fa_password_admin(acc_id: int, req: EditPasswordRequest, db: Session = Depends(get_db), current_user: User = Depends(check_owner), bg_tasks: BackgroundTasks = BackgroundTasks()):",
        content
    )
    
    pwd_hook = """    db.commit()
    
    w_name = acc.assigned_worker.name if acc.assigned_worker else "Свободен"
    a_name = acc.assigned_user.name if acc.assigned_user else "Без админа"
    bg_tasks.add_task(
        sync_account_to_sheets,
        account_id=acc.id,
        account_name=acc.first_name,
        phone=acc.phone,
        password=acc.two_fa_password,
        worker_name=w_name,
        admin_name=a_name,
        start_date="",
        action="Смена пароля 2FA"
    )
"""
    content = content.replace("    db.commit()\n    return {\"ok\": True}", pwd_hook + "    return {\"ok\": True}", 1)


# 3. delete_account
if "def delete_account(acc_id: int, db: Session = Depends(get_db), current_user: User = Depends(check_owner), bg_tasks: BackgroundTasks = BackgroundTasks()):" not in content:
    content = re.sub(
        r"def delete_account\(acc_id: int, db: Session = Depends\(get_db\), current_user: User = Depends\(check_owner\)\):",
        r"def delete_account(acc_id: int, db: Session = Depends(get_db), current_user: User = Depends(check_owner), bg_tasks: BackgroundTasks = BackgroundTasks()):",
        content
    )
    
    del_hook = """    db.commit()
    
    bg_tasks.add_task(
        sync_account_to_sheets,
        account_id=acc.id,
        account_name=acc.first_name,
        phone=acc.phone,
        password="",
        worker_name="",
        admin_name="",
        start_date="",
        action="DELETE"
    )
"""
    content = content.replace("    db.commit()\n    return {\"ok\": True}", del_hook + "    return {\"ok\": True}", 1)

with open("backend/app/api/telegram_admin.py", "w") as f:
    f.write(content)

