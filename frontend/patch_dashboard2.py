with open("src/app/dashboard/page.tsx", "r") as f:
    content = f.read()

fetch_code = """        const [candRes, workRes, tasksRes, logsRes, statsFinRes] = await Promise.all(["""
new_fetch_code = """        api.get('/attendance/pending').then(({data}) => setPendingShifts(data)).catch(console.error);
        const [candRes, workRes, tasksRes, logsRes, statsFinRes] = await Promise.all(["""
content = content.replace(fetch_code, new_fetch_code)

with open("src/app/dashboard/page.tsx", "w") as f:
    f.write(content)
