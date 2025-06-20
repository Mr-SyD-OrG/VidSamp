import math, time, random, os, tempfile, subprocess, asyncio
from pyrogram import Client, enums, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from utils import is_req_subscribed
from info import AUTH_CHANNEL
# ── helper UI builders ─────────────────────────────────────────────────────────
from pyrogram.errors import UserNotParticipant
SYD_CHANNELS = ["Bot_Cracker", "Mod_Moviez_X", "MrSyD_Tg"]
SYD_BACKUP_LINK = "https://t.me/+0Zi1FC4ulo8zYzVl"        # your backup group

async def ensure_member(client, msg):
    """
    Returns True if the user is a member of every channel in SYD_CHANNELS.
    Otherwise sends a join-prompt and returns False.
    Works with both Message and CallbackQuery objects.
    """
    if hasattr(msg, "from_user"):         # Message
        user_id   = msg.from_user.id
        chat_id   = msg.chat.id
        replyable = msg
    else:                                 # CallbackQuery
        user_id   = msg.from_user.id
        chat_id   = msg.message.chat.id
        replyable = msg.message          # reply to the msg that contains buttons

    not_joined = []

    for ch in SYD_CHANNELS:
        try:
            member = await client.get_chat_member(ch, user_id)
            if member.status in {"kicked", "left"}:
                not_joined.append(ch)
        except UserNotParticipant:
            not_joined.append(ch)
        except Exception:
            # channel is private / bot not admin etc. treat as not joined
            not_joined.append(ch)

    if not not_joined:
        return True   # user is OK

    # Build per-channel join buttons
    join_rows = [[
        InlineKeyboardButton(
            text=f"✧ Jᴏɪɴ {str(ch).replace('_',' ').title()} ✧",
            url=f"https://t.me/{str(ch).lstrip('@')}"
        )
    ] for ch in not_joined]

    # Extra rows: backup & re-check
    join_rows.append([InlineKeyboardButton("✧ Jᴏɪɴ Bᴀᴄᴋ Uᴩ ✧", url=SYD_BACKUP_LINK)])
    join_rows.append([InlineKeyboardButton("☑ ᴊᴏɪɴᴇᴅ ☑", callback_data="check_subscription")])

    text = (
        "**Sᴏʀʀʏ, ʏᴏᴜ ᴍᴜꜱᴛ ᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟꜱ ᴛᴏ ᴜꜱᴇ ᴛʜɪꜱ ꜰᴇᴀᴛᴜʀᴇ.**\n"
        "Pʟᴇᴀꜱᴇ ᴊᴏɪɴ ᴀɴᴅ ᴘʀᴇꜱꜱ **“ᴊᴏɪɴᴇᴅ”** ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ ⚡"
    )

    await replyable.reply_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(join_rows),
        quote=True,
        disable_web_page_preview=True
    )
    return False

async def handle_process_flags(client, query):
    user_id = query.from_user.id
    settings = await db.get_setings(user_id)
    oneprocess = settings.get('oneprocess', False)
    twoprocess = settings.get('twoprocess', False)

    # If both flags are True, user is in two sessions already
    if oneprocess and twoprocess:
        await query.message.reply_text(
            "⚠️ You're already in **two active sessions**. Please wait for them to finish before starting a new one.",
            quote=True
        )
        return False

    # First process is already running
    if oneprocess:
        if await ensure_member(client, query):
            if not twoprocess:
                await db.set_user_settings(user_id, {'twoprocess': True})
            return True
        return False  # ensure_member already sends a message

    # Start first session
    await db.set_user_settings(user_id, {'oneprocess': True})
    return True


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
    
def parse_hms(text: str) -> int | None:
    """
    Convert h:m:s or m:s (hours optional) to seconds (int).
    Returns None if the format is invalid.
    """
    parts = text.strip().split(":")
    if not 2 <= len(parts) <= 3:
        return None
    try:
        parts = [int(p) for p in parts]
    except ValueError:
        return None
    if len(parts) == 2:  # m:s
        m, s = parts
        h = 0
    else:                # h:m:s
        h, m, s = parts
    if m > 59 or s > 59 or h < 0 or m < 0 or s < 0:
        return None
    return h * 3600 + m * 60 + s
def humanbytes(size: int) -> str:
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
    if int(diff) % 5 == 0 or current == total:
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
            await message.edit(text=text)
        except Exception as e:
            print("Progress update failed:", e)

# ── FFmpeg helpers ─────────────────────────────────────────────────────────────
def ffmpeg_sample(src: str, start: int, length: int, dst: str):
    cmd = [
        "ffmpeg", "-ss", str(start), "-i", src, "-t", str(length),
        "-metadata", "title=⭐ New Title ⭐",  # ✅ Change only the title
        "-c:v", "libx264", "-c:a", "aac",
        "-preset", "ultrafast", "-y", dst
    ]
    subprocess.run(cmd, check=True, capture_output=True)

