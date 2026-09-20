import re

with open('frontend/src/app/dashboard/workers/[id]/page.tsx', 'r') as f:
    content = f.read()

# Add state for history
if "const [history, setHistory]" not in content:
    content = content.replace(
        "const [loading, setLoading] = useState(true);",
        "const [loading, setLoading] = useState(true);\n  const [history, setHistory] = useState<{telegram: any[], email: any[]}>({telegram: [], email: []});"
    )
    
# Fetch history
if "api.get(`/workers/${id}/history`)" not in content:
    content = content.replace(
        "const { data } = await api.get(`/workers/${id}`);",
        "const { data } = await api.get(`/workers/${id}`);\n      const histRes = await api.get(`/workers/${id}/history`);\n      setHistory(histRes.data);"
    )

# Add History UI
history_ui = """
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">История аккаунтов</h3>
        
        <h4 className="text-md font-medium text-gray-700 mt-4 mb-2">Telegram</h4>
        {history.telegram.length === 0 ? <p className="text-sm text-gray-500">Нет истории</p> : (
          <div className="space-y-3">
            {history.telegram.map((h, i) => (
              <div key={i} className="flex justify-between text-sm p-3 bg-gray-50 rounded-lg">
                <div>
                  <span className="font-medium">Аккаунт ID: {h.account_id}</span>
                  <p className="text-gray-500 text-xs">Причина отвязки: {h.reason || 'Активен'}</p>
                </div>
                <div className="text-right">
                  <p className="text-gray-900">{new Date(h.assigned_at).toLocaleDateString()}</p>
                  <p className="text-gray-500 text-xs">{h.revoked_at ? new Date(h.revoked_at).toLocaleDateString() : 'По сей день'}</p>
                </div>
              </div>
            ))}
          </div>
        )}

        <h4 className="text-md font-medium text-gray-700 mt-6 mb-2">Email</h4>
        {history.email.length === 0 ? <p className="text-sm text-gray-500">Нет истории</p> : (
          <div className="space-y-3">
            {history.email.map((h, i) => (
              <div key={i} className="flex justify-between text-sm p-3 bg-gray-50 rounded-lg">
                <div>
                  <span className="font-medium">Аккаунт ID: {h.email_account_id}</span>
                  <p className="text-gray-500 text-xs">Причина отвязки: {h.reason || 'Активен'}</p>
                </div>
                <div className="text-right">
                  <p className="text-gray-900">{new Date(h.assigned_at).toLocaleDateString()}</p>
                  <p className="text-gray-500 text-xs">{h.revoked_at ? new Date(h.revoked_at).toLocaleDateString() : 'По сей день'}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
"""

if "История аккаунтов" not in content:
    content = content.replace(
        "return (",
        history_ui + "\n    return ("
    )
    # Move it into the actual render
    content = content.replace(
        history_ui + "\n    return (",
        "return ("
    )
    content = content.replace(
        "</div>\n    </div>\n  );",
        history_ui + "\n      </div>\n    </div>\n  );"
    )

with open('frontend/src/app/dashboard/workers/[id]/page.tsx', 'w') as f:
    f.write(content)
