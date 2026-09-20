import re

with open('frontend/src/app/dashboard/shifts/page.tsx', 'r') as f:
    content = f.read()

new_approve = """
  const handleApprove = async (shift: any) => {
    let workerAmount = 0;
    let adminAmount = 0;
    
    const baseAmount = shift.stats?.balance || 0;
    
    const workerInput = prompt(`Подтверждение смены #${shift.id}\\nЗаработок воркера (изначально ${baseAmount}):`, String(baseAmount * 0.20));
    if (workerInput === null) return;
    workerAmount = parseFloat(workerInput) || 0;
    
    const adminInput = prompt(`Заработок куратора/админа (изначально ${baseAmount}):`, String(baseAmount * 0.05));
    if (adminInput === null) return;
    adminAmount = parseFloat(adminInput) || 0;
    
    try {
      await api.post(`/shifts/${shift.id}/approve`, {
        worker_amount: workerAmount,
        admin_amount: adminAmount
      });
      alert('Смена одобрена');
      fetchShifts();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка');
    }
  };
"""

content = content.replace("const handleApprove = async (id: number) => {", new_approve + "\n  const handleApproveOLD = async (id: number) => {")
content = content.replace("handleApprove(shift.id)", "handleApprove(shift)")

with open('frontend/src/app/dashboard/shifts/page.tsx', 'w') as f:
    f.write(content)
