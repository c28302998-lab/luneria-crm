import re

with open("frontend/src/app/dashboard/finance/page.tsx", "r") as f:
    content = f.read()

# Add states
content = content.replace(
    "const [isExpenseModalOpen, setIsExpenseModalOpen] = useState(false);",
    "const [isExpenseModalOpen, setIsExpenseModalOpen] = useState(false);\n  const [uploadingPaymentId, setUploadingPaymentId] = useState<number | null>(null);\n  const [uploadingExpenseId, setUploadingExpenseId] = useState<number | null>(null);"
)

# Update handlePaymentFileUpload
new_payment_upload = """  const handlePaymentFileUpload = async (id: number, file: File) => {
    setUploadingPaymentId(id);
    const formData = new FormData();
    formData.append('file', file);
    try {
      await api.post(`/payments/${id}/files`, formData, { headers: { 'Content-Type': undefined } });
      fetchData();
    } catch (err) { alert('Ошибка при загрузке чека'); } finally { setUploadingPaymentId(null); }
  };"""

content = re.sub(
    r'  const handlePaymentFileUpload = async \(id: number, file: File\) => \{.*?  \};',
    new_payment_upload,
    content,
    flags=re.DOTALL
)

# Update handleExpenseFileUpload
new_expense_upload = """  const handleExpenseFileUpload = async (id: number, file: File) => {
    setUploadingExpenseId(id);
    const formData = new FormData();
    formData.append('file', file);
    try {
      await api.post(`/payments/expenses/${id}/files`, formData, { headers: { 'Content-Type': undefined } });
      fetchData();
    } catch (err) { alert('Ошибка при загрузке чека'); } finally { setUploadingExpenseId(null); }
  };"""

content = re.sub(
    r'  const handleExpenseFileUpload = async \(id: number, file: File\) => \{.*?  \};',
    new_expense_upload,
    content,
    flags=re.DOTALL
)

# Update Payment row UI
old_payment_ui = """                              <label className="cursor-pointer text-primary hover:text-indigo-900 flex items-center">
                                <Upload className="w-4 h-4 mr-1" /> Загрузить
                                <input type="file" className="hidden" onChange={(ev) => {
                                  if(ev.target.files && ev.target.files[0]) handlePaymentFileUpload(p.id, ev.target.files[0]);
                                }} />
                              </label>"""

new_payment_ui = """                              {uploadingPaymentId === p.id ? (
                                <span className="text-primary flex items-center text-xs"><span className="animate-spin rounded-full h-3 w-3 border-b-2 border-primary mr-1"></span> Загрузка...</span>
                              ) : (
                                <label className="cursor-pointer text-primary hover:text-indigo-900 flex items-center">
                                  <Upload className="w-4 h-4 mr-1" /> Загрузить
                                  <input type="file" className="hidden" onChange={(ev) => {
                                    if(ev.target.files && ev.target.files[0]) handlePaymentFileUpload(p.id, ev.target.files[0]);
                                  }} />
                                </label>
                              )}"""

content = content.replace(old_payment_ui, new_payment_ui)


# Update Expense row UI
old_expense_ui = """                              <label className="cursor-pointer text-primary hover:text-indigo-900 flex items-center">
                                <Upload className="w-4 h-4 mr-1" /> Загрузить
                                <input type="file" className="hidden" onChange={(ev) => {
                                  if(ev.target.files && ev.target.files[0]) handleExpenseFileUpload(e.id, ev.target.files[0]);
                                }} />
                              </label>"""

new_expense_ui = """                              {uploadingExpenseId === e.id ? (
                                <span className="text-primary flex items-center text-xs"><span className="animate-spin rounded-full h-3 w-3 border-b-2 border-primary mr-1"></span> Загрузка...</span>
                              ) : (
                                <label className="cursor-pointer text-primary hover:text-indigo-900 flex items-center">
                                  <Upload className="w-4 h-4 mr-1" /> Загрузить
                                  <input type="file" className="hidden" onChange={(ev) => {
                                    if(ev.target.files && ev.target.files[0]) handleExpenseFileUpload(e.id, ev.target.files[0]);
                                  }} />
                                </label>
                              )}"""

content = content.replace(old_expense_ui, new_expense_ui)

with open("frontend/src/app/dashboard/finance/page.tsx", "w") as f:
    f.write(content)
