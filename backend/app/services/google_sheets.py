import json
import os
import gspread
from google.oauth2.service_account import Credentials
from typing import Optional, Dict
import traceback

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

import base64
import json
try:
    DEFAULT_CREDS = json.loads(base64.b64decode("eyJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsICJwcm9qZWN0X2lkIjogImx1bmVyeS1jcm0tYm90IiwgInByaXZhdGVfa2V5X2lkIjogImU3NjA1ZmM5OGJlZmQwYjY3ZDk5NmY2OWU5YzhhODUwNWMxZjAyNjIiLCAicHJpdmF0ZV9rZXkiOiAiLS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tXG5NSUlFdmdJQkFEQU5CZ2txaGtpRzl3MEJBUUVGQUFTQ0JLZ3dnZ1NrQWdFQUFvSUJBUUM2bFZtZGhndGk1VTgyXG5UdFVBUEZEZjdVRmJvK2pyT3puNGtwMzQvdVVEaGdaOHY3MUp4N0tDUldXVXJPOTVKemJPQjBiUUFTcVNieGVhXG5INm9vem9RMGNQMjVMcnpIWUt0NjE5eWdIZVJhS1hSY3NzTnZkUnArMnYxbGlGTGRqbjltdkovWk40YWVBZFRmXG5JcDNWME1aVE5yODlHQmt2YjNpUHFFbnZVZTdzeTdSMnQzU2R2OWtuUnByUjNJbkthQ2tOZXE4UjkzZHFBZDc1XG5XYXpEekFqQk9CeGFlQ1JYK01TU1Q4MkZXTmplblhkb0FQbWFsVlMwUFp2cmd6ZHVaT0Jla0xHZ1hNbng3VDBkXG5KM3NJVzVYUHA2NEhTNEt4YUo0a3M3YkJiMmg5T2VKTzdXRE1aVjd2a2k4aUs4Q3Y3MnQvbG8yaElob0VPVU53XG5aYTdETFJXQkFnTUJBQUVDZ2dFQUJIVHdNVDhBSDBCdjJTSE9qTkVVQTdoTHFBNHBFSExmaUc1c29YT3B1ZUVCXG4vMGwzY3BkbmZqejgvMTFXNGttSGNhb0s5UW1kR0NhNURTcDUxcHdSdkh5eE05TGY2YUdIa1JGdVRNRVFDUDhOXG4zMis1OHp2c2FraXQ5amFZbDZBWmJ4VmMrbHZkSG1HMzhXMUcwTUphRldka3I2ZDNaUXFjS2k3TWRzL3B4WXhRXG40RklvTGZPcCtIMmlOY1FYTzl3c0hFT2hxNTNYR1llQXRzV0N2bXBMaTZkUHBoQVJab1QydjdRK1E5RkVHUVRrXG5QT0Y3OWdMa3l4TmRwTmdFZWEveHMrVnhMSUtHZEFEUFpzbTBLamNpTFd4dmJzMFNWTUw2R0lMUUM0ZGxxYUxIXG5FMTAyZTBtdXVNeXNUd2RNM0hCcmJQUis4emtlRmhPNkZJQWdXeWhPa1FLQmdRRHVHWFc5QkdvckFuU2ZZZGFFXG4rSUN1ZVZyclVsRFl2TmJObTBsV2xLRmhzNTd4dmdnU3NiRE1pYjRiUldNNU1WbzNqMVRORFRZSWNtM0hGQWJ4XG5rK21HS0tJM1gwRjRKT2xTWW9QK3RCNzd4dUlDdnBpVjFRSlk2ZGJMSXhqeSs3WDNqakUwTTRDVEpoK29tYWxCXG5UOW9RR3dYUzVTVEk0UzNNTERtYWdWSnlzUUtCZ1FESW5HVXhobjRpOW1rNktKVUhNR0ZMZ3haY3JCNEJEV2tyXG5vWUV6eUhEOCtqa0N6OEJtYlVnVURVV2d5R2JpUjZqZEFmcTByR0tzQ29NRzlmcHlocEo0Snl0a1ptRkpiNE50XG5NNmZyUWh0N3d0MHVENmZ2elJib3JzVjhOUXJkakZGMm1lUEkxNTlkV3JFUnVsRjU3ZXdtQW4xRG5id3phZWZIXG5wWEMyOTNOajBRS0JnUUNXRXY0Zk1aVXBudGFiVHpQRGhFNjNxazRnWFRZUUpwYk42YjhFRDVMWTNqcWs3TDV4XG42Z1lpSmYvcGVJYmVHYmxmbzd3enNzd0g3dmc2cnVqaGcvV0JWa05JMjRXTWtOZHYwaUNZZmplNVF0WmFISUJZXG5rSFoyVEkzU1pFRHBoclpmWHdTc2ZubmdSZnRXYmVROUFuUFVDdlJVeFpHMS9CaTl4SEphYklEblFRS0JnUUMvXG5ycEFTVGt2ZjVFcVBRNCtDR3Z3Y1J0anJHNXBmcnd5Nm44cndTNm1LVHh5Q1R6ZXJwdWVrSVRwU2NxbTd0SFRwXG5GNmNSVTFYRXhSYUZaQ3MxbXRnQTdveExsbmVHejRKb3FWN2RMNEZMTTlwYTFLTEdRdFNNNTlIUzZHdkZYUG5KXG50U2t0RXJvM1hSeXJyN2VDSlkvcWtaNVhLVFJXZSs3M21HQ21zcklTd1FLQmdBajdibW94SVN1MHZSM0wyZGN5XG5qQlZxNkJCczhjQVpIK0luR212SjVIaUlPcFJER3ZOdEpZZFV2QTVTSStOZDFpWGxjUEhQVm1hbVpQd09sdUJyXG4yNjh2b3VGNkxPRytnbEc1NDJsR3JqdVV2ZVRGRWNhSEZvSXN0MDNYdnY5d2VvQitvTm5yYnYycHNRTUY4WVp5XG52c1BUMUc4YTFtOEl2UzlKdmVpREM0blhcbi0tLS0tRU5EIFBSSVZBVEUgS0VZLS0tLS1cbiIsICJjbGllbnRfZW1haWwiOiAic2hlZXQtYm90QGx1bmVyeS1jcm0tYm90LmlhbS5nc2VydmljZWFjY291bnQuY29tIiwgImNsaWVudF9pZCI6ICIxMTAyODgwNjIxNzUwMzE1NTY1NjAiLCAiYXV0aF91cmkiOiAiaHR0cHM6Ly9hY2NvdW50cy5nb29nbGUuY29tL28vb2F1dGgyL2F1dGgiLCAidG9rZW5fdXJpIjogImh0dHBzOi8vb2F1dGgyLmdvb2dsZWFwaXMuY29tL3Rva2VuIiwgImF1dGhfcHJvdmlkZXJfeDUwOV9jZXJ0X3VybCI6ICJodHRwczovL3d3dy5nb29nbGVhcGlzLmNvbS9vYXV0aDIvdjEvY2VydHMiLCAiY2xpZW50X3g1MDlfY2VydF91cmwiOiAiaHR0cHM6Ly93d3cuZ29vZ2xlYXBpcy5jb20vcm9ib3QvdjEvbWV0YWRhdGEveDUwOS9zaGVldC1ib3QlNDBsdW5lcnktY3JtLWJvdC5pYW0uZ3NlcnZpY2VhY2NvdW50LmNvbSIsICJ1bml2ZXJzZV9kb21haW4iOiAiZ29vZ2xlYXBpcy5jb20ifQ==").decode())
