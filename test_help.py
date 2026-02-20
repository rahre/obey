import asyncio, json, os, sys
from server import RoWhoIs


# Fake interaction
class FakeCommandInteraction:
    def __init__(self):
        self.channel_id = 123
        self.user = type("User", (), {"id": 123})()

    async def create_initial_response(self, **kwargs):
        print("create_initial_response:", kwargs)


async def test():
    try:
        interaction = FakeCommandInteraction()
        await RoWhoIs.help(interaction)
        print("Success!")
    except Exception as e:
        import traceback

        traceback.print_exc()


# Mock config
sys.modules["aioconsole"] = type("aioconsole", (), {"ainput": lambda x: None})
try:
    asyncio.run(test())
except Exception as e:
    import traceback

    traceback.print_exc()
