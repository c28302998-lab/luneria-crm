import re

with open("src/app/dashboard/telegram/page.tsx", "r") as f:
    content = f.read()

# Add import
import_stmt = "import { parsePhoneNumberFromString } from 'libphonenumber-js';\n"
if "parsePhoneNumberFromString" not in content:
    content = import_stmt + content

# Add formatter function
formatter = """
const formatPhone = (phone: string | null) => {
  if (!phone) return '-';
  let p = phone.trim();
  if (!p.startsWith('+')) {
    p = '+' + p;
  }
  const parsed = parsePhoneNumberFromString(p);
  if (parsed) {
    return parsed.formatInternational();
  }
  return phone;
};

export default function TelegramPage() {
"""
content = content.replace("export default function TelegramPage() {", formatter)

# Replace the phone render
content = content.replace("{acc.name} ({acc.phone})", "{acc.name} ({formatPhone(acc.phone)})")
content = content.replace("Номер: {acc.phone}<br/>", "Номер: {formatPhone(acc.phone)}<br/>")

with open("src/app/dashboard/telegram/page.tsx", "w") as f:
    f.write(content)
