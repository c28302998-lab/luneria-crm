with open("src/app/dashboard/page.tsx", "r") as f:
    content = f.read()

widget = """
      {pendingShifts.length > 0 && user?.role !== 'CURATOR' && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-2xl p-6 shadow-sm mb-6">
          <div className="flex items-center mb-4 text-yellow-800">
            <Clock className="w-6 h-6 mr-2" />
            <h3 className="text-lg font-bold">Ожидают подтверждения смены</h3>
          </div>
          <div className="space-y-3">
            {pendingShifts.map(shift => (
              <div key={shift.id} className="flex justify-between items-center bg-white p-4 rounded-xl border border-yellow-100 shadow-sm">
                <div>
                  <div className="font-semibold text-foreground">Воркер #{shift.worker_id}</div>
                  <div className="text-sm text-muted-foreground">Запрашивает начало смены на {shift.date}</div>
                </div>
                <div className="flex gap-2">
                  <button onClick={() => handleVerifyShift(shift.id, true)} className="px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg font-medium transition-colors flex items-center">
                    <CheckCircle className="w-4 h-4 mr-1" /> Да, был
                  </button>
                  <button onClick={() => handleVerifyShift(shift.id, false)} className="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg font-medium transition-colors flex items-center">
                    <XCircle className="w-4 h-4 mr-1" /> Нет
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
"""
content = content.replace("<div className=\"grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4\">", widget + "\n      <div className=\"grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4\">")

with open("src/app/dashboard/page.tsx", "w") as f:
    f.write(content)
