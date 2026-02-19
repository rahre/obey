"""
Invite Tracking Module for Aegis
Theme: Eye of Geass
"""
import hikari
import logging

class InviteTracker:
    def __init__(self, client: hikari.GatewayBot):
        self.client = client
        self.invites = {} # guild_id: {invite_code: uses}

    async def update_invites(self, guild_id: int):
        """Updates the internal invite cache for a guild."""
        try:
            invites = await self.client.rest.fetch_guild_invites(guild_id)
            self.invites[guild_id] = {invite.code: invite.uses for invite in invites}
        except hikari.errors.ForbiddenError:
            pass # No permission

    async def find_inviter(self, guild_id: int) -> Optional[hikari.Invite]:
        """Finds the invite used by the most recent join."""
        if guild_id not in self.invites:
            return None
        
        try:
            current_invites = await self.client.rest.fetch_guild_invites(guild_id)
            old_invites = self.invites[guild_id]
            
            for invite in current_invites:
                if invite.code in old_invites:
                    if invite.uses > old_invites[invite.code]:
                        self.invites[guild_id][invite.code] = invite.uses
                        return invite
                elif invite.uses > 0:
                    # New invite used
                    self.invites[guild_id][invite.code] = invite.uses
                    return invite
            
            # If no change found, update cache anyway
            self.invites[guild_id] = {invite.code: invite.uses for invite in current_invites}
            
        except hikari.errors.ForbiddenError:
            return None
        return None
