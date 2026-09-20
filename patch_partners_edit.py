with open("frontend/src/app/dashboard/partners/page.tsx", "r") as f:
    content = f.read()

import re

# Add state for editing
old_state = """  const [formData, setFormData] = useState({
    company_name: '',
    contact: '',
    country: '',
    seats: 0,
    payment_terms: '',
    experience: '',
    registration_time: '',
    response_time: '',
    rating: 0,
    last_contact_date: ''
  });"""

new_state = """  const [editingId, setEditingId] = useState<number | null>(null);
  const [formData, setFormData] = useState({
    company_name: '',
    contact: '',
    country: '',
    seats: 0,
    payment_terms: '',
    experience: '',
    registration_time: '',
    response_time: '',
    rating: 0,
    last_contact_date: ''
  });

  const openEditModal = (p: Partner) => {
    setFormData({
      company_name: p.company_name || '',
      contact: p.contact || '',
      country: p.country || '',
      seats: p.seats || 0,
      payment_terms: p.payment_terms || '',
      experience: p.experience || '',
      registration_time: p.registration_time || '',
      response_time: p.response_time || '',
      rating: p.rating || 0,
      last_contact_date: p.last_contact_date || ''
    });
    setEditingId(p.id);
    setIsModalOpen(true);
  };
"""

content = content.replace(old_state, new_state)

# Modify handleCreate to handleUpdate
old_submit = """  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/partners/', formData);
      setIsModalOpen(false);
      setFormData({ 
        company_name: '', contact: '', country: '', seats: 0, 
        payment_terms: '', experience: '', registration_time: '', 
        response_time: '', rating: 0, last_contact_date: '' 
      });
      fetchPartners();
    } catch (err) {
      console.error(err);
      alert('Ошибка при создании партнера');
    }
  };"""

new_submit = """  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingId) {
        await api.put(`/partners/${editingId}`, formData);
      } else {
        await api.post('/partners/', formData);
      }
      setIsModalOpen(false);
      setEditingId(null);
      setFormData({ 
        company_name: '', contact: '', country: '', seats: 0, 
        payment_terms: '', experience: '', registration_time: '', 
        response_time: '', rating: 0, last_contact_date: '' 
      });
      fetchPartners();
    } catch (err) {
      console.error(err);
      alert('Ошибка при сохранении партнера');
    }
  };"""

content = content.replace(old_submit, new_submit)
content = content.replace("onSubmit={handleCreate}", "onSubmit={handleSubmit}")
content = content.replace("onClick={() => setIsModalOpen(true)}", "onClick={() => { setEditingId(null); setFormData({ company_name: '', contact: '', country: '', seats: 0, payment_terms: '', experience: '', registration_time: '', response_time: '', rating: 0, last_contact_date: '' }); setIsModalOpen(true); }}")
content = content.replace("Новый партнер", "{editingId ? 'Редактировать партнера' : 'Новый партнер'}")
content = content.replace(">Создать<", ">{editingId ? 'Сохранить' : 'Создать'}<")

# Add Edit button to table
old_td = """                    <td className="px-4 py-3 whitespace-nowrap text-right text-sm font-medium">
                      <button 
                        onClick={() => handleDelete(p.id)}
                        className="text-red-600 hover:text-red-900"
                      >
                        Удалить
                      </button>
                    </td>"""

new_td = """                    <td className="px-4 py-3 whitespace-nowrap text-right text-sm font-medium">
                      <button 
                        onClick={() => openEditModal(p)}
                        className="text-indigo-600 hover:text-indigo-900 mr-4"
                      >
                        Изменить
                      </button>
                      <button 
                        onClick={() => handleDelete(p.id)}
                        className="text-red-600 hover:text-red-900"
                      >
                        Удалить
                      </button>
                    </td>"""

content = content.replace(old_td, new_td)

with open("frontend/src/app/dashboard/partners/page.tsx", "w") as f:
    f.write(content)
