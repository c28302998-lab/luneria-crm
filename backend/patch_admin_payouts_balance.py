with open("app/api/admin_payouts.py", "r") as f:
    content = f.read()

content = content.replace("admin.balance += payout_in.amount", "admin.balance -= payout_in.amount")
content = content.replace("admin.balance -= payout.amount", "admin.balance += payout.amount")

with open("app/api/admin_payouts.py", "w") as f:
    f.write(content)
