from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument, DocumentAttributeAudio, DocumentAttributeVideo

def detect_media(m):
    media = getattr(m, 'media', None)
    if not media: return None
    
    if isinstance(media, MessageMediaPhoto):
        return "photo"
    elif isinstance(media, MessageMediaDocument):
        doc = media.document
        if hasattr(doc, 'attributes'):
            for attr in doc.attributes:
                if isinstance(attr, DocumentAttributeAudio):
                    return "voice" if getattr(attr, 'voice', False) else "audio"
                elif isinstance(attr, DocumentAttributeVideo):
                    return "video"
        return "document"
    return "other"
