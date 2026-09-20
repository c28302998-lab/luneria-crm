with open("app/api/workers.py", "r") as f:
    content = f.read()

import re

# In create_worker
content = content.replace('name=candidate.first_name,\n            role="WORKER"', 'name=candidate.first_name,\n            role="WORKER",\n            raw_password=default_password')

# In create_worker_account (new account logic)
content = content.replace('name=candidate.first_name or f"Worker {worker.id}",\n        role="WORKER"', 'name=candidate.first_name or f"Worker {worker.id}",\n        role="WORKER",\n        raw_password=new_password')

with open("app/api/workers.py", "w") as f:
    f.write(content)
