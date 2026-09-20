with open("backend/app/api/telegram_admin.py", "r") as f:
    content = f.read()

import re

# Add bg_tasks to verify_code
content = re.sub(
    r"async def verify_code\(req: VerifyCodeRequest, db: Session = Depends\(get_db\), current_user: User = Depends\(check_owner\)\):",
    r"async def verify_code(req: VerifyCodeRequest, db: Session = Depends(get_db), current_user: User = Depends(check_owner), bg_tasks: BackgroundTasks = BackgroundTasks()):",
    content
)

verify_hook = """        # Google Sheets Sync
        try:
            bg_tasks.add_task(
                sync_account_to_sheets,
                account_id=acc.id,
                account_name=acc.first_name,
                phone=acc.phone,
                password=acc.two_fa_password,
                worker_name="Свободен",
                admin_name="Без админа",
                start_date=datetime.datetime.now().strftime("%d.%m.%Y %H:%M"),
                action="Добавление аккаунта"
            )
        except Exception as e:
            print(f"Error scheduling Sheets sync: {e}")
            
        return {"status": "success", "account_id": acc.id}"""

content = content.replace('        return {"status": "success", "account_id": acc.id}', verify_hook, 1)

with open("backend/app/api/telegram_admin.py", "w") as f:
    f.write(content)
