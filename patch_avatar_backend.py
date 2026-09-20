import re

with open("backend/app/api/telegram_proxy.py", "r") as f:
    content = f.read()

# Make get_avatar public (or just remove the RoleChecker so img tags can load it)
# We can allow anonymous access to avatars, since they are public Telegram photos anyway.
# We will just depend on `db` to get it if needed, but actually we don't even need `db`.
# We'll just change `current_user: User = Depends(RoleChecker...` to `token: str = None` (or just remove it).

new_avatar_endpoint = """
import os
import hashlib

@router.get("/accounts/{account_id}/avatar/{entity_id}")
async def get_avatar(account_id: int, entity_id: int):
    try:
        cache_dir = "uploads/avatars"
        os.makedirs(cache_dir, exist_ok=True)
        cache_path = os.path.join(cache_dir, f"{account_id}_{entity_id}.jpg")
        
        if os.path.exists(cache_path):
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
        return {"error": "No avatar"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
"""

content = re.sub(r'@router\.get\("/accounts/\{account_id\}/avatar/\{entity_id\}"\).*?return \{"error": "No avatar"\}\n    except Exception as e:\n        raise HTTPException\(status_code=400, detail=str\(e\)\)', new_avatar_endpoint, content, flags=re.DOTALL)

with open("backend/app/api/telegram_proxy.py", "w") as f:
    f.write(content)
