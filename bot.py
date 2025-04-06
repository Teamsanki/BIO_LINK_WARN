from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
import requests
import os
import time

# ----------- Bot Config -------------
API_ID = 22243185
API_HASH = "39d926a67155f59b722db787a23893ac"
BOT_TOKEN = "7364490758:AAFQHSTWOfFxxebzOpP_O_lLakaYPLYNkDo"
OWNER_ID = 5311223486
NSFW_API_KEY = "000c1386-b011-4cea-8db0-a181b31e3718"

app = Client("GroupSecurityBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ----------- Banned Words & Links -------------
ABUSE_WORDS = ["cp", "ncert", "physics wallah", "aakash", "byjus", "dick", "madarchod", "bsdk", "sex", "asshole", "lund", "randi", "lode"]
BANNED_EXTENSIONS = [".pdf", ".gif", ".apk", ".zip", ".exe", ".txt", ".html", ".php", ".py"]

def contains_link(text):
    return any(x in text for x in ["http://", "https://", "t.me", "www."])

# ----------- Start Command -------------
@app.on_message(filters.command("start"))
async def start(client, message):
    buttons = [
        [InlineKeyboardButton("ð Owner", url="https://t.me/moh_maya_official"),
         InlineKeyboardButton("ð¢ Update", url="https://t.me/otploothub")],
        [InlineKeyboardButton("â Add to Group", url=f"https://t.me/{(await client.get_me()).username}?startgroup=true")]
    ]
    await message.reply_photo(
        photo="https://graph.org/file/e7d8fcbcd6b0ba2b334d5-431de28784638bf363.jpg",
        caption=(
            "ð¤ ð¦ðððð ð²ð¾ð¼ððððð ð±ðð»ðð ð¡ï¸\n\n"
            "ð¬ð¼ðð¿ ðð¹ð¹-ðð»-ð¢ð»ð² ð´ðð®ð¿ð± ð³ð¼ð¿ ð§ð²ð¹ð²ð´ð¿ð®ðº ðð¿ð¼ðð½ð.\n"
            "ð Link Protection\n"
            "ð§  Abuse Filter\n"
            "â NSFW Filter\n"
            "ð File Blocking\n"
            "ð Edited Message Deletion"
        ),
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# ----------- Ping Command -------------
@app.on_message(filters.command("ping"))
async def ping(_, message):
    start = time.time()
    m = await message.reply("Pinging...")
    end = time.time()
    await m.edit(f"Pong! {round((end - start) * 1000)} ms")

# ----------- New Group Joined -------------
@app.on_chat_member_updated()
async def joined_group(client, member):
    if member.new_chat_member.user.id == (await client.get_me()).id:
        await client.send_message(OWNER_ID, f"â Bot added to group: {member.chat.title} ({member.chat.id})")

# ----------- Message Monitoring -------------
@app.on_message(filters.group & filters.text)
async def monitor_messages(client, message: Message):
    text = message.text.lower()
    if len(text) > 250 or contains_link(text) or any(bad in text for bad in ABUSE_WORDS):
        await message.delete()
        await message.reply(f"{message.from_user.mention} Ye sab krna hai to dusre group me kiya kro idhar nahi samjha ð¡.!")

# ----------- Edited Messages Delete -------------
@app.on_message(filters.group)
async def edited_message_check(client, message):
    if message.edit_date:
        await message.delete()

# ----------- Banned File Extensions Delete -------------
@app.on_message(filters.group & filters.document)
async def delete_banned_files(client, message):
    filename = message.document.file_name.lower()
    if any(filename.endswith(ext) for ext in BANNED_EXTENSIONS):
        await message.delete()
        await message.reply(f"{message.from_user.mention} File not allowed.")

# ----------- NSFW Sticker Check -------------
@app.on_message(filters.group & filters.sticker)
async def nsfw_sticker(client, message):
    # Ignore animated/video stickers
    if message.sticker.is_animated or message.sticker.is_video:
        return

    file_path = await message.download()
    try:
        with open(file_path, "rb") as f:
            response = requests.post(
                "https://api.deepai.org/api/nsfw-detector",
                headers={"api-key": NSFW_API_KEY},
                files={'image': f}
            )
        response.raise_for_status()
        data = response.json()

        nsfw_score = data.get("output", {}).get("nsfw_score", 0)
        if nsfw_score > 0.7:
            await message.delete()
            await message.reply(
                f"{message.from_user.mention} Wtf bhai kya bhej raha hai NSFW sticker!"
            )
    except requests.exceptions.RequestException as e:
        print("Network error during NSFW check:", e)
    except Exception as e:
        print("General error in NSFW detection:", e)
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

# ----------- Bot Start -------------
print("Bot is running...")
app.run()
