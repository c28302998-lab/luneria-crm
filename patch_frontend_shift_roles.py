with open('frontend/src/app/dashboard/shifts/page.tsx', 'r') as f:
    content = f.read()

# Change the render condition for the Approve button
old_button_cond = "{shift.status === 'PENDING_REVIEW' && ("
new_button_cond = "{shift.status === 'PENDING_REVIEW' && (user?.role === 'OWNER' || user?.role === 'FINANCE') && ("
content = content.replace(old_button_cond, new_button_cond)

# Also add the text for Admin "Ожидает Овнера"
admin_wait_text = """
                      {shift.status === 'PENDING_REVIEW' && user?.role === 'ADMIN' && (
                        <span className="text-xs text-muted-foreground italic">Ожидает Овнера</span>
                      )}
"""
content = content.replace("</button>\n                      )}", "</button>\n                      )}" + admin_wait_text)

with open('frontend/src/app/dashboard/shifts/page.tsx', 'w') as f:
    f.write(content)
