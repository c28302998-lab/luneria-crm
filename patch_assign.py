with open("backend/app/api/telegram_admin.py", "r") as f:
    content = f.read()

assign_hook = """        # Google Sheets Sync
        try:
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
        except Exception as e:
            print(f"Error scheduling Sheets sync: {e}")
            
        return {"status": "success"}"""

content = content.replace('        return {"status": "success"}', assign_hook, 1)

with open("backend/app/api/telegram_admin.py", "w") as f:
    f.write(content)
