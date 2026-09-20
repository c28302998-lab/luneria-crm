with open("backend/app/api/telegram_admin.py", "r") as f:
    content = f.read()

import re
del_hook = """    # Google Sheets Sync
    try:
        bg_tasks.add_task(
            sync_account_to_sheets,
            account_id=acc.id,
            account_name=acc.first_name,
            phone=acc.phone,
            password="",
            worker_name="",
            admin_name="",
            start_date=datetime.datetime.now().strftime("%d.%m.%Y %H:%M"),
            action="Удаление аккаунта"
        )
    except Exception as e:
        print(f"Error scheduling Sheets sync: {e}")
        
    return {"status": "ok"}"""

# We want to replace inside delete_account
# Let's replace the whole function end
old_end = """    # We soft delete it
    acc.is_deleted = True
    db.commit()
    return {"status": "ok"}"""

new_end = """    # We soft delete it
    acc.is_deleted = True
    db.commit()
""" + del_hook

content = content.replace(old_end, new_end)

with open("backend/app/api/telegram_admin.py", "w") as f:
    f.write(content)
