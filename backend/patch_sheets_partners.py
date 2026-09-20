with open("backend/app/services/google_sheets.py", "r") as f:
    content = f.read()

sync_function = """
def sync_partner_to_sheets(partner_id: int, company_name: str, contact: str, country: str, seats: int, payment_terms: str, experience: str, registration_time: str, response_time: str, rating: float, last_contact_date: str):
    try:
        client = get_gspread_client()
        if not client: return
        sheet = client.open_by_key(DEFAULT_SHEET_ID)
        
        try:
            worksheet = sheet.worksheet("Партнеры")
        except gspread.exceptions.WorksheetNotFound:
            worksheet = sheet.add_worksheet(title="Партнеры", rows="1000", cols="20")
            headers = ["ID", "Агентство", "Контакт", "Страна", "Места", "Оплата", "Опыт", "Регистрация", "Ответ", "Рейтинг", "Последний контакт"]
            worksheet.append_row(headers)
            
        records = worksheet.get_all_records()
        row_idx = None
        for i, record in enumerate(records):
            if str(record.get("ID", "")) == str(partner_id):
                row_idx = i + 2
                break
                
        row_data = [
            str(partner_id),
            company_name or "",
            contact or "",
            country or "",
            str(seats) if seats is not None else "0",
            payment_terms or "",
            experience or "",
            registration_time or "",
            response_time or "",
            str(rating) if rating is not None else "",
            last_contact_date or ""
        ]
        
        if row_idx:
            worksheet.update(f"A{row_idx}:K{row_idx}", [row_data])
        else:
            worksheet.append_row(row_data)
            
    except Exception as e:
        print("Error syncing partner to sheets:", e)
        traceback.print_exc()
"""

if "def sync_partner_to_sheets" not in content:
    content += sync_function
    with open("backend/app/services/google_sheets.py", "w") as f:
        f.write(content)
