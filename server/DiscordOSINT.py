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
    except Exception:
        return None

def find_discord_in_bio(bio: str) -> list[str]:
    """Scans a text for Discord invites or usernames."""
    import re
    # Patterns for discord.gg/code and username#1234
    invite_pattern = r"(?:https?://)?(?:www\.)?(?:discord\.(?:gg|io|me|li)|discord(?:app)?\.com/invite)/([a-zA-Z0-9]+)"
    
    # Simple tag pattern (Note: Discord uses unique usernames now, so tags are legacy/display names)
    # matching "name#1234"
    legacy_tag_pattern = r"(\b\w+#\d{4}\b)"
    
    # New username pattern (just word characters, strict to avoid false positives)
    # We look for "Discord: name" or "dc: name"
    username_pattern = r"(?:Discord|dc|disc|tag):\s*([a-z0-9_.]+)"

    invites = re.findall(invite_pattern, bio)
    tags = re.findall(legacy_tag_pattern, bio)
    usernames = re.findall(username_pattern, bio, re.IGNORECASE)

    results = []
    if invites: results.extend([f"Invite: {code}" for code in invites])
    if tags: results.extend([f"Legacy Tag: {tag}" for tag in tags])
    if usernames: results.extend([f"Username: {name}" for name in usernames])
    
    return list(set(results))
