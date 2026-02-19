"""
Project Fenrir: Activity Tracker Module
Theme: Fenrir / Wolf of the Black Knights
"""
import asyncio
import hikari
import datetime
from server import RoModules, Archives
from utils import logger

class ActivityTracker:
    def __init__(self, client: hikari.GatewayBot):
        self.client = client
        self.tracked_users = {} # user_id: {channel_id, last_status: str, last_game: str}
        self.log_collector = logger.AsyncLogCollector("logs/main.log")

    async def add_target(self, user_id: int, channel_id: int):
        """Starts tracking a user's activity."""
        self.tracked_users[user_id] = {
            'channel_id': channel_id,
            'last_status': None,
            'last_game': None
        }
        await self.log_collector.info(f"Fenrir is now tracking user {user_id}", initiator="ActivityTracker.add_target")

    async def tracker_loop(self):
        """Background loop to check for activity changes."""
        while True:
            await asyncio.sleep(300) # Check every 5 minutes
            for user_id, info in list(self.tracked_users.items()):
                try:
                    # Get profile and presence
                    profile = await RoModules.get_player_profile(user_id, 0)
                    presence_data = await RoModules.last_online(user_id, 0) # last_online returns status string in RoWhoIs
                    
                    current_status = presence_data
                    
                    if current_status != info['last_status']:
                        await self.report_activity(user_id, info['channel_id'], current_status)
                        self.tracked_users[user_id]['last_status'] = current_status
                        
                        # Also update Archives
                        await Archives.update_user(user_id, profile.username, current_status)
                        
                except Exception as e:
                    await self.log_collector.error(f"Fenrir error tracking {user_id}: {e}", initiator="ActivityTracker.tracker_loop")

    async def report_activity(self, user_id: int, channel_id: int, status: str):
        """Reports activity changes to Discord."""
        embed = hikari.Embed(title="FENRIR INTEL: Activity Update", color=0x990000)
        embed.description = f"Subject `{user_id}` has changed manifestation status."
        embed.add_field(name="Current Status", value=f"`{status}`", inline=True)
        embed.set_footer(text="The Wolf of Aegis never sleeps.")
        
        try:
            await self.client.rest.create_message(channel_id, embed=embed)
        except Exception:
            pass
