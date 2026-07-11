import asyncio
import random
import time
from typing import List, Optional

import aiohttp
import requests  # fallback

class DiscordUsernameSniper:
    def __init__(
        self,
        token: str,
        target_username: str,
        password: str,          # Required for username changes
        proxies: List[str],     # List of proxies like "http://ip:port" or "http://user:pass@ip:port"
        delay: float = 1.0,     # Delay between attempts (seconds)
        webhook_url: Optional[str] = None
    ):
        self.token = token
        self.target_username = target_username.strip()
        self.password = password
        self.proxies = proxies
        self.delay = delay
        self.webhook_url = webhook_url
        self.attempts = 0
        self.session = None

    def get_random_proxy(self) -> Optional[str]:
        """Return a random proxy or None if no proxies."""
        if not self.proxies:
            return None
        proxy = random.choice(self.proxies)
        return proxy.strip() if proxy else None

    async def send_webhook(self, message: str, color: int = 0x00ff00):
        if not self.webhook_url:
            return
        try:
            async with aiohttp.ClientSession() as sess:
                await sess.post(
                    self.webhook_url,
                    json={
                        "embeds": [{
                            "title": "Discord Username Sniper",
                            "description": message,
                            "color": color,
                            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                        }]
                    }
                )
        except Exception:
            pass  # silent fail

    async def check_and_snipe(self) -> bool:
        proxy = self.get_random_proxy()
        proxy_dict = {"http": proxy, "https": proxy} if proxy else None

        headers = {
            "Authorization": self.token,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        payload = {
            "username": self.target_username,
            "password": self.password
        }

        self.attempts += 1
        print(f"[Attempt {self.attempts}] Trying to snipe '{self.target_username}' | Proxy: {'Enabled' if proxy else 'None'}")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.patch(
                    "https://discord.com/api/v9/users/@me",
                    json=payload,
                    headers=headers,
                    proxy=proxy,
                    timeout=10
                ) as resp:
                    text = await resp.text()

                    if resp.status == 200:
                        print(f"✅ SUCCESS! Sniped username: {self.target_username}")
                        await self.send_webhook(f"**Successfully sniped:** `{self.target_username}`", 0x00ff00)
                        return True

                    elif resp.status == 429:
                        retry_after = resp.headers.get("Retry-After", 5)
                        print(f"⏳ Rate limited. Waiting {retry_after}s...")
                        await asyncio.sleep(float(retry_after))
                        return False

                    elif resp.status == 400:
                        # Often means username taken or invalid
                        print(f"❌ Username taken / invalid ({resp.status}): {text[:200]}")
                    elif resp.status == 401:
                        print("❌ Invalid token!")
                        return True  # stop
                    else:
                        print(f"⚠️ Status {resp.status}: {text[:300]}")

        except Exception as e:
            print(f"❌ Error: {e}")

        return False

    async def run(self):
        print(f"🚀 Starting sniper for username: {self.target_username}")
        print(f"Proxies loaded: {len(self.proxies)}")

        while True:
            success = await self.check_and_snipe()
            if success:
                break

            await asyncio.sleep(self.delay + random.uniform(0.1, 0.5))  # jitter


# ========================== CONFIG ==========================
if __name__ == "__main__":
    TOKEN = "YOUR_USER_TOKEN_HERE"          # User token (self-bot)
    TARGET_USERNAME = "desiredusername"     # without @
    PASSWORD = "your_account_password"      # Required for security

    # Load proxies from file (one per line)
    try:
        with open("proxies.txt", "r", encoding="utf-8") as f:
            PROXIES = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        print("proxies.txt not found. Running without proxies.")
        PROXIES = []

    WEBHOOK_URL = None  # Optional: "https://discord.com/api/webhooks/..."

    sniper = DiscordUsernameSniper(
        token=TOKEN,
        target_username=TARGET_USERNAME,
        password=PASSWORD,
        proxies=PROXIES,
        delay=0.8,          # Adjust based on rate limits (higher = safer)
        webhook_url=WEBHOOK_URL
    )

    asyncio.run(sniper.run())