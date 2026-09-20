with open('backend/app/api/router.py', 'r') as f:
    content = f.read()

if 'emails' not in content:
    content = content.replace(
        'balance_requests\n)',
        'balance_requests, emails\n)'
    )
    content += '\napi_router.include_router(emails.router, prefix="/emails", tags=["emails"])\n'
    with open('backend/app/api/router.py', 'w') as f:
        f.write(content)
