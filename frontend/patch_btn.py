with open("src/app/dashboard/workers/[id]/page.tsx", "r") as f:
    content = f.read()

import re

old_block = """            {userAccount ? (
              <p className="text-xs text-pink-200 mt-4">ID Аккаунта: {userAccount.id}</p>
            ) : (
              <div className="mt-4 flex flex-col items-center">
                <p className="text-xs text-yellow-200 mb-2">Системный аккаунт еще не создан</p>
                <button onClick={handleCreateAccount} className="text-xs bg-white text-purple-700 px-3 py-1.5 rounded-full font-bold shadow-sm hover:bg-pink-50 transition-colors flex items-center">
                  <Key className="w-3 h-3 mr-1" /> Выдать доступ в CRM
                </button>
              </div>
            )}"""

new_block = """            {userAccount ? (
              <div className="mt-4 flex flex-col items-center">
                <button onClick={handleCreateAccount} className="text-xs bg-white/20 hover:bg-white/30 text-white px-3 py-1.5 rounded-full font-bold transition-colors flex items-center border border-white/30">
                  <Key className="w-3 h-3 mr-1" /> Сбросить пароль (Показать)
                </button>
              </div>
            ) : (
              <div className="mt-4 flex flex-col items-center">
                <p className="text-xs text-yellow-200 mb-2">Системный аккаунт еще не создан</p>
                <button onClick={handleCreateAccount} className="text-xs bg-white text-purple-700 px-3 py-1.5 rounded-full font-bold shadow-sm hover:bg-pink-50 transition-colors flex items-center">
                  <Key className="w-3 h-3 mr-1" /> Выдать доступ в CRM
                </button>
              </div>
            )}"""

content = content.replace(old_block, new_block)

with open("src/app/dashboard/workers/[id]/page.tsx", "w") as f:
    f.write(content)
