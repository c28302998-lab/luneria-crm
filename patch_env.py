with open('backend/alembic/env.py', 'r') as f:
    content = f.read()
content = content.replace('import app.models.models', 'import app.models.models\nimport app.models.telegram\nimport app.models.email')
with open('backend/alembic/env.py', 'w') as f:
    f.write(content)
