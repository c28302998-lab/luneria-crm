import os
import sys
sys.path.insert(0, os.path.abspath('backend'))

from app.services.google_sheets import sync_account_to_sheets

sync_account_to_sheets(
    account_id=999,
    account_name="",
    phone="",
    password="",
    worker_name="",
    admin_name="",
    start_date="",
    action="Удаление аккаунта"
)
print("Deleted test row")
