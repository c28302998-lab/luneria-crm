import re

# page.tsx
with open("frontend/src/app/page.tsx", "r") as f:
    page = f.read()

page = page.replace(
    '">Lunery</span>',
    '">{process.env.NEXT_PUBLIC_AGENCY_NAME || "Lunery"}</span>'
)
page = page.replace(
    'Почему выбирают Lunery?',
    'Почему выбирают {process.env.NEXT_PUBLIC_AGENCY_NAME || "Lunery"}?'
)
page = page.replace(
    '">Lunery Agency</span>',
    '">{process.env.NEXT_PUBLIC_AGENCY_NAME || "Lunery Agency"}</span>'
)
page = page.replace(
    '© 2026 Lunery.',
    '© 2026 {process.env.NEXT_PUBLIC_AGENCY_NAME || "Lunery"}.'
)

with open("frontend/src/app/page.tsx", "w") as f:
    f.write(page)

# dashboard/layout.tsx
with open("frontend/src/app/dashboard/layout.tsx", "r") as f:
    dash = f.read()

dash = dash.replace(
    '">Lunery CRM</span>',
    '">{process.env.NEXT_PUBLIC_AGENCY_NAME ? process.env.NEXT_PUBLIC_AGENCY_NAME + " CRM" : "Lunery CRM"}</span>'
)
with open("frontend/src/app/dashboard/layout.tsx", "w") as f:
    f.write(dash)

# login/page.tsx
with open("frontend/src/app/login/page.tsx", "r") as f:
    login = f.read()

login = login.replace(
    '>Lunery CRM</h2>',
    '>{process.env.NEXT_PUBLIC_AGENCY_NAME ? process.env.NEXT_PUBLIC_AGENCY_NAME + " CRM" : "Lunery CRM"}</h2>'
)
with open("frontend/src/app/login/page.tsx", "w") as f:
    f.write(login)

