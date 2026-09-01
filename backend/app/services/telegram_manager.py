import asyncio
import os
from typing import Dict, Any
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError
from pydantic import BaseModel

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
            raise Exception("Telegram session is no longer valid or revoked")
            
        self.clients[account_id] = client
        return client

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

    async def auth_sign_in(self, phone: str, code: str, password: str = None) -> str:
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
            session_string = client.session.save()
            await client.disconnect()
            del self.auth_sessions[phone]
            return session_string
            
        except SessionPasswordNeededError:
            # Code was correct, but 2FA is required.
            # Keep client alive in dict so they can submit password.
            raise ValueError("2FA_REQUIRED")
        except Exception as e:
            await client.disconnect()
            del self.auth_sessions[phone]
            raise e

# Global singleton
telegram_manager = TelegramManager()
