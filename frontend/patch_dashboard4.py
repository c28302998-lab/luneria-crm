with open("src/app/dashboard/page.tsx", "r") as f:
    content = f.read()

# I want to add max-h-96 overflow-y-auto to the pending shifts space-y-3 div.
old_div = """          <div className="space-y-3">
            {pendingShifts.map(shift => ("""
new_div = """          <div className="space-y-3 max-h-96 overflow-y-auto pr-2">
            {pendingShifts.map(shift => ("""

content = content.replace(old_div, new_div)

with open("src/app/dashboard/page.tsx", "w") as f:
    f.write(content)
