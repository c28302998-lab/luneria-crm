import asyncio
import os
from typing import Dict, Any
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError
from pydantic import BaseModel

from dotenv import load_dotenv
load_dotenv()
API_ID = int(os.getenv("TELEGRAM_API_ID", "0"))
API_HASH = os.getenv("TELEGRAM_API_HASH", "")

class AuthState(BaseModel):
    phone: str
    phone_code_hash: str
    client: Any = None # We won't pydantic serialize this
    
    class Config:
        arbitrary_types_allowed = True

class TelegramManager:
    def __init__(self):
        # Active verified clients: account_id -> TelegramClient
        self.clients: Dict[int, TelegramClient] = {}
        # Temporary clients during auth process: phone -> AuthState
        self.auth_sessions: Dict[str, AuthState] = {}
        
    async def get_client(self, account_id: int, session_string: str) -> TelegramClient:
        """Get or initialize a connected client for a specific account."""
        if not API_ID or not API_HASH:
            raise ValueError("Telegram API credentials not configured in .env")
            
        if account_id in self.clients:
            client = self.clients[account_id]
            if not client.is_connected():
                await client.connect()
            return client
            
        client = TelegramClient(StringSession(session_string), API_ID, API_HASH)
        await client.connect()
        
        if not await client.is_user_authorized():
            await client.disconnect()
            
            # --- AUTOMATION TRIGGER ---
            try:
                from app.db.database import SessionLocal
                from app.models.telegram import TelegramAccount
                from app.models.models import Task, User
                
                db = SessionLocal()
                acc = db.query(TelegramAccount).filter(TelegramAccount.id == account_id).first()
                if acc:
                    acc.status = "DISABLED"
                    admin_id = acc.responsible_admin_id or acc.assigned_user_id
                    if not admin_id:
                        owner = db.query(User).filter(User.role == "OWNER").first()
                        admin_id = owner.id if owner else 1
                        
                    task = Task(
                        title=f"Автоматизация: Ошибка сессии на аккаунте #{account_id}",
                        description=f"Telegram-аккаунт {acc.name or acc.phone} вылетел (сессия невалидна или revoked). Требуется перерегистрация/перепривязка.",
                        priority="HIGH",
                        assigned_user_id=admin_id,
                        creator_id=1,
                        status="NEW"
                    )
                    db.add(task)
                    db.commit()
                db.close()
            except Exception as e:
                print("Failed to trigger automation:", e)
            # --------------------------
            
            raise Exception("Telegram session is no longer valid or revoked")
            
        self.clients[account_id] = client
        return client

    async def download_message_media(self, account_id: int, chat_id: int, message_id: int, session_string: str = None) -> bytes:
        client = await self.get_client(account_id, session_string) if session_string else self.clients.get(account_id)
        if not client:
            raise Exception('Client not connected')
        if not client:
            raise Exception("Client not connected")
        
        msg = await client.get_messages(chat_id, ids=message_id)
        if not msg or not msg.media:
            return None
            
        data = await client.download_media(msg, file=bytes)
        return data

    async def disconnect_account(self, account_id: int):
        """Force disconnect and remove an account session (e.g. for Session Lock)."""
        if account_id in self.clients:
            try:
                import asyncio
                await asyncio.wait_for(self.clients[account_id].disconnect(), timeout=2.0)
            except:
                pass
            del self.clients[account_id]

    async def auth_send_code(self, phone: str) -> str:
        """Step 1: Send SMS code to phone."""
        if not API_ID or not API_HASH:
            raise ValueError("Telegram API credentials not configured")
            
        client = TelegramClient(StringSession(), API_ID, API_HASH)
        await client.connect()
        
        try:
            result = await client.send_code_request(phone)
            self.auth_sessions[phone] = AuthState(
                phone=phone,
                phone_code_hash=result.phone_code_hash,
                client=client
            )
            return result.phone_code_hash
        except Exception as e:
            await client.disconnect()
            raise e

    async def auth_sign_in(self, phone: str, code: str, password: str = None) -> tuple[str, str]:
        """Step 2: Submit code (and optionally password) to get session string."""
        if phone not in self.auth_sessions:
            raise ValueError("Auth session not found. Please request code again.")
            
        state = self.auth_sessions[phone]
        client = state.client
        
        try:
            if password:
                # If password was provided, it means we hit 2FA earlier
                await client.sign_in(password=password)
            else:
                await client.sign_in(phone, code, phone_code_hash=state.phone_code_hash)
                
            # Successfully logged in! Return the session string.
            me = await client.get_me()
            session_string = client.session.save()
            await client.disconnect()
            del self.auth_sessions[phone]
            return session_string, getattr(me, 'username', None)
            
        except SessionPasswordNeededError:
            # Code was correct, but 2FA is required.
            # Keep client alive in dict so they can submit password.
            raise ValueError("2FA_REQUIRED")
        except Exception as e:
            await client.disconnect()
            del self.auth_sessions[phone]
            raise e


    async def edit_2fa_password(self, session_string: str, old_password: str, new_password: str) -> str:
        if not API_ID or not API_HASH:
            raise ValueError("Telegram API credentials not configured")
            
        client = TelegramClient(StringSession(session_string), API_ID, API_HASH)
        await client.connect()
        try:
            if not await client.is_user_authorized():
                raise ValueError("Session is invalid or expired")
                
            await client.edit_2fa(current_password=old_password, new_password=new_password)
            new_session = client.session.save()
            return new_session
        finally:
            await client.disconnect()

    async def resolve_entity(self, account_id: int, query: str, session_string: str = None) -> dict:
        client = await self.get_client(account_id, session_string) if session_string else self.clients.get(account_id)
        if not client:
            raise Exception('Client not connected')
        if not client:
            raise Exception("Client not connected")

        try:
            # If it's a phone number (starts with + or digits and > 8 chars), try to add to contacts first
            import re
            clean_q = re.sub(r'\D', '', query)
            if (query.startswith('+') or query.isdigit()) and len(clean_q) >= 10:
                from telethon.tl.functions.contacts import ImportContactsRequest
                from telethon.tl.types import InputPhoneContact
                phone_str = '+' + clean_q if not clean_q.startswith('+') else clean_q
                contact = InputPhoneContact(client_id=0, phone=phone_str, first_name="Client", last_name="")
                await client(ImportContactsRequest([contact]))
                
            entity = await client.get_entity(query)

        except Exception as e:
            raise ValueError(f"Could not find user or chat: {e}")
            
        name = getattr(entity, 'title', None)
        if not name:
            first = getattr(entity, 'first_name', '') or ''
            last = getattr(entity, 'last_name', '') or ''
            name = (first + ' ' + last).strip() or getattr(entity, 'username', 'Unknown')
            
        return {
            "id": str(entity.id),
            "name": name,
            "username": getattr(entity, 'username', None),
            "date": None,
            "message": "Start a new chat",
            "unread_count": 0,
            "archived": False
        }

    async def get_profile_photo(self, account_id: int, entity_id: int, session_string: str = None) -> bytes:
        client = await self.get_client(account_id, session_string) if session_string else self.clients.get(account_id)
        if not client:
            raise Exception('Client not connected')
        if not client:
            raise Exception("Client not connected")
        try:
            entity = await client.get_entity(entity_id)
            return await client.download_profile_photo(entity, file=bytes)
        except Exception:
            return None


# Global singleton
telegram_manager = TelegramManager()

