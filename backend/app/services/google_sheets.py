import os
import json
import gspread
from google.oauth2.service_account import Credentials
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

executor = ThreadPoolExecutor(max_workers=5)

class GoogleSheetsService:
    def __init__(self):
        self.client = None
        self.spreadsheet_id = os.getenv("GOOGLE_SHEETS_ID")
        self.credentials_json = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
        
        if self.credentials_json and self.spreadsheet_id:
            try:
                creds_dict = json.loads(self.credentials_json)
                credentials = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
                self.client = gspread.authorize(credentials)
            except Exception as e:
                print(f"Failed to initialize Google Sheets: {e}")

    def _sync_worker_sync(self, worker_data: dict):
        if not self.client:
            return
        try:
            sheet = self.client.open_by_key(self.spreadsheet_id)
            try:
                worksheet = sheet.worksheet("Работники")
            except gspread.exceptions.WorksheetNotFound:
                worksheet = sheet.sheet1

            col_a = worksheet.col_values(1)
            next_row = len(col_a) + 1
            
            row_data = [
                worker_data.get("id", ""),
                worker_data.get("candidate_name", ""),
                worker_data.get("admin_name", ""),
                worker_data.get("created_at", datetime.now().strftime("%d.%m.%Y")),
                worker_data.get("status", "ACTIVE"),
            ]
            worksheet.update(f"A{next_row}", [row_data])
        except Exception as e:
            print(f"Google Sheets sync error (worker): {e}")

    def _sync_account_sync(self, account_data: dict):
        if not self.client:
            return
        try:
            sheet = self.client.open_by_key(self.spreadsheet_id)
            try:
                worksheet = sheet.worksheet("ТГ Аккаунты")
            except gspread.exceptions.WorksheetNotFound:
                try:
                    worksheet = sheet.worksheet("Аккаунты")
                except:
                    return

            col_a = worksheet.col_values(1)
            next_row = len(col_a) + 1
            
            row_data = [
                account_data.get("account_number", ""),
                account_data.get("admin_name", ""),
                account_data.get("issued_at", datetime.now().strftime("%d.%m.%Y")),
            ]
            worksheet.update(f"A{next_row}", [row_data])
        except Exception as e:
            print(f"Google Sheets sync error (account): {e}")

    async def sync_new_worker(self, worker_data: dict):
        if not self.client:
            return
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(executor, self._sync_worker_sync, worker_data)

    async def sync_issued_account(self, account_data: dict):
        if not self.client:
            return
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(executor, self._sync_account_sync, account_data)

sheets_service = GoogleSheetsService()
