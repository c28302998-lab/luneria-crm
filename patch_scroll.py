with open("frontend/src/app/dashboard/telegram/page.tsx", "r") as f:
    content = f.read()

import re

# We can replace the simple useEffect with one that tracks the previous last message ID
old_scroll = """  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);"""

new_scroll = """  const [lastMessageId, setLastMessageId] = useState<number | null>(null);
  
  useEffect(() => {
    if (messages.length > 0) {
      const currentLastId = messages[messages.length - 1].id;
      if (currentLastId !== lastMessageId) {
        setLastMessageId(currentLastId);
        if (messagesEndRef.current) {
          messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
        }
      }
    }
  }, [messages, lastMessageId]);"""

content = content.replace(old_scroll, new_scroll)

with open("frontend/src/app/dashboard/telegram/page.tsx", "w") as f:
    f.write(content)
