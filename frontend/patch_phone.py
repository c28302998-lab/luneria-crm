import re

with open("src/app/dashboard/telegram-accounts/page.tsx", "r") as f:
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

export default function TelegramAccountsPage() {
"""
content = content.replace("export default function TelegramAccountsPage() {", formatter)

# Replace the phone render
old_render = '<td className="px-6 py-4 whitespace-nowrap text-sm text-foreground">{acc.phone}</td>'
new_render = '<td className="px-6 py-4 whitespace-nowrap text-sm text-foreground">{formatPhone(acc.phone)}</td>'
content = content.replace(old_render, new_render)

with open("src/app/dashboard/telegram-accounts/page.tsx", "w") as f:
    f.write(content)
