import re

def fix_file(path):
    with open(path, "r") as f:
        content = f.read()

    # Add onKeyDown to shift input
    content = content.replace(
        'onBlur={(e) => handleInfoChange(worker.id, \'shift\', e.target.value)}',
        'onBlur={(e) => handleInfoChange(worker.id, \'shift\', e.target.value)}\n                            onKeyDown={(e) => e.key === \'Enter\' && e.currentTarget.blur()}'
    )
    
    # Add onKeyDown to account_info input
    content = content.replace(
        'onBlur={(e) => handleInfoChange(worker.id, \'account_info\', e.target.value)}',
        'onBlur={(e) => handleInfoChange(worker.id, \'account_info\', e.target.value)}\n                            onKeyDown={(e) => e.key === \'Enter\' && e.currentTarget.blur()}'
    )

    with open(path, "w") as f:
        f.write(content)

fix_file("frontend/src/app/dashboard/attendance/page.tsx")
