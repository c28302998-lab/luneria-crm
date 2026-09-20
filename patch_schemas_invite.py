with open('backend/app/schemas/schemas.py', 'r') as f:
    content = f.read()

content = content.replace(
'''class Worker(WorkerBase):
    id: int''',
'''class Worker(WorkerBase):
    id: int
    invite_link: Optional[str] = None'''
)

with open('backend/app/schemas/schemas.py', 'w') as f:
    f.write(content)
