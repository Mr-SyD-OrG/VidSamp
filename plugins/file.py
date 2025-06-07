import math, time, random, os, tempfile, subprocess
from pyrogram import Client, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ── helper UI builders ─────────────────────────────────────────────────────────
def build_even_keyboard() -> InlineKeyboardMarkup:
    rows, row = [], []
    for sec in range(2, 22, 2):
        row.append(InlineKeyboardButton(str(sec), callback_data=f"getshot#{sec}"))
        if len(row) == 5:
            rows.append(row); row = []
    if row:
        rows.append(row)
    return InlineKeyboardMarkup(rows)

def generate_progress_bar(percentage: float) -> str:
    filled = "⬢" * math.floor(percentage / 5)
    empty  = "⬡" * (20 - math.floor(percentage / 5))
    return filled + empty

def humanbytes(size: int) -> str:
    # simple IEC units
    power, unit = 1024, 0
    units = ["B", "KiB", "MiB", "GiB", "TiB"]
    while size >= power and unit < len(units) - 1:
        size /= power; unit += 1
    return f"{size:.2f} {units[unit]}"

def calculate_times(diff, current, total, speed):
    if speed == 0:
        return diff, 0, ""
    time_to_completion = (total - current) / speed
    return diff, time_to_completion, time_to_completion + diff

async def progress_for_pyrogram(current, total, ud_type, message, start):
    now, diff = time.time(), time.time() - start
    if current == total or round(diff % 5.00) == 0:
        percentage = current * 100 / total
        speed      = current / diff if diff else 0
        _, eta, _  = calculate_times(diff, current, total, speed)

        bar = generate_progress_bar(percentage)
        text = (
            f"{ud_type}\n\n"
            f"{bar} `{percentage:.2f}%`\n"
            f"**{humanbytes(current)} / {humanbytes(total)}** "
            f"at **{humanbytes(speed)}/s**\n"
            f"ETA: `{round(eta)} s`"
        )
        try:
            await message.edit(text=text, parse_mode="md")
        except:
            pass

# ── FFmpeg helpers ─────────────────────────────────────────────────────────────
def ffmpeg_sample(src: str, start: int, length: int, dst: str):
    cmd = [
        "ffmpeg", "-ss", str(start), "-i", src, "-t", str(length),
        "-c:v", "libx264", "-c:a", "aac", "-preset", "ultrafast", "-y", dst
    ]
    subprocess.run(cmd, check=True, capture_output=True)

def ffmpeg_screenshot(src: str, sec: int, dst: str):
    cmd = ["ffmpeg", "-ss", str(sec), "-i", src, "-vframes", "1", "-q:v", "2", "-y", dst]
    subprocess.run(cmd, check=True, capture_output=True)

# ── main callback handler ──────────────────────────────────────────────────────
@Client.on_callback_query()
async def callback_handler(client, query):
    # must be a reply to a media message
    orig = query.message.reply_to_message
    if not orig or not (orig.video or orig.document):
        return await query.answer("❌ Please reply to a media file.", show_alert=True)

    media    = orig.video or orig.document
    duration = getattr(media, "duration", 120) or 120

    # ─ 1. 30-second sample ────────────────────────────────────────────────────
    if query.data == "sample":
        await query.answer("Generating sample…", show_alert=False)

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            full_path = tmp.name
        sample_path = full_path.replace(".mp4", "_sample.mp4")

        try:
            # download with progress
            await client.download_media(
                message = media,
                file_name = full_path,
                progress = progress_for_pyrogram,
                progress_args = ("__Downloading…__", query.message, time.time())
            )

            start = random.randint(0, max(0, duration - 30))
            ffmpeg_sample(full_path, start, 30, sample_path)

            await orig.reply_video(
                video   = sample_path,
                caption = f"🎞 Sample (30 s from {start}s)",
                quote   = True
            )
        except subprocess.CalledProcessError as e:
            await query.message.reply(
                f"❌ FFmpeg error:\n<code>{e.stderr.decode()}</code>",
                parse_mode=enums.ParseMode.HTML,
                quote=True
            )
        finally:
            for f in (full_path, sample_path):
                if os.path.exists(f):
                    os.remove(f)

    # ─ 2. ask for second ──────────────────────────────────────────────────────
    elif query.data == "screenshot":
        await query.answer()
        await orig.reply(
            "🖼 Choose second for screenshot:",
            reply_markup = build_even_keyboard(),
            quote = True
        )

    # ─ 3.
    elif query.data.startswith("getshot#"):
        count = int(query.data.split("#")[1])
        await query.answer(f"Taking {count} random screenshots…", show_alert=False)

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            full_path = tmp.name

        try:
            # Download media with progress
            await client.download_media(
                message = media,
                file_name = full_path,
                progress = progress_for_pyrogram,
                progress_args = ("__Downloading…__", query.message, time.time())
            )

            # Generate random timestamps
            timestamps = sorted(random.sample(range(2, max(duration - 1, 3)), count))
            media_group = []

            for idx, ts in enumerate(timestamps, start=1):
                shot_path = full_path.replace(".mp4", f"_s{idx}.jpg")
                ffmpeg_screenshot(full_path, ts, shot_path)
                media_group.append({
                    "type": "photo",
                    "media": shot_path,
                    "caption": f"📸 Screenshot {idx}/{count} at {ts}s" if idx == 1 else ""
                })

            await client.send_media_group(
                chat_id = query.message.chat.id,
                media = media_group,
                reply_to_message_id = orig.id
            )

        except subprocess.CalledProcessError as e:
            await query.message.reply(
                f"❌ FFmpeg error:\n<code>{e.stderr.decode()}</code>",
                parse_mode=enums.ParseMode.HTML,
                quote=True
            )
        finally:
            if os.path.exists(full_path):
                os.remove(full_path)
            for file in os.listdir(tempfile.gettempdir()):
                if file.startswith(os.path.basename(full_path).replace(".mp4", "_s")) and file.endswith(".jpg"):
                    try: os.remove(os.path.join(tempfile.gettempdir(), file))
                    except: pass

