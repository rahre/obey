"""
Sherlock Integration Module
Theme: Black Knights Intelligence Network
"""
import aiohttp
import asyncio

SITES = {
    "GitHub": "https://github.com/{}",
    "Roblox": "https://www.roblox.com/user.aspx?username={}",
    "Twitter": "https://twitter.com/{}",
    "Instagram": "https://www.instagram.com/{}/",
    "TikTok": "https://www.tiktok.com/@{}",
    "Reddit": "https://www.reddit.com/user/{}",
    "Twitch": "https://www.twitch.com/{}",
    "YouTube": "https://www.youtube.com/@{}"
}

async def check_site(session: aiohttp.ClientSession, platform: str, url_template: str, username: str) -> tuple:
    """Checks if a username exists on a specific platform."""
    url = url_template.format(username)
    try:
        async with session.get(url, timeout=5) as response:
            if response.status == 200:
                # Some sites return 200 even if user doesn't exist (need better logic for each, but this is a base)
                return platform, url, True
            return platform, url, False
    except Exception:
        return platform, url, False

async def scan_username(username: str):
    """Scans all supported sites for a username."""
    results = []
    async with aiohttp.ClientSession(headers={"User-Agent": "Mozilla/5.0"}) as session:
        tasks = [check_site(session, p, u, username) for p, u in SITES.items()]
        results = await asyncio.gather(*tasks)
    return results
吐
