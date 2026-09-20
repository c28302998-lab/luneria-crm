with open("backend/app/api/telegram_proxy.py", "r") as f:
    content = f.read()

old_resp = """        data = await telegram_manager.download_message_media(acc.id, peer_id, message_id)
        if not data:
            raise HTTPException(status_code=404, detail="Media not found or could not be downloaded")
        return Response(content=data)"""

new_resp = """        data = await telegram_manager.download_message_media(acc.id, peer_id, message_id)
        if not data:
            raise HTTPException(status_code=404, detail="Media not found or could not be downloaded")
        
        # We can guess content type based on URL parameter ?type=voice
        mt = "application/octet-stream"
        if request.query_params.get("type") == "voice":
            mt = "audio/ogg"
        elif request.query_params.get("type") == "photo":
            mt = "image/jpeg"
            
        return Response(content=data, media_type=mt)"""

content = content.replace(old_resp, new_resp)

with open("backend/app/api/telegram_proxy.py", "w") as f:
    f.write(content)
