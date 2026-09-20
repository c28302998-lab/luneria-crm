import asyncio
from telethon import TelegramClient, StringSession
import os
import sys

# We need to instantiate the client and try downloading a media from some chat
# But wait, without credentials I can't.
