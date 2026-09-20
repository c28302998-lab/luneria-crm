import re

with open('frontend/src/app/dashboard/workers/[id]/page.tsx', 'r') as f:
    content = f.read()

func_injection = """
  const handleLeave = async () => {
    if (!confirm('Вы уверены, что хотите уволить этого работника? Все его аккаунты будут отвязаны, и будут созданы ревью для аккаунтов.')) return;
    try {
      await api.post(`/workers/${id}/leave`);
      alert('Работник уволен. Аккаунты отвязаны.');
      window.location.reload();
    } catch (e: any) {
      alert(e.response?.data?.detail || 'Ошибка при увольнении');
    }
  };
"""
content = content.replace("const handleCreateAccount = async () => {", func_injection + "\n  const handleCreateAccount = async () => {")

button_html = """
          <button
            onClick={handleLeave}
            className="flex items-center px-4 py-2 bg-red-100 text-red-600 rounded-lg hover:bg-red-200 transition-colors"
          >
            <UserMinus className="w-5 h-5 mr-2" />
            Уволить
          </button>
"""
if "lucide-react';" in content:
    content = content.replace("lucide-react';", "UserMinus } from 'lucide-react';")
    content = content.replace("UserMinus, UserMinus", "UserMinus") # just in case

if "className=\"flex justify-between items-start" in content:
    content = content.replace(
        "className=\"flex justify-between items-start",
        "className=\"flex justify-between items-start"
    )
    # It's better to find where the action buttons are
    
    parts = content.split('className="flex justify-between items-start mb-6"')
    if len(parts) > 1:
        # inside the div there is probably a title and a div of buttons
        right_side = parts[1].split('</div>\n      </div>')
        new_right_side = right_side[0] + button_html
        content = parts[0] + 'className="flex justify-between items-start mb-6"' + new_right_side + '</div>\n      </div>' + right_side[1]

with open('frontend/src/app/dashboard/workers/[id]/page.tsx', 'w') as f:
    f.write(content)
