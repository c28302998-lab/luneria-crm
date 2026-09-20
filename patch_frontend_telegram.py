import re

with open("frontend/src/app/dashboard/telegram/page.tsx", "r") as f:
    content = f.read()

# 1. Add states
state_insertion = """  const [searchQuery, setSearchQuery] = useState('');
  const [globalSearchResult, setGlobalSearchResult] = useState<any>(null);
  const [searchingGlobal, setSearchingGlobal] = useState(false);
"""
content = content.replace("  const [showArchived, setShowArchived] = useState(false);", "  const [showArchived, setShowArchived] = useState(false);\n" + state_insertion)

# 2. Add global search handler
search_handler = """
  const handleGlobalSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!searchQuery.trim() || !selectedAccountId) return;
    setSearchingGlobal(true);
    setGlobalSearchResult(null);
    try {
      const { data } = await api.get(`/telegram/proxy/resolve?account_id=${selectedAccountId}&query=${encodeURIComponent(searchQuery)}`);
      setGlobalSearchResult(data);
    } catch (err: any) {
      alert("Не найдено: " + (err.response?.data?.detail || err.message));
    } finally {
      setSearchingGlobal(false);
    }
  };
"""
content = content.replace("  const fetchMyAccounts = async () => {", search_handler + "\n  const fetchMyAccounts = async () => {")

# 3. Modify search input
old_search_input = """          <div className="relative flex-1">
            <input 
              type="text" 
              placeholder="Поиск..." 
              className="w-full bg-muted rounded-full py-1.5 pl-10 pr-4 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
            />
            <Search className="w-4 h-4 text-gray-400 absolute left-3 top-2" />
          </div>"""
new_search_input = """          <form onSubmit={handleGlobalSearch} className="relative flex-1 flex gap-2">
            <div className="relative flex-1">
              <input 
                type="text" 
                placeholder="Поиск чатов или @username..." 
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                className="w-full bg-muted rounded-full py-1.5 pl-10 pr-4 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
              />
              <Search className="w-4 h-4 text-gray-400 absolute left-3 top-2" />
            </div>
            <button type="submit" disabled={searchingGlobal || !searchQuery} className="text-xs bg-primary text-white px-3 rounded-full hover:bg-primary/90 disabled:opacity-50">
              {searchingGlobal ? '...' : 'Найти'}
            </button>
          </form>"""
content = content.replace(old_search_input, new_search_input)

# 4. Filter local chats
old_chat_filter = "chats.filter(c => !!c.archived === showArchived).map(chat => ("
new_chat_filter = """chats
              .filter(c => !!c.archived === showArchived)
              .filter(c => !searchQuery || (c.name || '').toLowerCase().includes(searchQuery.toLowerCase()))
              .map(chat => ("""
content = content.replace(old_chat_filter, new_chat_filter)

# 5. Insert global search result above chats
global_search_ui = """
          {globalSearchResult && (
            <div className="mb-2 p-2 border-b border-border bg-indigo-50/50">
              <p className="text-xs font-semibold text-indigo-800 mb-1 px-2 uppercase tracking-wider">Глобальный поиск</p>
              <div 
                onClick={() => { setActiveChat(globalSearchResult); setGlobalSearchResult(null); setSearchQuery(''); }}
                className="flex items-center gap-3 p-3 cursor-pointer hover:bg-background rounded-lg transition"
              >
                <img src={`https://lunery-backend.onrender.com/api/v1/telegram/proxy/accounts/${selectedAccountId}/avatar/${globalSearchResult.id}`} onError={(e) => { e.currentTarget.style.display = 'none'; e.currentTarget.nextElementSibling!.classList.remove('hidden') }} className="w-12 h-12 rounded-full object-cover" />
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-indigo-400 to-purple-500 hidden flex-shrink-0 flex items-center justify-center text-white font-medium">
                  {globalSearchResult.name ? globalSearchResult.name.charAt(0).toUpperCase() : '?'}
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-medium text-foreground truncate">{globalSearchResult.name}</h3>
                  <p className="text-sm text-muted-foreground truncate">@{globalSearchResult.username || '—'}</p>
                </div>
              </div>
            </div>
          )}
"""
content = content.replace("{loadingChats ? (", global_search_ui + "\n          {loadingChats ? (")

# 6. Add avatars to existing chats list
old_avatar = """                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-indigo-400 to-purple-500 flex-shrink-0 flex items-center justify-center text-white font-medium">
                  {chat.name ? chat.name.charAt(0).toUpperCase() : '?'}
                </div>"""
new_avatar = """                <img src={`https://lunery-backend.onrender.com/api/v1/telegram/proxy/accounts/${selectedAccountId}/avatar/${chat.id}`} onError={(e) => { e.currentTarget.style.display = 'none'; e.currentTarget.nextElementSibling!.classList.remove('hidden') }} className="w-12 h-12 rounded-full object-cover flex-shrink-0" />
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-indigo-400 to-purple-500 hidden flex-shrink-0 flex items-center justify-center text-white font-medium">
                  {chat.name ? chat.name.charAt(0).toUpperCase() : '?'}
                </div>"""
content = content.replace(old_avatar, new_avatar)

# 7. Add avatar to active chat header
old_header_avatar = """                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-400 to-purple-500 flex items-center justify-center text-white font-medium">
                  {activeChat.name ? activeChat.name.charAt(0).toUpperCase() : '?'}
                </div>"""
new_header_avatar = """                <img src={`https://lunery-backend.onrender.com/api/v1/telegram/proxy/accounts/${selectedAccountId}/avatar/${activeChat.id}`} onError={(e) => { e.currentTarget.style.display = 'none'; e.currentTarget.nextElementSibling!.classList.remove('hidden') }} className="w-10 h-10 rounded-full object-cover flex-shrink-0" />
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-400 to-purple-500 hidden flex items-center justify-center text-white font-medium">
                  {activeChat.name ? activeChat.name.charAt(0).toUpperCase() : '?'}
                </div>"""
content = content.replace(old_header_avatar, new_header_avatar)


with open("frontend/src/app/dashboard/telegram/page.tsx", "w") as f:
    f.write(content)
