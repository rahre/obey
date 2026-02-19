"""
Roblox Group Spy Module
Theme: Black Knights
"""
import asyncio
import hikari
from server import RoModules, Roquest
from utils import logger

class GroupSpy:
    def __init__(self, client: hikari.GatewayBot):
        self.client = client
        self.tracked_groups = {} # group_id: {channel_id, last_members: dict(user_id: role_name)}
        self.log_collector = logger.AsyncLogCollector("logs/main.log")

    async def add_group(self, group_id: int, channel_id: int):
        """Starts tracking a group."""
        if group_id in self.tracked_groups:
            self.tracked_groups[group_id]['channel_id'] = channel_id
            return
        
        # Initial members fetch
        members = await self.fetch_all_members(group_id)
        self.tracked_groups[group_id] = {
            'channel_id': channel_id,
            'last_members': members
        }
        await self.log_collector.info(f"Started spying on group {group_id}, logged to {channel_id}", initiator="GroupSpy.add_group")

    async def fetch_all_members(self, group_id: int) -> dict:
        """Fetches all member IDs and roles of a group."""
        members = {} # user_id: role_name
        cursor = ""
        while True:
            # We'll use a shard_id of 0 for background tasks
            data = await Roquest.Roquest("GET", "groups", f"v1/groups/{group_id}/users?limit=100&cursor={cursor}&sortOrder=Asc", shard_id=0)
            if data[0] != 200:
                break
            for member in data[1].get('data', []):
                members[member['user']['userId']] = member['role']['name']
            cursor = data[1].get('nextPageCursor')
            if not cursor:
                break
        return members

    async def spy_loop(self):
        """Background loop to check for group changes."""
        while True:
            await asyncio.sleep(600) # Check every 10 minutes
            for group_id, info in list(self.tracked_groups.items()):
                try:
                    current_members = await self.fetch_all_members(group_id)
                    old_members = info['last_members']
                    
                    old_set = set(old_members.keys())
                    new_set = set(current_members.keys())
                    
                    joined = new_set - old_set
                    left = old_set - new_set
                    
                    # Knightmare Analysis: Rank changes
                    rank_changes = []
                    for uid in old_set & new_set:
                        if old_members[uid] != current_members[uid]:
                            rank_changes.append((uid, old_members[uid], current_members[uid]))
                    
                    if joined or left or rank_changes:
                        await self.report_changes(group_id, info['channel_id'], joined, left, rank_changes)
                        self.tracked_groups[group_id]['last_members'] = current_members
                except Exception as e:
                    await self.log_collector.error(f"Error spying on group {group_id}: {e}", initiator="GroupSpy.spy_loop")

    async def report_changes(self, group_id: int, channel_id: int, joined: set, left: set, rank_changes: list):
        """Reports changes to Discord."""
        embed = hikari.Embed(title=f"BLACK KNIGHTS INTEL: Group {group_id} Change", color=0x990000)
        
        if joined:
            joined_str = ", ".join([f"`{uid}`" for uid in list(joined)[:20]])
            if len(joined) > 20: joined_str += f" (and {len(joined)-20} more)"
            embed.add_field(name="REINFORCEMENTS (Joined)", value=joined_str or "None", inline=False)
            
        if left:
            left_str = ", ".join([f"`{uid}`" for uid in list(left)[:20]])
            if len(left) > 20: left_str += f" (and {len(left)-20} more)"
            embed.add_field(name="DESERTIONS (Left)", value=left_str or "None", inline=False)

        if rank_changes:
            changes_str = "\n".join([f"`{uid}`: `{old}` -> `{new}`" for uid, old, new in rank_changes[:10]])
            if len(rank_changes) > 10: changes_str += f"\n(and {len(rank_changes)-10} more)"
            embed.add_field(name="KNIGHTMARE ANALYSIS (Rank Changes)", value=changes_str or "None", inline=False)
            
        embed.set_footer(text="The Black Knights see everything.")
        try:
            await self.client.rest.create_message(channel_id, embed=embed)
        except Exception:
            pass
