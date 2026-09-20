import re

with open("backend/app/services/telegram_manager.py", "r") as f:
    content = f.read()

# We need to import ImportContactsRequest, InputPhoneContact from telethon.tl.functions.contacts, telethon.tl.types
# Let's just do it inside resolve_entity

phone_import_logic = """
        try:
            # If it's a phone number (starts with + or digits and > 8 chars), try to add to contacts first
            import re
            clean_q = re.sub(r'\\D', '', query)
            if (query.startswith('+') or query.isdigit()) and len(clean_q) >= 10:
                from telethon.tl.functions.contacts import ImportContactsRequest
                from telethon.tl.types import InputPhoneContact
                phone_str = '+' + clean_q if not clean_q.startswith('+') else clean_q
                contact = InputPhoneContact(client_id=0, phone=phone_str, first_name="Client", last_name="")
                await client(ImportContactsRequest([contact]))
                
            entity = await client.get_entity(query)
"""

content = content.replace("        try:\n            entity = await client.get_entity(query)", phone_import_logic)

with open("backend/app/services/telegram_manager.py", "w") as f:
    f.write(content)
