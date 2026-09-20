with open('frontend/src/app/dashboard/emails/page.tsx', 'r') as f:
    content = f.read()

replacement = '''<div>
              <h3 className="font-medium text-lg truncate">{acc.email_address}</h3>
              <p className="text-sm text-gray-500 mt-1">
                Статус: <span className={acc.status === 'ACTIVE' ? 'text-green-500' : 'text-red-500'}>{acc.status}</span>
              </p>
              {(user?.role === 'OWNER' || user?.role === 'ADMIN') && (
                <p className="text-sm text-gray-500 mt-1">
                  Работник: {workers.find(w => w.id === acc.assigned_worker_id) ? workers.find(w => w.id === acc.assigned_worker_id)?.candidate?.first_name : 'Не назначен'}
                </p>
              )}
            </div>'''

content = content.replace('''<div>
              <h3 className="font-medium text-lg truncate">{acc.email_address}</h3>
              <p className="text-sm text-gray-500 mt-1">
                Статус: <span className={acc.status === 'ACTIVE' ? 'text-green-500' : 'text-red-500'}>{acc.status}</span>
              </p>
            </div>''', replacement)

with open('frontend/src/app/dashboard/emails/page.tsx', 'w') as f:
    f.write(content)
print("Patched again")
