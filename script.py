import os
import sys
import time
import requests
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

API_BASE = "https://discord.com/api/v10"
CDN_BASE = "https://cdn.discordapp.com"
OUTPUT_DIR = "avatars"

def get_user_object(user_id: str) -> dict:
    headers = {"Authorization": f"Bot {BOT_TOKEN}"}
    url = f"{API_BASE}/users/{user_id}"
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.json()

def avatar_url_from_user(user_obj: dict) -> str:
    user_id = user_obj["id"]
    avatar = user_obj.get("avatar")
    discriminator = user_obj.get("discriminator", "0")

    if avatar:
        is_animated = avatar.startswith("a_")
        ext = "gif" if is_animated else "png"
        return f"{CDN_BASE}/avatars/{user_id}/{avatar}.{ext}?size=2048"
    else:
        try:
            idx = int(discriminator) % 5
        except Exception:
            idx = 0
        return f"{CDN_BASE}/embed/avatars/{idx}.png"

def download_file(url: str, out_path: str):
    with requests.get(url, stream=True, timeout=15) as r:
        r.raise_for_status()
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

def process_user(user_id: str, delay: float = 2.0):
    user_id = user_id.strip()
    if not user_id or not user_id.isdigit():
        print(f"Skipping '{user_id}' (bukan user_id angka)")
        return

    try:
        user = get_user_object(user_id)
    except Exception as e:
        print(f"Gagal fetch {user_id}: {e}")
        return

    url = avatar_url_from_user(user)
    ext = url.split("?")[0].split(".")[-1]
    filename = f"{user.get('username','user')}_{user_id}.{ext}".replace("/", "_")
    out_path = os.path.join(OUTPUT_DIR, filename)

    print(f"Downloading {user.get('username')}#{user.get('discriminator')} -> {url}")

    try:
        download_file(url, out_path)
        print("Saved:", out_path)
    except Exception as e:
        print("Download gagal:", e)

    time.sleep(delay)

def main():
    if len(sys.argv) < 2:
        print("Usage: python download_avatars.py users.txt")
        sys.exit(1)

    if not BOT_TOKEN:
        print("Error: DISCORD_BOT_TOKEN tidak ditemukan di .env")
        sys.exit(1)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    users_file = sys.argv[1]
    with open(users_file, "r", encoding="utf-8") as f:
        for line in f:
            process_user(line)

if __name__ == "__main__":
    main()
