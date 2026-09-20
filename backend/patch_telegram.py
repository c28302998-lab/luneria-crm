with open("app/services/telegram_manager.py", "r") as f:
    content = f.read()

import re
content = re.sub(r'API_ID = int\(os.getenv\("TELEGRAM_API_ID", "0"\)\)', 'from dotenv import load_dotenv\nload_dotenv()\nAPI_ID = int(os.getenv("TELEGRAM_API_ID", "0"))', content)

with open("app/services/telegram_manager.py", "w") as f:
    f.write(content)
