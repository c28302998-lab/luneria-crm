import re

with open("frontend/src/app/dashboard/sources/page.tsx", "r") as f:
    content = f.read()

# Add isSubmitting and uploadingId state
content = content.replace(
    "const [expandedId, setExpandedId] = useState<number | null>(null);",
    "const [expandedId, setExpandedId] = useState<number | null>(null);\n  const [isSubmitting, setIsSubmitting] = useState(false);\n  const [uploadingId, setUploadingId] = useState<number | null>(null);"
)

# Update handleCreate
new_create = """  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      const res = await api.post('/sources/', formData);
      const newSourceId = res.data.id;
      
      for (const file of selectedFiles) {
        const fd = new FormData();
        fd.append('file', file);
        await api.post(`/sources/${newSourceId}/files`, fd, {
          headers: { 'Content-Type': undefined }
        });
      }

      setIsModalOpen(false);
      setFormData({ title: '', content: '' });
      setSelectedFiles([]);
      fetchSources();
    } catch (err) {
      alert('Ошибка при создании источника');
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

# Update handleFileUpload
new_upload = """  const handleFileUpload = async (sourceId: number, file: File) => {
    setUploadingId(sourceId);
    const fd = new FormData();
    fd.append('file', file);
    try {
      await api.post(`/sources/${sourceId}/files`, fd, {
        headers: { 'Content-Type': undefined }
      });
      fetchSources();
    } catch (err) {
      alert('Ошибка загрузки файла');
    } finally {
      setUploadingId(null);
    }
  };"""

content = re.sub(
    r'  const handleFileUpload = async \(sourceId: number, file: File\) => \{.*?  \};',
    new_upload,
    content,
    flags=re.DOTALL
)

# Update modal submit button
new_button = """                <button type="submit" disabled={isSubmitting} className="px-4 py-2 bg-indigo-600 border border-transparent rounded-md text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50 flex items-center">
                  {isSubmitting ? (
                    <><span className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></span> Создание...</>
                  ) : "Создать источник"}
                </button>"""

content = re.sub(
    r'                <button type="submit" className="px-4 py-2 bg-indigo-600 border border-transparent rounded-md text-sm font-medium text-white hover:bg-indigo-700">Создать источник</button>',
    new_button,
    content
)

# Update list upload button
new_ui = """                      <div>
                        {uploadingId === m.id ? (
                          <div className="flex items-center px-3 py-1.5 text-indigo-700 text-xs font-medium">
                            <span className="animate-spin rounded-full h-3 w-3 border-b-2 border-indigo-700 mr-1.5"></span>
                            Загрузка...
                          </div>
                        ) : (
                          <label className="flex items-center px-3 py-1.5 border border-indigo-200 text-indigo-700 rounded-md text-xs font-medium cursor-pointer hover:bg-primary/10">
                            <Upload className="h-3 w-3 mr-1.5" />
                            Прикрепить файл
                            <input 
                              type="file" 
                              className="hidden" 
                              onChange={(e) => {
                                if (e.target.files && e.target.files[0]) {
                                  handleFileUpload(m.id, e.target.files[0]);
                                }
                              }}
                            />
                          </label>
                        )}
                      </div>"""

content = re.sub(
    r'                      <div>\s*<label className="flex items-center px-3 py-1\.5 border border-indigo-200 text-indigo-700 rounded-md text-xs font-medium cursor-pointer hover:bg-primary/10">\s*<Upload className="h-3 w-3 mr-1\.5" />\s*Прикрепить файл\s*<input \s*type="file" \s*className="hidden" \s*onChange=\{\(e\) => \{\s*if \(e\.target\.files && e\.target\.files\[0\]\) \{\s*handleFileUpload\(m\.id, e\.target\.files\[0\]\);\s*\}\s*\}\}\s*/>\s*</label>\s*</div>',
    new_ui,
    content
)

with open("frontend/src/app/dashboard/sources/page.tsx", "w") as f:
    f.write(content)
