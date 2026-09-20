import re

with open('frontend/src/app/dashboard/workers/[id]/page.tsx', 'r') as f:
    content = f.read()

button_html = """
            <div className="mt-4">
              <button
                onClick={handleLeave}
                className="flex items-center px-4 py-2 bg-red-100 text-red-600 rounded-lg hover:bg-red-200 transition-colors text-sm font-medium"
              >
                <UserMinus className="w-4 h-4 mr-2" />
                Уволить воркера (отвязать аккаунты)
              </button>
            </div>
"""

content = content.replace('<Key className="w-4 h-4 mr-1" /> Worker ID #{worker.id}\n            </div>', '<Key className="w-4 h-4 mr-1" /> Worker ID #{worker.id}\n            </div>' + button_html)

with open('frontend/src/app/dashboard/workers/[id]/page.tsx', 'w') as f:
    f.write(content)
