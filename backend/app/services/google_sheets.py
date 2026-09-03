import os
import json
from concurrent.futures import ThreadPoolExecutor
import asyncio
from datetime import datetime

try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError:
    gspread = None
    Credentials = None

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

executor = ThreadPoolExecutor(max_workers=3)

class GoogleSheetsService:
    def __init__(self):
        self.credentials_json = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
        self.spreadsheet_id = os.getenv("GOOGLE_SHEETS_ID")
        self.client = None

        if not gspread or not Credentials:
            print("Google Sheets dependencies not installed.")
            return

        if self.credentials_json and self.spreadsheet_id:
            try:
                creds_dict = json.loads(self.credentials_json)
                credentials = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
                self.client = gspread.authorize(credentials)
            except Exception as e:
                print(f"Failed to initialize Google Sheets: {e}")

    def _sync_new_worker_sync(self, worker_data: dict):
        if not self.client:
            return
        try:
            sheet = self.client.open_by_key(self.spreadsheet_id)
            
            # 1. Запись на лист "Люди"
            try:
                ws_people = sheet.worksheet("Люди")
                col_a = ws_people.col_values(1)
                next_row = len(col_a) + 1
                new_id = f"id {next_row-1:03d}" if next_row > 1 else "id 001"
                
                row_data_people = [
                    new_id,
                    worker_data.get("candidate_name", ""),
                    worker_data.get("referrer_name", ""),
                    worker_data.get("created_at", datetime.now().strftime("%d.%m.%Y")),
                    worker_data.get("status", "В работе"),
                    worker_data.get("telegram", ""),
                    worker_data.get("partner_name", "")
                ]
                ws_people.update(f"A{next_row}", [row_data_people])
            except Exception as e:
                print(f"Error updating Люди: {e}")

            # 2. Заготовка в Реферальной структуре
            partner = worker_data.get("partner_name", "")
            if partner:
                try:
                    ws_ref = sheet.worksheet(f"Реферальная структура {partner}")
                    ref_col_a = ws_ref.col_values(1)
                    ref_next_row = len(ref_col_a) + 1
                    row_data_ref = [
                        worker_data.get("candidate_name", ""), # Человек
                        worker_data.get("referrer_name", ""), # Реферер
                        worker_data.get("status", "В работе"), # Статус
                        worker_data.get("created_at", datetime.now().strftime("%d.%m.%Y")), # Дата регистрации
                        "", # Дата первой смены
                        worker_data.get("telegram", ""), # Telegram
                        "0", # Доход
                        "", # Аккаунт человека
                        "", # Аккаунт реферера
                        partner # Агенция
                    ]
                    ws_ref.update(f"A{ref_next_row}", [row_data_ref])
                except gspread.exceptions.WorksheetNotFound:
                    print(f"Worksheet Реферальная структура {partner} not found")
                except Exception as e:
                    print(f"Error updating Реферальная: {e}")

        except Exception as e:
            print(f"Google Sheets sync error (worker): {e}")

    async def sync_new_worker(self, worker_data: dict):
        if not self.client:
            return
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(executor, self._sync_new_worker_sync, worker_data)

    def _sync_issued_account_sync(self, account_data: dict):
        if not self.client:
            return
        try:
            sheet = self.client.open_by_key(self.spreadsheet_id)
            try:
                worksheet = sheet.worksheet("Аккаунты")
            except gspread.exceptions.WorksheetNotFound:
                return

            col_a = worksheet.col_values(1)
            next_row = len(col_a) + 1
            new_id = f"ID {next_row-1:03d}" if next_row > 1 else "ID 001"
            
            row_data = [
                new_id,
                account_data.get("account_name", ""),
                account_data.get("account_number", ""),
                account_data.get("admin_name", ""), # Закреплен за
                account_data.get("status", "В работе"),
                account_data.get("password_tg", ""),
                "", # Gmail
                "", # Password Gmail
                "" # Status 2
            ]
            worksheet.update(f"A{next_row}", [row_data])
        except Exception as e:
            print(f"Google Sheets sync error (account): {e}")

    async def sync_issued_account(self, account_data: dict):
        if not self.client:
            return
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(executor, self._sync_issued_account_sync, account_data)

    def _sync_income_sync(self, income_data: dict):
        if not self.client:
            return
        try:
            sheet = self.client.open_by_key(self.spreadsheet_id)
            partner = income_data.get("partner_name", "")
            if not partner:
                return
                
            try:
                worksheet = sheet.worksheet(f"Реферальная структура {partner}")
            except gspread.exceptions.WorksheetNotFound:
                return

            names = worksheet.col_values(1) # Column A is Человек
            worker_name = income_data.get("worker_name", "")
            
            try:
                row_idx = names.index(worker_name) + 1
            except ValueError:
                # Person not found, append a new row
                row_idx = len(names) + 1
                worksheet.update(f"A{row_idx}", [[worker_name, "", "", "", "", "", "0"]])
                
            # Update Date of first shift (Col E) if empty
            col_e = worksheet.col_values(5)
            first_shift = col_e[row_idx-1] if row_idx <= len(col_e) else ""
            if not first_shift or first_shift.strip() == "":
                worksheet.update(f"E{row_idx}", [[income_data.get("date", "")]])
                
            # Add Income (Col G)
            col_g = worksheet.col_values(7)
            current_income = col_g[row_idx-1] if row_idx <= len(col_g) else "0"
            try:
                # Try to sum it up if it's a number
                curr_val = float(current_income.replace(",", "."))
                new_val = float(income_data.get("income", 0))
                total = curr_val + new_val
                worksheet.update(f"G{row_idx}", [[str(total)]])
            except:
                # If parsing fails, just overwrite
                worksheet.update(f"G{row_idx}", [[str(income_data.get("income", 0))]])

        except Exception as e:
            print(f"Google Sheets sync error (income): {e}")

    async def sync_income(self, income_data: dict):
        if not self.client:
            return
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(executor, self._sync_income_sync, income_data)

    def _sync_partner_sync(self, partner_data: dict):
        if not self.client:
            return
        try:
            sheet = self.client.open_by_key(self.spreadsheet_id)
            try:
                worksheet = sheet.worksheet("Partner")
            except gspread.exceptions.WorksheetNotFound:
                return

            col_a = worksheet.col_values(1)
            next_row = len(col_a) + 1
            
            row_data = [
                partner_data.get("name", ""),
                partner_data.get("contact", ""),
                partner_data.get("notes", ""),
                partner_data.get("schedule", "")
            ]
            worksheet.update(f"A{next_row}", [row_data])
        except Exception as e:
            print(f"Google Sheets sync error (partner): {e}")

    async def sync_partner(self, partner_data: dict):
        if not self.client:
            return
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(executor, self._sync_partner_sync, partner_data)

sheets_service = GoogleSheetsService()
