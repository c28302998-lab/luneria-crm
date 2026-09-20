with open("backend/app/api/telegram_proxy.py", "r") as f:
    content = f.read()

import re

# Add imports for telethon media types
if "from telethon.tl.types import" not in content:
    content = content.replace(
        "from fastapi import APIRouter",
        "from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument, DocumentAttributeAudio, DocumentAttributeVideo\nfrom fastapi import APIRouter"
    )

old_for = """        messages = []
        for m in msgs:
            messages.append({
                "id": m.id,
                "sender_id": str(m.sender_id) if m.sender_id else None,
                "text": m.text,
                "date": m.date.isoformat() if m.date else None,
                "is_reply": m.is_reply,
                "out": m.out
            })"""

new_for = """        messages = []
        for m in msgs:
            media_type = None
            if getattr(m, 'media', None):
                if isinstance(m.media, MessageMediaPhoto):
                    media_type = "photo"
                elif isinstance(m.media, MessageMediaDocument):
                    if hasattr(m.media.document, 'attributes'):
                        for attr in m.media.document.attributes:
                            if isinstance(attr, DocumentAttributeAudio):
                                media_type = "voice" if getattr(attr, 'voice', False) else "audio"
                            elif isinstance(attr, DocumentAttributeVideo):
                                media_type = "video"
                    if not media_type:
                        media_type = "document"

            messages.append({
                "id": m.id,
                "sender_id": str(m.sender_id) if m.sender_id else None,
                "text": m.text,
                "date": m.date.isoformat() if m.date else None,
                "is_reply": m.is_reply,
                "out": m.out,
                "media_type": media_type
            })"""

content = content.replace(old_for, new_for)

with open("backend/app/api/telegram_proxy.py", "w") as f:
    f.write(content)
