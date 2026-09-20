with open("src/app/dashboard/WorkerDashboard.tsx", "r") as f:
    content = f.read()

import re

imports_addition = """import { useState, useEffect } from 'react';
import { api } from '@/lib/api';"""

content = content.replace("import Link from 'next/link';", "import Link from 'next/link';\n" + imports_addition)

hooks = """  const { user } = useAuth();
  const [reports, setReports] = useState<any[]>([]);

  useEffect(() => {
    api.get('/shift-reports/').then(({data}) => setReports(data)).catch(console.error);
  }, []);
"""
content = content.replace("  const { user } = useAuth();", hooks)

reports_ui = """        </div>
      </div>
      
      <div className="bg-card rounded-2xl shadow-sm border border-border p-6 mt-8">
        <h3 className="text-xl font-bold mb-4">История отчетов</h3>
        <div className="space-y-3">
          {reports.length === 0 ? <p className="text-muted-foreground text-sm">Отчетов пока нет</p> : null}
          {reports.map((r) => (
            <div key={r.id} className="flex justify-between items-center p-3 bg-muted rounded-lg border border-border">
              <div>
                <div className="font-semibold text-sm">Отчет #{r.id}</div>
                <div className="text-xs text-muted-foreground">{new Date(r.created_at).toLocaleString('ru-RU')}</div>
              </div>
              <div className="flex items-center gap-3">
                <div className="font-bold">${r.amount}</div>
                <span className={`px-2 py-1 text-xs font-semibold rounded-full ${r.status === 'APPROVED' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                  {r.status === 'APPROVED' ? 'Одобрен' : 'В ожидании'}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );"""
content = content.replace("        </div>\n      </div>\n    </div>\n  );", reports_ui)

with open("src/app/dashboard/WorkerDashboard.tsx", "w") as f:
    f.write(content)
