with open('backend/app/api/auth.py', 'r') as f:
    lines = f.readlines()
    
# check if get_password_hash is at the top
has_import = any('get_password_hash' in line and 'from app.core.security' in line for line in lines[:20])

if not has_import:
    for i, line in enumerate(lines):
        if 'from app.core.security import verify_password, create_access_token' in line:
            lines[i] = 'from app.core.security import verify_password, create_access_token, get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES\n'
            break
            
with open('backend/app/api/auth.py', 'w') as f:
    f.writelines(lines)