except:
    DEFAULT_CREDS = {}


DEFAULT_SHEET_ID = "1nBXm-dvnGWs9Lf79q2nz7RnvANc5kgPBIFVGmCGbZIg"

def get_gspread_client() -> Optional[gspread.Client]:
    creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    creds_dict = DEFAULT_CREDS
    
    if creds_json:
        try:
            creds_dict = json.loads(creds_json)
        except Exception:
            pass

    try:
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        return gspread.authorize(creds)
    except Exception as e:
        print(f"Error authenticating with Google Sheets: {e}")
        return None

def sync_account_to_sheets(
    account_id: int, 
    account_name: str, 
    phone: str, 
    password: str, 
    worker_name: str, 
    admin_name: str, 
    start_date: str,
    action: str = "UPDATE",
    partner_name: str = None,
    email_address: str = ""
):
    sheet_id = os.environ.get("GOOGLE_SHEET_ID") or DEFAULT_SHEET_ID
        
    client = get_gspread_client()
    if not client:
        return

    try:
        sheet = client.open_by_key(sheet_id).sheet1
        
        # 1. Update Main Accounts Sheet
        
        # Check if this CRM instance has a custom tab name configured in Render Env Vars
        import os
        custom_tab_name = os.environ.get("GOOGLE_SHEET_TAB_NAME")
        
        target_tab_name = partner_name or custom_tab_name
        
        if target_tab_name:
            try:
                sheet = client.open_by_key(sheet_id).worksheet(target_tab_name)
            except gspread.exceptions.WorksheetNotFound:
                sheet = client.open_by_key(sheet_id).add_worksheet(title=target_tab_name, rows="1000", cols="20")
                sheet.insert_row(["ID", "Имя аккаунта", "Номер", "Пароль 2FA", "Воркер", "Админ", "Дата назначения", "Дата выхода", "Почта"], 1)
        
        records = sheet.get_all_records(expected_headers=[])
        if not records and not sheet.row_values(1):
            sheet.insert_row(["ID", "Имя аккаунта", "Номер", "Пароль 2FA", "Воркер", "Админ", "Дата назначения", "Дата выхода", "Почта"], 1)
        
        # Find row by account_id
        try:
            cell = sheet.find(str(account_id), in_column=1)
        except gspread.exceptions.CellNotFound:
            cell = None
        
        if action == "Удаление аккаунта":
            if cell:
                sheet.delete_rows(cell.row)
        else:
            row_data = [
                str(account_id),
                account_name or "",
                phone or "",
                password or "",
                worker_name or "Свободен",
                admin_name or "Без админа",
                start_date or "",
                "", # Дата выхода (leave empty on create/update)
                email_address or ""
            ]
            if cell:
                sheet.update(f"A{cell.row}:I{cell.row}", [row_data])
            else:
                sheet.append_row(row_data)

        # 2. Log changes to 'Логи' sheet
        try:
            log_sheet = client.open_by_key(sheet_id).worksheet("Логи")
        except gspread.exceptions.WorksheetNotFound:
            log_sheet = client.open_by_key(sheet_id).add_worksheet(title="Логи", rows="1000", cols="5")
            log_sheet.insert_row(["Дата и Время", "Аккаунт", "Действие", "Воркер", "Админ"], 1)
            
        import datetime
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_sheet.append_row([
            now_str, 
            account_name or str(account_id),
            action,
            worker_name or "Свободен",
            admin_name or "Без админа"
        ])

    except Exception as e:
        print(f"Error syncing to Google Sheets: {e}")
        traceback.print_exc()


