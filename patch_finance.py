import re

with open("frontend/src/app/dashboard/finance/page.tsx", "r") as f:
    content = f.read()

# 1. Table Headers
content = re.sub(
    r'<th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Общая Сумма</th>\s*<th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Доля Компании</th>\s*<th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Работнику</th>\s*<th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Админу</th>',
    '<th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase">Прибыль Компании</th>',
    content
)

# 2. Table Rows
content = re.sub(
    r'<td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-foreground">\$\{p\.amount\}</td>\s*<td className="px-6 py-4 whitespace-nowrap text-sm text-green-600 font-semibold">\$\{p\.amount_company\}</td>\s*<td className="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground">\$\{p\.amount_worker\}</td>\s*<td className="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground">\$\{p\.amount_admin\}</td>',
    '<td className="px-6 py-4 whitespace-nowrap text-sm text-green-600 font-semibold">${p.amount_company}</td>',
    content
)

# 3. Colspan fallback
content = re.sub(r'colSpan=\{6\}', 'colSpan={4}', content)

# 4. Form Submission
content = re.sub(
    r'amount: parseFloat\(paymentData\.amount\) \|\| 0,',
    'amount: parseFloat(paymentData.amount_company) || 0,',
    content
)

# 5. Form UI
old_form_ui = """              <div>
                <label className="block text-sm font-medium text-gray-700">Общая сумма прибыли ($)</label>
                <input 
                  type="number" required step="0.01"
                  value={paymentData.amount}
                  onChange={(e) => setPaymentData({...paymentData, amount: e.target.value})}
                  className="mt-1 block w-full rounded-md border-gray-300 border p-2 text-sm focus:border-indigo-500 focus:outline-none" 
                />
              </div>
              <div className="grid grid-cols-3 gap-4 border-t pt-4 mt-2">
                <div>
                  <label className="block text-xs font-medium text-gray-700">Доля Компании (Наша)</label>
                  <input 
                    type="number" required step="0.01"
                    value={paymentData.amount_company}
                    onChange={(e) => setPaymentData({...paymentData, amount_company: e.target.value})}
                    className="mt-1 block w-full rounded-md border-gray-300 border p-2 text-sm text-green-700 bg-green-50" 
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-700">Доля Работника</label>
                  <input 
                    type="number" required step="0.01"
                    value={paymentData.amount_worker}
                    onChange={(e) => setPaymentData({...paymentData, amount_worker: e.target.value})}
                    className="mt-1 block w-full rounded-md border-gray-300 border p-2 text-sm" 
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-700">Доля Админа</label>
                  <input 
                    type="number" required step="0.01"
                    value={paymentData.amount_admin}
                    onChange={(e) => setPaymentData({...paymentData, amount_admin: e.target.value})}
                    className="mt-1 block w-full rounded-md border-gray-300 border p-2 text-sm" 
                  />
                </div>
              </div>"""

new_form_ui = """              <div>
                <label className="block text-sm font-medium text-gray-700">Прибыль Компании ($)</label>
                <input 
                  type="number" required step="0.01"
                  value={paymentData.amount_company}
                  onChange={(e) => setPaymentData({...paymentData, amount_company: e.target.value})}
                  className="mt-1 block w-full rounded-md border-gray-300 border p-2 text-sm text-green-700 bg-green-50 focus:border-indigo-500 focus:outline-none" 
                />
              </div>"""

content = content.replace(old_form_ui, new_form_ui)

with open("frontend/src/app/dashboard/finance/page.tsx", "w") as f:
    f.write(content)
