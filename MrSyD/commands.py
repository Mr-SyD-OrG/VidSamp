from info import *
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from pyrogram import Client, filters, enums



@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(message.from_user.id, message.from_user.mention))
    
    await message.reply_text(
        text="<b>Oᴋ ʏᴏᴜ ᴄᴀɴ ᴄᴏɴᴛɪɴᴜᴇ ᴜꜱɪɴɢ ᴛʜᴇ ʙᴏᴛ...!😊 \nTʜᴀɴᴋꜱ ꜰᴏʀ ᴛʜᴇ ᴩʟᴇᴀꜱᴜʀᴇ ✨ @Mr_MovSearch_Bot</b>",   
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("OPEN", url=f"https://t.me/+5n7vViwKXJJiMjhl")]])
    )
