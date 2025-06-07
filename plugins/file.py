from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import tempfile, subprocess, os, random

def build_even_keyboard() -> InlineKeyboardMarkup:
    """Return 2,4,…,20 buttons in rows of five."""
    rows, row = [], []
    for sec in range(2, 22, 2):
        row.append(InlineKeyboardButton(str(sec), callback_data=f"getshot#{sec}"))
        if len(row) == 5:
            rows.append(row); row = []
    if row: rows.append(row)
    return InlineKeyboardMarkup(rows)

def ffmpeg_sample(src: str, start: int, length: int, dst: str):
    """Extract sample clip of <length>s from <start>s in <src> to <dst>."""
    cmd = [
        "ffmpeg", "-ss", str(start), "-i", src, "-t", str(length),
        "-c:v", "libx264", "-c:a", "aac", "-preset", "ultrafast", "-y", dst
    ]
    subprocess.run(cmd, check=True, capture_output=True)

def ffmpeg_screenshot(src: str, sec: int, dst: str):
    """Take screenshot at <sec>s from <src>."""
    cmd = [
        "ffmpeg", "-ss", str(sec), "-i", src, "-vframes", "1", "-q:v", "2", "-y", dst
    ]
    subprocess.run(cmd, check=True, capture_output=True)

@Client.on_callback_query()
async def callback_hadler(client, query):
    if not query.message.reply_to_message or not (
        query.message.reply_to_message.video or query.message.reply_to_message.document
    ):
        return await query.answer("❌ Please reply to a media file.", show_alert=True)

    media = query.message.reply_to_message.video or query.message.reply_to_message.document
    duration = getattr(media, 'duration', 120) or 120  # fallback if not video

    # ── 1️⃣  Handle "sample"
    if query.data == "sample":
        await query.answer("Generating sample…", show_alert=False)

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            file_path = tmp.name

        sample_path = file_path.replace(".mp4", "_sample.mp4")
        try:
            await media.download(file_path)
            start = random.randint(0, max(0, duration - 30))
            ffmpeg_sample(file_path, start, 30, sample_path)
            await client.send_video(
                chat_id=query.from_user.id,
                video=sample_path,
                caption=f"🎞 Sample (30s from {start}s)"
            )
        except subprocess.CalledProcessError as e:
            await query.message.reply(
                f"❌ FFmpeg error:\n<code>{e.stderr.decode()}</code>",
                parse_mode=enums.ParseMode.HTML
            )
        finally:
            for f in (file_path, sample_path):
                if os.path.exists(f): os.remove(f)

    # ── 2️⃣  Handle "screenshot"
    elif query.data == "screenshot":
        await query.answer()
        await query.message.reply("🖼 Choose second for screenshot:",
            reply_markup=build_even_keyboard())

    # ── 3️⃣  Handle "getshot#<sec>"
    elif query.data.startswith("getshot#"):
        sec = int(query.data.split("#")[1])
        await query.answer(f"Generating screenshot at {sec}s…", show_alert=False)

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            file_path = tmp.name
        shot_path = file_path.replace(".mp4", ".jpg")

        try:
            await media.download(file_path)
            ffmpeg_screenshot(file_path, sec, shot_path)
            await client.send_photo(
                chat_id=query.from_user.id,
                photo=shot_path,
                caption=f"🖼 Screenshot at {sec}s"
            )
        except subprocess.CalledProcessError as e:
            await query.message.reply(
                f"❌ FFmpeg error:\n<code>{e.stderr.decode()}</code>",
                parse_mode=enums.ParseMode.HTML
            )
        finally:
            for f in (file_path, shot_path):
                if os.path.exists(f): os.remove(f)

    else:
        await query.answer("Unknown command.", show_alert=True)
