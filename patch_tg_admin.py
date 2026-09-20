import re

with open('backend/app/api/telegram_admin.py', 'r') as f:
    content = f.read()

# Add a helper function to get partner_name
helper = '''
def get_partner_name(db: Session, worker_user_id: int) -> Optional[str]:
    if not worker_user_id:
        return None
    from ..models.models import User, Worker, Partner
    user = db.query(User).filter(User.id == worker_user_id).first()
    if not user or not user.candidate_id:
        return None
    worker = db.query(Worker).filter(Worker.candidate_id == user.candidate_id).first()
    if not worker or not worker.partner_id:
        return None
    partner = db.query(Partner).filter(Partner.id == worker.partner_id).first()
    if partner:
        return partner.company_name
    return None
'''

if 'def get_partner_name' not in content:
    content = content.replace('router = APIRouter(prefix="/telegram/admin", tags=["Telegram Admin"])', 'router = APIRouter(prefix="/telegram/admin", tags=["Telegram Admin"])\n' + helper)


# Find all sync_account_to_sheets calls and add partner_name=get_partner_name(db, acc.assigned_worker_id)
# 1. in add_account (acc.assigned_worker_id is None, so it will be None)
content = content.replace(
    'action="Добавление аккаунта"',
    'action="Добавление аккаунта",\n                partner_name=get_partner_name(db, acc.assigned_worker_id)'
)

# 2. in assign_account
content = content.replace(
    'action="Передача аккаунта"',
    'action="Передача аккаунта",\n                partner_name=get_partner_name(db, acc.assigned_worker_id)'
)

# 3. in revoke_account
content = content.replace(
    'action="Удаление аккаунта"',
    'action="Удаление аккаунта",\n            partner_name=get_partner_name(db, acc.assigned_worker_id)'
)

# 4. in change_2fa_password
content = content.replace(
    'action="Смена пароля 2FA"',
    'action="Смена пароля 2FA",\n            partner_name=get_partner_name(db, acc.assigned_worker_id)'
)

with open('backend/app/api/telegram_admin.py', 'w') as f:
    f.write(content)
