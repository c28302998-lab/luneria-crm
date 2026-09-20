import re

with open("src/app/dashboard/worker-reports/page.tsx", "r") as f:
    content = f.read()

# Add handleDelete function
handle_delete_func = """
  const handleDelete = async (id: number) => {
    if (!confirm("Точно удалить этот отчет?")) return;
    try {
      await api.delete(`/shift-reports/${id}`);
      fetchReports();
    } catch (err) {
      alert("Ошибка при удалении");
    }
  };
"""
content = content.replace("const handleApprove =", handle_delete_func + "\n  const handleApprove =")

# Add Delete button in the table actions
old_approve_btn = """<button 
                            onClick={() => handleApprove(r.id)}
                            className="text-green-600 hover:text-green-800 flex items-center justify-end"
                          >
                            <Check className="h-4 w-4 mr-1" /> Подтвердить
                          </button>"""

new_approve_btn = """<div className="flex justify-end gap-3 mt-1">
                            <button 
                              onClick={() => handleDelete(r.id)}
                              className="text-red-500 hover:text-red-700 flex items-center text-xs"
                            >
                              <X className="h-4 w-4 mr-1" /> Удалить
                            </button>
                            <button 
                              onClick={() => handleApprove(r.id)}
                              className="text-green-600 hover:text-green-800 flex items-center text-xs"
                            >
                              <Check className="h-4 w-4 mr-1" /> Подтвердить
                            </button>
                          </div>"""

content = content.replace(old_approve_btn, new_approve_btn)

# Wait, what if the report is already APPROVED or REJECTED? Does the owner want to delete it then?
# Usually yes. So let's add a Delete button for ALL statuses if user is OWNER.
old_status_span = """{r.status === 'PENDING' && user?.role === 'ADMIN' && (
                        <span className="text-xs text-muted-foreground italic">Ожидает Овнера</span>
                      )}"""

new_status_span = """{r.status === 'PENDING' && user?.role === 'ADMIN' && (
                        <span className="text-xs text-muted-foreground italic">Ожидает Овнера</span>
                      )}
                      {r.status !== 'PENDING' && (user?.role === 'OWNER' || user?.role === 'FINANCE') && (
                        <button 
                          onClick={() => handleDelete(r.id)}
                          className="text-red-500 hover:text-red-700 flex items-center justify-end w-full text-xs mt-2"
                        >
                          <X className="h-3 w-3 mr-1" /> Удалить
                        </button>
                      )}"""
content = content.replace(old_status_span, new_status_span)

with open("src/app/dashboard/worker-reports/page.tsx", "w") as f:
    f.write(content)
