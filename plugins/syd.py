import logging, re, asyncio
from utils import temp
from info import ADMINS
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, ChatAdminRequired, UsernameInvalid, UsernameNotModified

from database.ia_filterdb import save_file
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
lock = asyncio.Lock()

INDEX_CHANNEL = "-1002498086501"

@Client.on_message(filters.document | filters.audio | filters.video)
async def auto(bot, message):
    # Check if the message is from the specified channel
    if message.chat.id == INDEX_CHANNEL:
        # Log the received media for tracking purposes
        logger.info(f"Received {message.media.value} from {message.chat.title or message.chat.id}")

        # Extract the media
        media = getattr(message, message.media.value, None)
        if media:
            media.file_type = message.media.value
            media.caption = message.caption
            
            # Save the media file
            aynav, vnay = await save_file(media)
            
            # Handle the result of the save operation
            if aynav:
                await message.reply("File successfully indexed and saved.")
            elif vnay == 0:
                await message.reply("Duplicate file was skipped.")
            elif vnay == 2:
                await message.reply("Error occurred while saving the file.")
        else:
            logger.warning("No media found in the message.")
