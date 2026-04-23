import httpx
import logging
import config


async def get_latest_battleroom() -> dict | None:
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{config.API_BASE_URL}/battleroom/latest",
                headers={"X-Admin-Key": config.ADMIN_KEY},
                timeout=5.0,
            )
        if r.status_code == 404:
            return None
        return r.json()
    except httpx.HTTPError as e:
        logging.error("get_latest_battleroom failed: %s", e)
        return None


async def battleroom_enter(battleroom_id: int, username: str) -> dict | None:
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{config.API_BASE_URL}/battleroom/enter",
                json={"battleroom_id": battleroom_id, "username": username},
                headers={"X-Admin-Key": config.ADMIN_KEY},
                timeout=5.0,
            )
        return {"status": r.status_code, "body": r.json()}
    except httpx.HTTPError as e:
        logging.error("battleroom_enter failed for user %s: %s", username, e)
        return None