def ffmpeg_screenshot(src: str, sec: int, dst: str):
    cmd = ["ffmpeg", "-ss", str(sec), "-i", src, "-vframes", "1", "-q:v", "2", "-y", dst]
    subprocess.run(cmd, check=True, capture_output=True)

# ── main callback handler ──────────────────────────────────────────────────────
@Client.on_callback_query()
async def callback_handler(client: Client, query):
    if AUTH_CHANNEL and not await is_req_subscribed(client, query):
        btn = [[InlineKeyboardButton("⊛ Jᴏɪɴ Uᴘᴅᴀᴛᴇꜱ CʜᴀɴɴᴇL ⊛", url=invite_link.invite_link)],
               [InlineKeyboardButton("↻ Tʀʏ Aɢᴀɪɴ ↻", callback_data="checksub")]]

        await query.message.reply(
            text="Jᴏɪɴ Oᴜʀ Uᴘᴅᴀᴛᴇꜱ Cʜᴀɴɴᴇʟ Aɴᴅ Tʜᴇɴ Cʟɪᴄᴋ Oɴ Tʀʏ Aɢᴀɪɴ Tᴏ Cᴏɴᴛɪɴᴜᴇ.",
            reply_markup=InlineKeyboardMarkup(btn),
            parse_mode=enums.ParseMode.MARKDOWN
        )
        return
    orig = query.message.reply_to_message
    if not orig or not (orig.video or orig.document):
        return await query.answer("❌ Please reply to a media file.", show_alert=True)

    media = orig.video or orig.document
    duration = getattr(media, "duration", 120) or 120

    # ─ 1. 30-second sample
    if query.data == "sample":
        await query.answer("Generating sample…", show_alert=False)
       # settings = await db.get_setings(query.from_user.id)
     #   if settings.get('oneprocess'):
            #
            


        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            full_path = tmp.name
        sample_path = full_path.replace(".mp4", "_sample.mp4")

        try:
            progress_msg = await query.message.reply("📥 Starting download...", quote=True)
            await client.download_media(
                message=media,
                file_name=full_path,
                progress=progress_for_pyrogram,
                progress_args=("__Downloading…__", progress_msg, time.time())
            )
            await progress_msg.edit("Gᴇɴᴇʀᴀᴛɪɴɢ...")
            start = random.randint(0, max(0, duration - 30))
            ffmpeg_sample(full_path, start, 30, sample_path)
            await orig.reply_video(
                video=sample_path,
                caption=f"Sᴀᴍᴩʟᴇ 30ꜱ (Fʀᴏᴍ {start}s)",
                quote=True,
                progress=progress_for_pyrogram,                    # <<< NEW
                progress_args=("__Uᴩʟᴏᴀᴅɪɴɢ Sᴀᴍᴩʟᴇ__", progress_msg, time.time())  # <<< NEW
            )
            await progress_msg.delete()

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

    # ─ 2. Ask for screenshot count
    elif query.data == "screenshot":
        await query.answer()
        await orig.reply(
            "🖼 Choose number of screenshots to generate:",
            reply_markup=build_even_keyboard(),
            quote=True
        )

    # ─ 3. Take screenshots
    elif query.data.startswith("getshot#"):
        count = int(query.data.split("#")[1])
        await query.answer(f"Taking {count} random screenshots…", show_alert=False)

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            full_path = tmp.name

        try:
            progress_msg = await query.message.reply("📥 Starting download...", quote=True)
            await client.download_media(
                message=media,
                file_name=full_path,
                progress=progress_for_pyrogram,
                progress_args=("__Downloading…__", progress_msg, time.time())
            )

            timestamps = sorted(random.sample(range(2, max(duration - 1, 3)), count))
            media_group = []
            paths = []

            for idx, ts in enumerate(timestamps, start=1):
                shot_path = full_path.replace(".mp4", f"_s{idx}.jpg")
                ffmpeg_screenshot(full_path, ts, shot_path)
                paths.append(shot_path)
                media_group.append(InputMediaPhoto(
                    media=shot_path,
                    caption=f"📸 Screenshot {idx}/{count} at {ts}s" if idx == 1 else None
                ))

            await client.send_media_group(
                chat_id=query.message.chat.id,
                media=media_group,
                reply_to_message_id=orig.id
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
            for p in paths:
                if os.path.exists(p):
                    os.remove(p)

    elif query.data == "extract_audio":
        await query.answer("🎧 Extracting audio…", show_alert=False)

        orig = query.message.reply_to_message
        if not orig or not (orig.video or orig.document):
            return await query.message.reply("❌ Please reply to a video or audio-supported file.", quote=True)

        media = orig.video or orig.document

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            full_path = tmp.name
        audio_path = full_path.replace(".mp4", ".m4a")

        try:
            # download with progress
            await client.download_media(
                message=media,
                file_name=full_path,
                progress=progress_for_pyrogram,
                progress_args=("__Downloading…__", query.message, time.time())
            )
            await query.message.edit("Gᴇɴᴇʀᴀᴛɪɴɢ ᴀɴᴅ ᴜᴩʟᴏᴀᴅɪɴɢ ᴀᴜᴅɪᴏ")
            # extract audio
            cmd = [
                "ffmpeg", "-i", full_path, "-vn", "-c:a", "aac", "-b:a", "192k", "-y", audio_path
            ]
            subprocess.run(cmd, check=True, capture_output=True)

            await orig.reply_audio(
                audio=audio_path,
                caption="🎵 Extracted Audio",
                quote=True
            )
        except subprocess.CalledProcessError as e:
            await query.message.reply(
                f"❌ FFmpeg error:\n<code>{e.stderr.decode()}</code>",
                parse_mode=enums.ParseMode.HTML,
                quote=True
            )
        finally:
            for f in (full_path, audio_path):
                if os.path.exists(f):
                    os.remove(f)

    elif query.data == "trim":
       # await query.answer()
        prompt1 = await orig.reply(
            "✂️ **Trim:**\nSend start time in `m:s` or `h:m:s` format:",
            quote=True
        )

        try:
            await orig.reply("3")
            start_msg = await client.listen(
                chat_id=query.from_user.id,
                timeout=90
            )
            await orig.reply("3")
        except asyncio.TimeoutError:
            await prompt1.edit("⏰ Timed-out. Trim cancelled.", parse_mode="md")
            return
        except Exception as e:
            await orig.reply(f"Error {e}")

        await orig.reply("3")
        start_sec = parse_hms(start_msg.text)
        if start_sec is None:
            return await start_msg.reply("❌ Invalid time format. Trim cancelled.", quote=True)

        # Ask for end time
        prompt2 = await start_msg.reply(
            "Now send **end time**:", quote=True, parse_mode="md"
        )
        try:
            end_msg = await client.listen(
                chat_id=query.from_user.id,
                timeout=90
            )
        except asyncio.TimeoutError:
            await prompt2.edit("⏰ Timed-out. Trim cancelled.", parse_mode="md")
            return
        end_sec = parse_hms(end_msg.text)
        if end_sec is None:
            return await end_msg.reply("❌ Invalid time format. Trim cancelled.", quote=True)

        # Validation
        if end_sec <= start_sec:
            return await end_msg.reply("⚠️ End time must be greater than start time.", quote=True)
        if end_sec > duration:
            return await end_msg.reply("⚠️ End time exceeds video length.", quote=True)
        if end_sec - start_sec > 600:
            return await end_msg.reply("⚠️ Segment must be ≤ 10 minutes.", quote=True)

        # Start processing
        ack = await end_msg.reply("📥 Downloading for trim…", quote=True)
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            full_path = tmp.name
        trimmed_path = full_path.replace(".mp4", "_trimmed.mp4")
        try:
            await client.download_media(
                message=media,
                file_name=full_path,
                progress=progress_for_pyrogram,
                progress_args=("__Downloading…__", ack, time.time())
            )

            # First try a fast copy
            cmd = [
                "ffmpeg", "-ss", str(start_sec), "-to", str(end_sec),
                "-i", full_path, "-c", "copy", "-y", trimmed_path
            ]
            proc = subprocess.run(cmd, capture_output=True)
            if proc.returncode != 0:  # fallback re-encode
                cmd = [
                    "ffmpeg", "-ss", str(start_sec), "-to", str(end_sec),
                    "-i", full_path, "-c:v", "libx264", "-c:a", "aac",
                    "-preset", "medium", "-y", trimmed_path
                ]
                subprocess.run(cmd, check=True, capture_output=True)

            await orig.reply_video(
                video=trimmed_path,
                caption=f"✂️ Trimmed segment {start_msg.text} → {end_msg.text}",
                quote=True
            )
        except subprocess.CalledProcessError as e:
            await ack.edit(f"❌ FFmpeg error:\n<code>{e.stderr.decode()}</code>",
                           parse_mode=enums.ParseMode.HTML)
        finally:
            for p in (full_path, trimmed_path):
                if os.path.exists(p):
                    os.remove(p)


    elif query.data == "checksub":
        await query.answer("🔍 Checking access…", show_alert=False)

        buttons = [
            [InlineKeyboardButton("Sᴀᴍᴩʟᴇ - 30ꜱ", callback_data="sample")],
            [InlineKeyboardButton("Gᴇɴᴇʀᴀᴛᴇ Sᴄʀᴇᴇɴꜱʜᴏᴛ", callback_data="screenshot")],
            [InlineKeyboardButton("Tʀɪᴍ", callback_data="trim")],
            [InlineKeyboardButton("Exᴛʀᴀᴄᴛ Aᴜᴅɪᴏ", callback_data="extract_audio")],
            [InlineKeyboardButton("⚡ Fast Download", url=download_url),
             InlineKeyboardButton("▶️ Watch Online", url=stream_url)],
            [InlineKeyboardButton("🆘 Support", url="https://t.me/YourSupportGroup")]
        ]

        await query.message.reply(
            "✅ You have access. Choose an action below:",
            reply_markup=InlineKeyboardMarkup(buttons),
            quote=True
        )

