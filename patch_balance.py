with open("backend/app/api/balance_requests.py", "r") as f:
    content = f.read()

content = content.replace("worker.balance -= br.amount", "worker.balance = (worker.balance or 0.0) - br.amount")
content = content.replace("worker.balance += br.amount", "worker.balance = (worker.balance or 0.0) + br.amount")

with open("backend/app/api/balance_requests.py", "w") as f:
    f.write(content)
