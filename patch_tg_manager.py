import re

with open('backend/app/services/telegram_manager.py', 'r') as f:
    content = f.read()

old_code = """        if not await client.is_user_authorized():
            await client.disconnect()
            raise Exception("Telegram session is no longer valid or revoked")"""

new_code = """        if not await client.is_user_authorized():
            await client.disconnect()
            
            # --- AUTOMATION TRIGGER ---
            try:
                from app.db.database import SessionLocal
                from app.models.telegram import TelegramAccount
                from app.models.models import Task, User
                
                db = SessionLocal()
                acc = db.query(TelegramAccount).filter(TelegramAccount.id == account_id).first()
                if acc:
                    acc.status = "DISABLED"
                    admin_id = acc.responsible_admin_id or acc.assigned_user_id
                    if not admin_id:
                        owner = db.query(User).filter(User.role == "OWNER").first()
                        admin_id = owner.id if owner else 1
                        
                    task = Task(
                        title=f"Автоматизация: Ошибка сессии на аккаунте #{account_id}",
                        description=f"Telegram-аккаунт {acc.name or acc.phone} вылетел (сессия невалидна или revoked). Требуется перерегистрация/перепривязка.",
                        priority="HIGH",
                        assigned_user_id=admin_id,
                        creator_id=1,
                        status="NEW"
                    )
                    db.add(task)
                    db.commit()
                db.close()
            except Exception as e:
                print("Failed to trigger automation:", e)
            # --------------------------
            
            raise Exception("Telegram session is no longer valid or revoked")"""

content = content.replace(old_code, new_code)

with open('backend/app/services/telegram_manager.py', 'w') as f:
    f.write(content)
