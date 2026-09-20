with open('backend/app/schemas/email.py', 'r') as f:
    content = f.read()

content = content.replace(
'''class EmailAccountResponse(EmailAccountBase):
    id: int
    status: str
    last_activity_at: Optional[datetime] = None
    created_at: datetime''',
'''class EmailAccountResponse(BaseModel):
    id: int
    email_address: EmailStr
    imap_server: Optional[str]
    imap_port: Optional[int]
    smtp_server: Optional[str]
    smtp_port: Optional[int]
    assigned_worker_id: Optional[int]
    assigned_admin_id: Optional[int]
    status: str
    last_activity_at: Optional[datetime] = None
    created_at: datetime'''
)

with open('backend/app/schemas/email.py', 'w') as f:
    f.write(content)
