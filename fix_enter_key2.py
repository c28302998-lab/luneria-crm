import re

with open("frontend/src/app/dashboard/workers/[id]/page.tsx", "r") as f:
    content = f.read()

content = content.replace(
    'onBlur={(e) => handleInfoChange(\'shift\', e.target.value)}',
    'onBlur={(e) => handleInfoChange(\'shift\', e.target.value)}\n                onKeyDown={(e) => e.key === \'Enter\' && e.currentTarget.blur()}'
)

content = content.replace(
    'onBlur={(e) => handleInfoChange(\'account_info\', e.target.value)}',
    'onBlur={(e) => handleInfoChange(\'account_info\', e.target.value)}\n                onKeyDown={(e) => e.key === \'Enter\' && e.currentTarget.blur()}'
)

with open("frontend/src/app/dashboard/workers/[id]/page.tsx", "w") as f:
    f.write(content)
