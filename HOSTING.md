# Aegis OSINT: Deployment Guide

Your tactical bot is ready. Here is how to host it for free.

## Option 1: Koyeb (Recommended)
1. Fork the codebase to your GitHub.
2. Sign up at [Koyeb.com](https://www.koyeb.com/).
3. Create a new App and connect your GitHub repository.
4. Koyeb will automatically detect the `Dockerfile` and build it.
5. In the "Environment Variables" section, add:
   - `TOKEN`: Your Discord bot token.
   - `ROBLOSECURITY`: Your .ROBLOSECURITY cookie (for search features).

## Option 2: Railway (Best for Perpetual Hosting)
1. **GitHub Setup**: I have already initialized git and linked it to your repository: [rahre/obey](https://github.com/rahre/obey).
2. **Push the Intel**: Run the following in your terminal:
   ```powershell
   git add .
   git commit -m "Initialize Aegis OSINT: Ultimate Suite"
   git push -u origin master
   ```
3. **Deploy**:
   - Go to [Railway.app](https://railway.app/).
   - Click **New Project** -> **Deploy from GitHub repo**.
   - Select `rahre/obey`.
4. **Configuration**:
   - In Railway, go to the **Variables** tab.
   - Add your `TOKEN` (Discord bot token) and `.ROBLOSECURITY` cookie.
   - The bot will automatically start using the included `Dockerfile`.

## Option 3: Self-Hosting (Docker)
If you have a server or a home PC always on:
```bash
docker build -t aegis-osint .
docker run -d --name aegis-bot -e TOKEN=your_token aegis-osint
```

**Note**: For Discord invite tracking and Group Spy to work reliably, the bot should be online 24/7.
