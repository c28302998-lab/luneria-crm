import re

with open("frontend/src/app/dashboard/training/page.tsx", "r") as f:
    content = f.read()

# Add uploadingId state
content = content.replace(
    "const [loading, setLoading] = useState(true);",
    "const [loading, setLoading] = useState(true);\n  const [uploadingId, setUploadingId] = useState<number | null>(null);"
)

# Update handleFileUpload
new_upload = """  const handleFileUpload = async (materialId: number, file: File) => {
    setUploadingId(materialId);
    const fd = new FormData();
    fd.append('file', file);
    try {
      await api.post(`/materials/${materialId}/files`, fd, {
        headers: { 'Content-Type': undefined }
      });
      fetchMaterials();
    } catch (err) {
      alert('Ошибка загрузки файла');
    } finally {
      setUploadingId(null);
    }
  };"""

content = re.sub(
    r'  const handleFileUpload = async \(materialId: number, file: File\) => \{.*?  \};',
    new_upload,
    content,
    flags=re.DOTALL
)

# Update UI to show loading
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

with open("frontend/src/app/dashboard/training/page.tsx", "w") as f:
    f.write(content)