def set_shift_date_for_accounts(account_ids: list, shift_date: str):
    sheet_id = os.environ.get("GOOGLE_SHEET_ID") or DEFAULT_SHEET_ID
    client = get_gspread_client()
    if not client: return
    
    try:
        sheet = client.open_by_key(sheet_id).sheet1
        for acc_id in account_ids:
            try:
                cell = sheet.find(str(acc_id), in_column=1)
                if cell:
                    # Column H (8) is "Дата первой смены" (First Shift)
                    current_first_shift = sheet.cell(cell.row, 8).value
                    if not current_first_shift:
                        sheet.update_cell(cell.row, 8, shift_date)
                    
                    # Column J (10) is "Дата текущей/последней смены" (Current Shift)
                    sheet.update_cell(cell.row, 10, shift_date)
            except gspread.exceptions.CellNotFound:
                continue
    except Exception as e:
        print(f"Error setting shift date in Sheets: {e}")

def sync_partner_to_sheets(partner_id: int, company_name: str, contact: str, country: str, seats: int, payment_terms: str, experience: str, registration_time: str, response_time: str, rating: float, last_contact_date: str, advances: str, schedules: str):
    try:
        client = get_gspread_client()
        if not client: return
        sheet = client.open_by_key(DEFAULT_SHEET_ID)
        
        try:
            worksheet = sheet.worksheet("Партнеры")
        except gspread.exceptions.WorksheetNotFound:
            worksheet = sheet.add_worksheet(title="Партнеры", rows="1000", cols="20")
            headers = ["ID", "Агентство", "Контакт", "Страна", "Места", "Оплата", "Опыт", "Регистрация", "Ответ", "Рейтинг", "Последний контакт", "Авансы", "Графики"]
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
            last_contact_date or "",
            advances or "",
            schedules or ""
        ]
        
        if row_idx:
            worksheet.update(f"A{row_idx}:M{row_idx}", [row_data])
        else:
            worksheet.append_row(row_data)
            
    except Exception as e:
        print("Error syncing partner to sheets:", e)
        traceback.print_exc()
