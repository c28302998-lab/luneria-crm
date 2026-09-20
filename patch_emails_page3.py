with open('frontend/src/app/dashboard/emails/page.tsx', 'r') as f:
    content = f.read()

content = content.replace(
    'const [formData, setFormData] = useState({ email_address: \'\', app_password: \'\' });',
    'const [formData, setFormData] = useState<any>({ email_address: \'\', app_password: \'\' });'
)

with open('frontend/src/app/dashboard/emails/page.tsx', 'w') as f:
    f.write(content)
