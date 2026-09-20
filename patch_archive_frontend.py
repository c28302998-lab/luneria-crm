with open("frontend/src/app/dashboard/telegram/page.tsx", "r") as f:
    content = f.read()

import re

# Add state
if "const [showArchived, setShowArchived] = useState(false);" not in content:
    content = content.replace(
        "const [activeChat, setActiveChat] = useState<any>(null);",
        "const [activeChat, setActiveChat] = useState<any>(null);\n  const [showArchived, setShowArchived] = useState(false);"
    )

# Add tabs under search bar
old_search = """          </div>
          {user?.role !== 'CANDIDATE' && ("""

new_search = """          </div>
          <div className="flex px-4 pb-2 gap-4 border-b border-border text-sm font-medium">
            <button 
              onClick={() => setShowArchived(false)} 
              className={`pb-2 ${!showArchived ? 'border-b-2 border-primary text-primary' : 'text-muted-foreground'}`}
            >
              Все чаты
            </button>
            <button 
              onClick={() => setShowArchived(true)} 
              className={`pb-2 ${showArchived ? 'border-b-2 border-primary text-primary' : 'text-muted-foreground'}`}
            >
              Архив
            </button>
          </div>
          {user?.role !== 'CANDIDATE' && ("""

content = content.replace(old_search, new_search)

# Filter chats
old_map = "            chats.map(chat => ("
new_map = "            chats.filter(c => !!c.archived === showArchived).map(chat => ("

content = content.replace(old_map, new_map)

with open("frontend/src/app/dashboard/telegram/page.tsx", "w") as f:
    f.write(content)
