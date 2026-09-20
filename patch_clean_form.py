with open("frontend/src/app/dashboard/partners/page.tsx", "r") as f:
    content = f.read()

import re

# Fix the messy onClick
bad_onclick = r"onClick=\{\(\) => \{ setEditingId\(null\); setFormData\(\{ company_name: '', contact: '', country: '', seats: 0, payment_terms: '', experience: '', registration_time: '', response_time: '', rating: 0, last_contact_date: '', advances: '', schedules: '',\n    schedules: '',\n    advances: '',\n    schedules: '' \}\); setIsModalOpen\(true\); \}\}"
good_onclick = "onClick={() => { setEditingId(null); setFormData({ company_name: '', contact: '', country: '', seats: 0, payment_terms: '', experience: '', registration_time: '', response_time: '', rating: 0, last_contact_date: '', advances: '', schedules: '' }); setIsModalOpen(true); }}"

content = re.sub(bad_onclick, good_onclick, content)

# Also fix the previous setFormData which might have newlines messed up
bad_set1 = r"response_time: '', rating: 0, last_contact_date: '', advances: '', schedules: '',\n    schedules: '',\n    advances: '',\n    schedules: ''"
good_set1 = r"response_time: '', rating: 0, last_contact_date: '', advances: '', schedules: ''"
content = re.sub(bad_set1, good_set1, content)

with open("frontend/src/app/dashboard/partners/page.tsx", "w") as f:
    f.write(content)
