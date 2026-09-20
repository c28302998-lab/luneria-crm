with open("frontend/src/app/dashboard/reports/page.tsx", "r") as f:
    content = f.read()

import re

# Add handleDelete function
if "const handleDelete =" not in content:
    old_fetch = "  const fetchReports = async () => {"
    new_func = """  const handleDelete = async (id: number) => {
    if (!confirm("Точно удалить этот отчет?")) return;
    try {
      await api.delete(`/reports/${id}`);
      fetchReports();
    } catch (e) {
      alert("Ошибка при удалении");
    }
  };

  const fetchReports = async () => {"""
    content = content.replace(old_fetch, new_func)

# Add X icon to imports
if "Trash2" not in content:
    content = content.replace("FileText, Download", "FileText, Download, Trash2")

# Add Delete button to UI
old_ui = """                    <button onClick={() => handleDownload(r)} className="text-primary hover:text-indigo-900 text-xs flex items-center">
                      <Download className="w-3 h-3 mr-1" /> Скачать
                    </button>"""
new_ui = """                    <button onClick={() => handleDownload(r)} className="text-primary hover:text-indigo-900 text-xs flex items-center">
                      <Download className="w-3 h-3 mr-1" /> Скачать
                    </button>
                    {(user?.role === 'OWNER' || user?.role === 'ADMIN') && (
                      <button onClick={() => handleDelete(r.id)} className="text-red-500 hover:text-red-700 text-xs flex items-center mt-2">
                        <Trash2 className="w-3 h-3 mr-1" /> Удалить
                      </button>
                    )}"""
content = content.replace(old_ui, new_ui)

with open("frontend/src/app/dashboard/reports/page.tsx", "w") as f:
    f.write(content)
