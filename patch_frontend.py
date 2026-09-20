with open("frontend/src/app/dashboard/telegram/page.tsx", "r") as f:
    content = f.read()

import re

# Update MediaWithAuth signature and body
old_media = """const MediaWithAuth = ({ accountId, chatId, messageId }: { accountId: number, chatId: string, messageId: number }) => {
  const [blobUrl, setBlobUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMedia = async () => {
      try {
        const res = await api.get(`/telegram/proxy/accounts/${accountId}/chats/${chatId}/messages/${messageId}/media`, {
          responseType: 'blob'
        });
        const url = URL.createObjectURL(res.data);
        setBlobUrl(url);
      } catch (err) {
        console.error("Failed to load media", err);
      } finally {
        setLoading(false);
      }
    };
    fetchMedia();
    return () => {
      if (blobUrl) URL.revokeObjectURL(blobUrl);
    };
  }, [accountId, chatId, messageId]);

  if (loading) return <div className="w-48 h-48 bg-gray-200 animate-pulse rounded-lg flex items-center justify-center text-gray-400 text-xs">Загрузка...</div>;
  if (!blobUrl) return <div className="text-xs text-muted-foreground italic">Медиа недоступно</div>;

  return <img src={blobUrl} alt="media" className="max-w-full h-auto rounded-lg mb-2" style={{ maxHeight: '300px' }} />;
};"""

new_media = """const MediaWithAuth = ({ accountId, chatId, messageId, mediaType }: { accountId: number, chatId: string, messageId: number, mediaType?: string }) => {
  const [blobUrl, setBlobUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMedia = async () => {
      try {
        const res = await api.get(`/telegram/proxy/accounts/${accountId}/chats/${chatId}/messages/${messageId}/media?type=${mediaType || ''}`, {
          responseType: 'blob'
        });
        const url = URL.createObjectURL(res.data);
        setBlobUrl(url);
      } catch (err) {
        console.error("Failed to load media", err);
      } finally {
        setLoading(false);
      }
    };
    fetchMedia();
    return () => {
      if (blobUrl) URL.revokeObjectURL(blobUrl);
    };
  }, [accountId, chatId, messageId, mediaType]);

  if (loading) return <div className="w-48 h-12 bg-gray-200 animate-pulse rounded-lg flex items-center justify-center text-gray-400 text-xs">Загрузка...</div>;
  if (!blobUrl) return <div className="text-xs text-muted-foreground italic">Медиа недоступно</div>;

  if (mediaType === "voice" || mediaType === "audio") {
    return <audio controls src={blobUrl} className="w-full max-w-[250px] mb-2" />;
  } else if (mediaType === "video") {
    return <video controls src={blobUrl} className="max-w-full h-auto rounded-lg mb-2" style={{ maxHeight: '300px' }} />;
  }
  return <img src={blobUrl} alt="media" className="max-w-full h-auto rounded-lg mb-2" style={{ maxHeight: '300px' }} />;
};"""

content = content.replace(old_media, new_media)

# Update where MediaWithAuth is called
old_render = """                      {msg.has_media && (
                        <MediaWithAuth accountId={selectedAccountId!} chatId={activeChat.id} messageId={msg.id} />
                      )}"""

new_render = """                      {msg.media_type && (
                        <MediaWithAuth accountId={selectedAccountId!} chatId={activeChat.id} messageId={msg.id} mediaType={msg.media_type} />
                      )}"""

content = content.replace(old_render, new_render)

with open("frontend/src/app/dashboard/telegram/page.tsx", "w") as f:
    f.write(content)
