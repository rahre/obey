"""
Discord OSINT Module for Aegis (Aegis-OSINT)
Theme: Eye of Geass / Zero
"""
import hikari
import datetime
from typing import Optional

async def get_user_info(client: hikari.GatewayBot, user_id: int) -> Optional[dict]:
    """Fetches detailed information about a Discord user."""
    try:
        user = await client.rest.fetch_user(user_id)
        if not user:
            return None
        
        # Calculate account age
        created_at = user.created_at
        now = datetime.datetime.now(datetime.timezone.utc)
        age = now - created_at
        
        # Flags mapping (simplified)
        flags = []
        if user.flags:
            for flag in hikari.UserFlag:
                if user.flags & flag:
                    flags.append(str(flag).split('.')[-1])

        return {
            "id": user.id,
            "username": user.username,
            "discriminator": user.discriminator,
            "global_name": user.global_name,
            "created_at": created_at,
            "age_days": age.days,
            "avatar_url": user.avatar_url or user.default_avatar_url,
            "banner_url": user.banner_url,
            "accent_color": user.accent_color,
            "is_bot": user.is_bot,
            "flags": flags
        }
    except hikari.errors.NotFoundError:
        return None
    except Exception:
        return None
