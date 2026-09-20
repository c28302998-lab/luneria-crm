import re

with open("app/api/telegram_admin.py", "r") as f:
    content = f.read()

new_endpoint = """
@router.post("/accounts/{acc_id}/sync")
async def sync_account(acc_id: int, db: Session = Depends(get_db), current_user: User = Depends(check_owner)):
    acc = db.query(TelegramAccount).filter(TelegramAccount.id == acc_id).first()
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    
    try:
        client = await telegram_manager.get_client(acc.id, acc.session_string)
        me = await client.get_me()
        if me:
            acc.name = f"{me.first_name or ''} {me.last_name or ''}".strip() or "No Name"
            acc.username = me.username
            acc.phone = me.phone
            db.commit()
            return {"status": "success", "username": acc.username, "name": acc.name, "phone": acc.phone}
        return {"status": "error", "detail": "Could not get user info"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
"""

if "def sync_account" not in content:
    content += new_endpoint
    with open("app/api/telegram_admin.py", "w") as f:
        f.write(content)
