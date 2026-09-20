import re

with open("frontend/src/app/dashboard/training/page.tsx", "r") as f:
    content = f.read()

# Add isSubmitting state
content = content.replace(
    "const [uploadingId, setUploadingId] = useState<number | null>(null);",
    "const [uploadingId, setUploadingId] = useState<number | null>(null);\n  const [isSubmitting, setIsSubmitting] = useState(false);"
)

# Update handleCreate
new_create = """  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      const res = await api.post('/materials/', formData);
      const newMaterialId = res.data.id;
      
      for (const file of selectedFiles) {
        const fd = new FormData();
        fd.append('file', file);
        await api.post(`/materials/${newMaterialId}/files`, fd, {
          headers: { 'Content-Type': undefined }
        });
      }

      setIsModalOpen(false);
      setFormData({ title: '', content: '' });
      setSelectedFiles([]);
      fetchMaterials();
    } catch (err) {
      alert('Ошибка при создании материала');
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };"""

content = re.sub(
    r'  const handleCreate = async \(e: React\.FormEvent\) => \{.*?  \};',
    new_create,
    content,
    flags=re.DOTALL
)

# Update submit button
new_button = """                <button type="submit" disabled={isSubmitting} className="px-4 py-2 bg-indigo-600 border border-transparent rounded-md text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50 flex items-center">
                  {isSubmitting ? (
                    <><span className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></span> Загрузка...</>
                  ) : "Создать материал"}
                </button>"""

content = re.sub(
    r'                <button type="submit" className="px-4 py-2 bg-indigo-600 border border-transparent rounded-md text-sm font-medium text-white hover:bg-indigo-700">Создать материал</button>',
    new_button,
    content
)

with open("frontend/src/app/dashboard/training/page.tsx", "w") as f:
    f.write(content)
