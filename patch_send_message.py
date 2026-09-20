import re

with open('backend/app/api/telegram_proxy.py', 'r') as f:
    content = f.read()

old_code = """        # Audit Log
        log = TelegramAuditLog(
            user_id=user.id,
            account_id=acc.id,
            action="SEND_MESSAGE",
            details=f"Sent message to {req.chat_id}"
        )
        db.add(log)
        
        # Stats
        acc.total_messages_sent = (acc.total_messages_sent or 0) + 1
        db.commit()"""

new_code = """        # Audit Log
        log = TelegramAuditLog(
            user_id=user.id,
            account_id=acc.id,
            action="SEND_MESSAGE",
            details=f"Sent message to {req.chat_id}"
        )
        db.add(log)
        
        # Stats
        acc.total_messages_sent = (acc.total_messages_sent or 0) + 1
        
        # Simple rule trigger example: if sent > 50 messages today, trigger task
        # Note: We use total_messages_sent blindly here just for demonstration of automation.
        # Ideally, we track per-day. If it reaches exactly 500, trigger warning.
        if acc.total_messages_sent == 500:
            from app.models.models import Task, User
            admin_id = acc.responsible_admin_id or acc.assigned_user_id
            if not admin_id:
                owner = db.query(User).filter(User.role == "OWNER").first()
                admin_id = owner.id if owner else 1
            task = Task(
                title=f"Внимание: аккаунт {acc.name} достиг 500 сообщений",
                description=f"Telegram-аккаунт отправляет слишком много сообщений.",
                priority="MEDIUM",
                assigned_user_id=admin_id,
                creator_id=1,
                status="NEW"
            )
            db.add(task)
            
        db.commit()"""

content = content.replace(old_code, new_code)

old_exception = """    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))"""

new_exception = """    except Exception as e:
        # Automations: Detect FloodWait
        if "FloodWaitError" in type(e).__name__ or "flood wait" in str(e).lower():
            from app.models.models import Task, User
            admin_id = acc.responsible_admin_id or acc.assigned_user_id
            if not admin_id:
                owner = db.query(User).filter(User.role == "OWNER").first()
                admin_id = owner.id if owner else 1
            task = Task(
                title=f"Автоматизация: FloodWait на аккаунте {acc.name}",
                description=f"Аккаунт получил спам-блок или FloodWait. Ошибка: {str(e)}",
                priority="HIGH",
                assigned_user_id=admin_id,
                creator_id=1,
                status="NEW"
            )
            db.add(task)
            db.commit()
            
        raise HTTPException(status_code=400, detail=str(e))"""

content = content.replace(old_exception, new_exception)

with open('backend/app/api/telegram_proxy.py', 'w') as f:
    f.write(content)
