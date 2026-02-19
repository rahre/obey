"""
RoWhoIs
The most advanced Discord-based Roblox lookup utility

CONTRIBUTORS:
https://github.com/aut-mn
"""
import asyncio, subprocess, datetime, json, os, aiohttp, traceback, warnings
from utils import logger
warnings.filterwarnings("ignore", category=RuntimeWarning)

if os.name != "nt":
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
setattr(asyncio.sslproto._SSLProtocolTransport, "_start_tls_compatible", True)
for folder in ["logs", "cache", "cache/clothing", "cache/asset", "data"]:
    if not os.path.exists(folder): os.makedirs(folder)

logCollector, modified = logger.AsyncLogCollector("logs/main.log"), True

def sync_logging(errorlevel: str, errorcontent: str) -> None:
    """Allows for synchronous logging using https://github.com/aut-mn/AsyncLogger"""
    log_functions = {"fatal": lambda: logCollector.fatal(errorcontent, initiator="RoWhoIs.main"), "error": lambda: logCollector.error(errorcontent, initiator="RoWhoIs.main"), "warn": lambda: logCollector.warn(errorcontent, initiator="RoWhoIs.main"), "info": lambda: logCollector.info(errorcontent, initiator="RoWhoIs.main")}
    asyncio.new_event_loop().run_until_complete(log_functions[errorlevel]())

try:
    tag = subprocess.check_output(['git', 'tag', '--contains', 'HEAD']).strip()
    version = tag.decode('utf-8') if tag else None
    if version is None: raise subprocess.CalledProcessError(1, "git tag --contains HEAD")
    else: modified = False
except subprocess.CalledProcessError:
    try: # Fallback, rely on short hash
        short_commit_id = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).strip()
        version = short_commit_id.decode('utf-8')
    except subprocess.CalledProcessError: version = "0"  # Assume not part of a git workspace

try:
    with open('config.json', 'r') as configfile:
        config = json.load(configfile)
        configfile.close()
except FileNotFoundError:
    # Fallback for Railway/Environment Variables
    config = {
        "RoWhoIs": {
            "production_mode": True,
            "admin_ids": [],
            "opt_out": [],
            "banned_users": [],
            "banned_assets": [],
            "donors": [],
            "easter_egg_enabled": False,
            "subscription_bypass": False
        },
        "Authentication": {
            "production": os.environ.get("TOKEN"),
            "testing": os.environ.get("TOKEN"),
            "webhook": os.environ.get("WEBHOOK_URL", ""),
            "roblosecurity": os.environ.get("ROBLOSECURITY", ""),
            "api_key": os.environ.get("ROBLOX_API_KEY", ""),
            "topgg": "",
            "dbl": ""
        },
        "Emojis": {},
        "Proxying": {
            "proxying_enabled": False,
            "proxy_urls": [],
            "username": "",
            "password": "",
            "log_proxying": False
        }
    }

logger.display_banner(version, config['RoWhoIs']['production_mode'], modified)

# Diagnostics for Railway
if not os.environ.get("TOKEN"):
    sync_logging("fatal", "CRITICAL ERROR: 'TOKEN' environment variable is missing! The bot cannot connect without a token.")
if not os.environ.get("ROBLOSECURITY"):
    sync_logging("warn", "WARNING: 'ROBLOSECURITY' environment variable is missing. Roblox lookups requiring authentication may fail.")

for file in ["server/Roquest.py", "server/RoWhoIs.py", "utils/ErrorDict.py", "utils/gUtils.py"]:
    if not os.path.exists(file):
        sync_logging("fatal", f"Missing {file}! RoWhoIs will not be able to initialize.")
        exit(1)


def push_status(enabling: bool, webhook_token: str) -> None:
    """Pushes to the webhook the initialization status of RoWhoIs"""
    if not webhook_token: return
    try:
        async def push(enabling: bool, webhook_token: str) -> None:
            async with aiohttp.ClientSession() as session:
                async with session.request("POST", webhook_token, json={"username": "RoWhoIs Status", "avatar_url": "https://rowhois.com//rwi-pfp.png", "embeds": [{"title": "RoWhoIs Status", "color": 65293 if enabling else 0xFF0000, "description": f"RoWhoIs is now {'online' if enabling else 'offline'}!"}]}) as r:
                    pass
        # Use asyncio.run for cleaner entry if no loop is running, or safe fallback
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(push(enabling, webhook_token))
                return
        except RuntimeError: pass
        asyncio.run(push(enabling, webhook_token))
    except Exception as e: sync_logging("error", f"Failed to push to status webhook: {e}")

try:
    from utils import ErrorDict
    productionMode = config['RoWhoIs']['production_mode']
    webhookToken = config['Authentication']['webhook']
    if productionMode: sync_logging("warn", "Currently running in production mode. Non-failing user data will be truncated.")
    else: sync_logging("warn", "Currently running in testing mode. All user data will be retained.")
except KeyError:
    sync_logging("fatal", "Failed to retrieve production type. RoWhoIs will not be able to initialize.")
    exit(1)
if productionMode: push_status(True, webhookToken)
for i in range(5): # Rerun server in event of a crash
    try:
        from server import Roquest, RoWhoIs
        Roquest.initialize(config, version, modified)
        if RoWhoIs.run(version) is True: break
    except KeyboardInterrupt: break
    except asyncio.exceptions.CancelledError: break
    except RuntimeError as e:
        sync_logging("error", f"ASYNCIO RUNTIME ERROR: {e}")
        traceback.print_exc()
    except ErrorDict.MissingRequiredConfigs: sync_logging("fatal", f"Missing or malformed configuration options detected!")
    except Exception as e:
        emsg = str(e)
        if "PrivilegedIntentsRequiredError" in emsg or "privileged intents" in emsg.lower():
            sync_logging("fatal", "DISCORD ERROR: Privileged Intents Required! You MUST enable 'Presence Intent' and 'Server Members Intent' in the Discord Developer Portal (under the Bot tab).")
        print(f"FATAL EXCEPTION: {type(e)} | {e}")
        traceback.print_exc()
        sync_logging("fatal", f"A fatal error occurred during runtime: {type(e)} | {traceback.format_exc()}")
    if i < 4: sync_logging("warn", f"Server crash detected. Restarting server...")

sync_logging("info", "RoWhoIs down")
if productionMode: push_status(False, webhookToken)
os.rename("logs/main.log", f"logs/server-{datetime.datetime.now().strftime('%Y-%m-%d-%H%M%S')}.log")
exit(0)
