import os
import sys

# Add backend dir to PYTHONPATH
sys.path.insert(0, os.path.abspath('backend'))

from app.services.google_sheets import sync_account_to_sheets

sync_account_to_sheets(
    account_id=999,
    account_name="Test Account",
    phone="+123456789",
    password="TestPassword",
    worker_name="Test Worker",
    admin_name="Test Admin",
    start_date="10.09.2026 13:55",
    action="Тестовая проверка"
)
print("Finished sync!")
