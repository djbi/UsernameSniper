# Discord Username Sniper

A simple Python tool to snipe Discord usernames using a user token and proxy rotation.

> ⚠️ **Warning**: This uses a self-bot (user token). This violates Discord's ToS and may result in your account being banned. Use at your own risk.

## Features
- Proxy support (HTTP / HTTPS / SOCKS)
- Automatic retry with delay
- Optional Discord webhook notifications
- Rate limit handling

## Setup

### 1. Install Requirements
```bash
pip install aiohttp requests


### 2. 
Create a file named proxies.txt in the same folder and add your proxies (one per line):


### 3. Configure the Script
Edit the bottom section of sniper.py:

TOKEN = "YOUR_DISCORD_USER_TOKEN"
TARGET_USERNAME = "desiredusername"   # without @
PASSWORD = "your_account_password"
WEBHOOK_URL = None                     # Optional

  ### 4. Run the Sniper
    python sniper.py