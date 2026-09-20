import re

# 1. Update models.py
with open("backend/app/models/models.py", "r") as f:
    models_content = f.read()

models_content = models_content.replace(
    "advances = Column(String, nullable=True)",
    "advances = Column(String, nullable=True)\n    schedules = Column(String, nullable=True)"
)

with open("backend/app/models/models.py", "w") as f:
    f.write(models_content)

# 2. Update schemas.py
with open("backend/app/schemas/schemas.py", "r") as f:
    schemas_content = f.read()

schemas_content = schemas_content.replace(
    "advances: Optional[str] = None",
    "advances: Optional[str] = None\n    schedules: Optional[str] = None"
)

with open("backend/app/schemas/schemas.py", "w") as f:
    f.write(schemas_content)

# 3. Update google_sheets.py
with open("backend/app/services/google_sheets.py", "r") as f:
    sheets_content = f.read()

sheets_content = sheets_content.replace(
    "rating: float, last_contact_date: str, advances: str):",
    "rating: float, last_contact_date: str, advances: str, schedules: str):"
)

sheets_content = sheets_content.replace(
    'headers = ["ID", "Агентство", "Контакт", "Страна", "Места", "Оплата", "Опыт", "Регистрация", "Ответ", "Рейтинг", "Последний контакт", "Авансы"]',
    'headers = ["ID", "Агентство", "Контакт", "Страна", "Места", "Оплата", "Опыт", "Регистрация", "Ответ", "Рейтинг", "Последний контакт", "Авансы", "Графики"]'
)

sheets_content = sheets_content.replace(
    'advances or ""\n        ]',
    'advances or "",\n            schedules or ""\n        ]'
)

sheets_content = sheets_content.replace(
    'worksheet.update(f"A{row_idx}:L{row_idx}", [row_data])',
    'worksheet.update(f"A{row_idx}:M{row_idx}", [row_data])'
)

with open("backend/app/services/google_sheets.py", "w") as f:
    f.write(sheets_content)

# 4. Update api/partners.py
with open("backend/app/api/partners.py", "r") as f:
    api_content = f.read()

api_content = api_content.replace(
    "partner.rating, partner.last_contact_date, partner.advances",
    "partner.rating, partner.last_contact_date, partner.advances, partner.schedules"
)

with open("backend/app/api/partners.py", "w") as f:
    f.write(api_content)

# 5. Update main.py for migration
with open("backend/app/main.py", "r") as f:
    main_content = f.read()

main_content = main_content.replace(
    "conn.execute(text(\"ALTER TABLE partners ADD COLUMN IF NOT EXISTS advances VARCHAR;\"))",
    "conn.execute(text(\"ALTER TABLE partners ADD COLUMN IF NOT EXISTS advances VARCHAR;\"))\n            conn.execute(text(\"ALTER TABLE partners ADD COLUMN IF NOT EXISTS schedules VARCHAR;\"))"
)

with open("backend/app/main.py", "w") as f:
    f.write(main_content)

