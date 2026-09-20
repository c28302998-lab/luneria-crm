import re

with open("frontend/src/app/layout.tsx", "r") as f:
    layout = f.read()

layout = layout.replace(
    'title: "Lunery CRM",',
    'title: `${process.env.NEXT_PUBLIC_AGENCY_NAME || "Lunery"} CRM`,'
)

with open("frontend/src/app/layout.tsx", "w") as f:
    f.write(layout)
