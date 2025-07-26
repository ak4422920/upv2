import os
import aiohttp
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from utils import readable_size, is_video_file, bypass_link
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH")
OWNER_ID = int(os.getenv("OWNER_ID", 0))
LOG_CHANNEL = os.getenv("LOG_CHANNEL")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 2_000_000_000))

bot = Client("ZoroverseXBypassBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.command("start") & filters.private)
async def start(client: Client, message: Message):
    await message.reply_text(
        f"👋 Hello {message.from_user.first_name}!
"
        f"I'm ZoroverseX Advanced Uploader Bot with 🔓Bypass support.
"
        f"Send me any direct or shortened movie links. I’ll do the rest!",
        quote=True
    )

@bot.on_message(filters.text & filters.private & (~filters.command([])))
async def handle_link(client: Client, message: Message):
    url = message.text.strip()
    if not url.startswith("http"):
        return await message.reply_text("❌ Not a valid URL.")

    msg = await message.reply("⏳ Processing your link...")

    try:
        bypassed_url = await bypass_link(url)
        final_url = bypassed_url if bypassed_url else url
        await handle_direct(client, message, final_url, msg)
    except Exception as e:
        logger.error(e)
        await msg.edit("❌ Error occurred while processing the link.")

async def handle_direct(client, message, url, msg):
    await msg.edit("📥 Downloading file...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                filename = url.split("/")[-1].split("?")[0] or "file.bin"
                size = int(resp.headers.get("Content-Length", 0))
                if size > MAX_FILE_SIZE:
                    return await msg.edit("⚠️ File too large.")
                with open(filename, "wb") as f:
                    f.write(await resp.read())
        await upload(client, message, filename, msg)
    except Exception as e:
        logger.error(e)
        await msg.edit("❌ Download/upload failed.")

async def upload(client, message, filename, msg):
    await msg.edit("⬆️ Uploading to Telegram...")
    try:
        if is_video_file(filename):
            await client.send_video(message.chat.id, filename, caption="🎥 Uploaded by @ZoroverseBot", supports_streaming=True)
        else:
            await client.send_document(message.chat.id, filename, caption="📁 Uploaded by @ZoroverseBot")
        os.remove(filename)
        if LOG_CHANNEL:
            await client.send_message(LOG_CHANNEL, f"✅ Uploaded: {filename} by {message.from_user.mention}")
        await msg.delete()
    except Exception as e:
        logger.error(e)
        await msg.edit("❌ Failed to upload to Telegram.")

if __name__ == "__main__":
    bot.run()