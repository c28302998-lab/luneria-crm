with open('frontend/src/app/dashboard/workers/[id]/page.tsx', 'r') as f:
    content = f.read()

history_ui = """
      <div className="bg-card rounded-xl shadow-sm border border-border p-6 mt-6">
        <h3 className="text-lg font-medium text-foreground mb-4">История аккаунтов</h3>
        
        <h4 className="text-md font-medium text-muted-foreground mt-4 mb-2">Telegram</h4>
        {!history.telegram || history.telegram.length === 0 ? <p className="text-sm text-muted-foreground">Нет истории</p> : (
          <div className="space-y-3">
            {history.telegram.map((h: any, i: number) => (
              <div key={i} className="flex justify-between text-sm p-3 bg-muted rounded-lg">
                <div>
                  <span className="font-medium text-foreground">Аккаунт ID: {h.account_id}</span>
                  <p className="text-muted-foreground text-xs">Причина отвязки: {h.reason || 'Активен'}</p>
                </div>
                <div className="text-right">
                  <p className="text-foreground">{new Date(h.assigned_at).toLocaleDateString()}</p>
                  <p className="text-muted-foreground text-xs">{h.revoked_at ? new Date(h.revoked_at).toLocaleDateString() : 'По сей день'}</p>
                </div>
              </div>
            ))}
          </div>
        )}

        <h4 className="text-md font-medium text-muted-foreground mt-6 mb-2">Email</h4>
        {!history.email || history.email.length === 0 ? <p className="text-sm text-muted-foreground">Нет истории</p> : (
          <div className="space-y-3">
            {history.email.map((h: any, i: number) => (
              <div key={i} className="flex justify-between text-sm p-3 bg-muted rounded-lg">
                <div>
                  <span className="font-medium text-foreground">Аккаунт ID: {h.email_account_id}</span>
                  <p className="text-muted-foreground text-xs">Причина отвязки: {h.reason || 'Активен'}</p>
                </div>
                <div className="text-right">
                  <p className="text-foreground">{new Date(h.assigned_at).toLocaleDateString()}</p>
                  <p className="text-muted-foreground text-xs">{h.revoked_at ? new Date(h.revoked_at).toLocaleDateString() : 'По сей день'}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
"""

content = content.replace("{showFineModal && (", history_ui + "\n      {showFineModal && (")

with open('frontend/src/app/dashboard/workers/[id]/page.tsx', 'w') as f:
    f.write(content)
