import re

with open("src/app/dashboard/reports/page.tsx", "r") as f:
    content = f.read()

template = """📊 DAILY TEAM REPORT

📅 Дата: 

👥 КОМАНДА

👤 Всего работников: 
🟢 Вышли на смену: 
🔴 Не вышли: 
🆕 Новых работников: 

━━━━━━━━━━━━━━

💰 ФИНАНСОВЫЙ РЕЗУЛЬТАТ

💵 Общий заработок команды за сегодня: $


━━━━━━━━━━━━━━

👤 РЕЗУЛЬТАТЫ ПО РАБОТНИКАМ

1. [Имя]
   📅 Работает с: 
   🟢 Смена: 
   ⏱ 
   💰 Заработал за сегодня: $
   📊 Продаж: 

2. [Имя]
   📅 Работает с: 
   🔴 НЕ ВЫШЕЛ
   Причина: 

━━━━━━━━━━━━━━

🏆 ТОП РЕЗУЛЬТАТЫ

🥇 
🥈 
🥉 

━━━━━━━━━━━━━━

⚠️ НЕ ВЫШЛИ НА СМЕНУ

🔴 

━━━━━━━━━━━━━━

📈 ИТОГО ЗА ДЕНЬ

Общий заработок: $
Работников на смене: 
Не вышли: 

📸 Скрины статистики прикреплены."""

# Change rows
content = content.replace("rows={4}", "rows={20} style={{ fontFamily: 'monospace' }}")

# Ensure template is used
content = content.replace("const [isModalOpen, setIsModalOpen] = useState(false);", "const [isModalOpen, setIsModalOpen] = useState(false);")

# We can replace the setIsModalOpen(true) call with a wrapper that pre-fills content
content = content.replace("onClick={() => setIsModalOpen(true)}", f"onClick={{() => {{\n          setFormData({{\\n            ...formData,\\n            content: `{template}`\\n          }});\n          setIsModalOpen(true);\n        }}}}")

with open("src/app/dashboard/reports/page.tsx", "w") as f:
    f.write(content)
