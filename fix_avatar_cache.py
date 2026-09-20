import re

with open("backend/app/api/telegram_proxy.py", "r") as f:
    content = f.read()

old_cache_logic = """        if os.path.exists(cache_path):
            with open(cache_path, "rb") as f:
                data = f.read()
        else:
            data = await telegram_manager.get_profile_photo(account_id, entity_id)
            if data:
                with open(cache_path, "wb") as f:
                    f.write(data)
                    
        if data:
            from fastapi.responses import Response
            return Response(content=data, media_type="image/jpeg")
        return {"error": "No avatar"}"""

new_cache_logic = """        if os.path.exists(cache_path):
            with open(cache_path, "rb") as f:
                data = f.read()
            if not data:
                return {"error": "No avatar"}
        else:
            data = await telegram_manager.get_profile_photo(account_id, entity_id)
            with open(cache_path, "wb") as f:
                f.write(data if data else b"")
                
        if data:
            from fastapi.responses import Response
            return Response(content=data, media_type="image/jpeg")
        return {"error": "No avatar"}"""

content = content.replace(old_cache_logic, new_cache_logic)

with open("backend/app/api/telegram_proxy.py", "w") as f:
    f.write(content)
