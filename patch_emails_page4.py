with open('frontend/src/app/dashboard/emails/page.tsx', 'r') as f:
    content = f.read()

# Change /workers to /users
content = content.replace(
'''const fetchWorkers = async () => {
    try {
      const { data } = await api.get('/workers');
      setWorkers(data);
    } catch (e) {}
  };''',
'''const fetchWorkers = async () => {
    try {
      const { data } = await api.get('/users');
      setWorkers(data.filter((u: any) => u.role === 'WORKER'));
    } catch (e) {}
  };'''
)

# Fix the render of worker names
content = content.replace(
    '{w.candidate?.first_name} {w.candidate?.last_name} ({w.candidate?.email})',
    '{w.first_name} {w.last_name} ({w.email})'
)

# Fix the display on cards
content = content.replace(
    'workers.find(w => w.id === acc.assigned_worker_id)?.candidate?.first_name',
    'workers.find(w => w.id === acc.assigned_worker_id)?.first_name || workers.find(w => w.id === acc.assigned_worker_id)?.email'
)

with open('frontend/src/app/dashboard/emails/page.tsx', 'w') as f:
    f.write(content)
