import re

with open("frontend/src/app/dashboard/telegram/page.tsx", "r") as f:
    content = f.read()

old_media = """  if (mediaType === "voice" || mediaType === "audio") {
    return <audio controls src={blobUrl} className="w-full max-w-[250px] mb-2" />;
  } else if (mediaType === "video") {
    return <video controls src={blobUrl} className="max-w-full h-auto rounded-lg mb-2" style={{ maxHeight: '300px' }} />;
  }
  return <img src={blobUrl} alt="media" className="max-w-full h-auto rounded-lg mb-2" style={{ maxHeight: '300px' }} />;"""

new_media = """  if (mediaType === "voice" || mediaType === "audio") {
    return <audio controls src={blobUrl} className="w-full max-w-[250px] mb-2" />;
  } else if (mediaType === "video") {
    return <video controls src={blobUrl} className="max-w-full h-auto rounded-lg mb-2" style={{ maxHeight: '300px' }} />;
  } else if (mediaType === "document") {
    return (
      <a href={blobUrl} download={`document_${messageId}`} className="flex items-center p-3 bg-primary/10 rounded-lg text-primary hover:bg-primary/20 transition mb-2 w-fit">
        <FileText className="w-4 h-4 mr-2" />
        <span className="text-sm font-medium">Скачать файл</span>
      </a>
    );
  }
  return <img src={blobUrl} alt="media" className="max-w-full h-auto rounded-lg mb-2" style={{ maxHeight: '300px' }} />;"""

content = content.replace(old_media, new_media)

with open("frontend/src/app/dashboard/telegram/page.tsx", "w") as f:
    f.write(content)
