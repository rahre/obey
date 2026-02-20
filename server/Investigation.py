"""
Investigation Module for Aegis
Theme: Absolute Order
"""
import asyncio
from server import RoModules, Roquest
from typing import Tuple, List

async def check_roblox_alt(user1_id: int, user2_id: int, shard_id: int = 0) -> dict:
    """Compares two Roblox accounts for potential alt indicators."""
    tasks = [
        RoModules.get_full_player_profile(user1_id, shard_id),
        RoModules.get_full_player_profile(user2_id, shard_id),
        RoModules.get_groups(user1_id, shard_id),
        RoModules.get_groups(user2_id, shard_id),
        RoModules.get_friends(user1_id, shard_id),
        RoModules.get_friends(user2_id, shard_id)
    ]
    
    results = await asyncio.gather(*tasks)
    p1, p2, g1, g2, f1, f2 = results
    
    # Common Groups
    groups1 = {g['group']['id'] for g in g1['data']}
    groups2 = {g['group']['id'] for g in g2['data']}
    common_groups = groups1 & groups2
    
    # Common Friends
    friends1 = {f['id'] for f in f1['data']}
    friends2 = {f['id'] for f in f2['data']}
    common_friends = friends1 & friends2
    
    # Age Difference
    date1 = p1[0].joined
    date2 = p2[0].joined
    
    return {
        "user1": p1[0],
        "user2": p2[0],
        "common_groups_count": len(common_groups),
        "common_friends_count": len(common_friends),
        "joined1": date1,
        "joined2": date2,
        "score": (len(common_groups) * 5) + (len(common_friends) * 2) # Arbitrary score
    }

async def map_friends(user_id: int, shard_id: int = 0):
    """Analyzes a subject's friends and associates."""
    friends = await RoModules.get_friends(user_id, shard_id)
    if not friends or 'data' not in friends:
        return []
    
    # We'll just return the top associates for now
    associates = []
    for f in friends['data'][:15]: # Show top 15
        associates.append({
            "id": f['id'],
            "name": f['name'],
            "display_name": f['displayName']
        })
    return associates
