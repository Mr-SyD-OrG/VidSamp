import os
import logging
import random
import asyncio
import pytz, string
from Script import script
from datetime import datetime
from pyrogram import Client, filters, enums
from pyrogram.errors import ChatAdminRequired, FloodWait
from pyrogram.types import *
from urllib.parse import quote_plus
from database.ia_filterdb import Media, get_file_details, unpack_new_file_id, get_bad_files
from database.users_chats_db import db, delete_all_referal_users, get_referal_users_count, get_referal_all_users, referal_add_user
from info import CHANNELS, ADMINS, AUTH_CHANNEL, LOG_CHANNEL, PICS, BATCH_FILE_CAPTION, CUSTOM_FILE_CAPTION, PROTECT_CONTENT, CHNL_LNK, GRP_LNK, REQST_CHANNEL, SUPPORT_CHAT_ID, SUPPORT_CHAT, MAX_B_TN, VERIFY, HOWTOVERIFY, SHORTLINK_API, SHORTLINK_URL, TUTORIAL, IS_TUTORIAL, PREMIUM_USER, PICS, SUBSCRIPTION, REFERAL_PREMEIUM_TIME, REFERAL_COUNT, PREMIUM_AND_REFERAL_MODE
from utils import get_settings, get_size, is_req_subscribed, is_subscribed, save_group_settings, temp, verify_user, check_token, check_verification, get_token, get_shortlink, get_tutorial
from database.connections_mdb import active_connection
# from plugins.pm_filter import ENABLE_SHORTLINK
import re, asyncio, os, sys
import json
import base64
logger = logging.getLogger(__name__)

TIMEZONE = "Asia/Kolkata"
BATCH_FILES = {}

@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        buttons = [[
                    InlineKeyboardButton('☒ Δᴅᴅ Mᴇ Tᴏ Yᴏᴜʀ Gʀᴏᴜᴩ ☒', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
                ],[
                    InlineKeyboardButton('📓 Gᴜɪᴅᴇ 📓', url="https://t.me/{temp.U_NAME}?start=help")
                  ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply(script.GSTART_TXT.format(message.from_user.mention if message.from_user else message.chat.title, temp.U_NAME, temp.B_NAME), reply_markup=reply_markup, disable_web_page_preview=True)
        await asyncio.sleep(2) # 😢 https://github.com/EvamariaTG/EvaMaria/blob/master/plugins/p_ttishow.py#L17 😬 wait a bit, before checking.
        if not await db.get_chat(message.chat.id):
            total=await client.get_chat_members_count(message.chat.id)
            await client.send_message(LOG_CHANNEL, script.LOG_TEXT_G.format(message.chat.title, message.chat.id, total, "Unknown"))       
            await db.add_chat(message.chat.id, message.chat.title)
        return 
    if not await db.is_user_exist(message.from_user.id):
        await message.reply_text(
             text="<b>Yᴏᴜ ʜᴀᴠᴇɴ'ᴛ ꜱᴛᴀʀᴛᴇᴅ ᴏᴜʀ ᴍᴀɪɴ ʙᴏᴛ ᴩʟᴇᴀꜱᴇ ꜱᴛᴀʀᴛ ɪᴛ..! \nJᴜꜱᴛ ᴄʟɪᴄᴋ ᴏɴ ꜱᴛᴀʀᴛ ɪɴ <a href='https://t.me/MovSearch_X_Bot?start=goon'>@MovSearch_X_Bot</a> ᴛᴏ ɢᴇᴛ ꜰɪʟᴇ...!</b>",   
             reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Gᴇᴛ Fɪʟᴇ", url="https://t.me/MovSearch_X_Bot?start=goon")]])
        )
        return
    if len(message.command) != 2:
        buttons = [[
                    InlineKeyboardButton('☒ Δᴅᴅ Mᴇ Tᴏ Yᴏᴜʀ Gʀᴏᴜᴩ ☒', url=f'http://telegram.me/{temp.U_NAME}?startgroup=true')
                ],[
                    InlineKeyboardButton('⌬ ᴇΔʀɴ ꪑᴏꫝᴇꪗ ⌬', callback_data="shortlink_info"),
                    InlineKeyboardButton('⚝ ᴜᴘᦔΔᴛꫀ𝘴 ⚝', callback_data='channels')
                ],[
                    InlineKeyboardButton('⇱  ᴄ0ᴍᴍᴀɴᴅꜱ  ⇲', callback_data='help'),
                    InlineKeyboardButton('⊛ Δʙᴏᴜᴛ ⊛', callback_data='about')
                ],[
                    InlineKeyboardButton("◎ Sꪊʙꜱᴄʀɪᴩᴛɪꪮɴ - Fяᴇᴇ Δɴ' Pᴀɪᴅ ◎", callback_data="premium_info")
                  ]]
       
        m=await message.reply_text("<i>ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ <b>ᴍʀ ᴍᴏᴠɪᴇꜱ ꜰɪʟᴇ ʙᴏᴛ</b>.\nʜᴏᴘᴇ ʏᴏᴜ'ʀᴇ ᴅᴏɪɴɢ ᴡᴇʟʟ...</i>")
        await asyncio.sleep(0.6)
        await m.delete()
        await message.reply_text(
             text="<b>Sᴇɴᴅ Mᴏᴠɪᴇ Nᴀᴍᴇ Hᴇʀᴇ..!😊 \n@MovSearch_X1_Bot</b>",   
             reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🥶 ʀᴇǫᴜᴇsᴛ ʜᴇʀᴇ 🥶", url=f"https://t.me/+5n7vViwKXJJiMjhl")]])
        )
        return
        
    if AUTH_CHANNEL:
        try:
            # Fetch subscription statuses once
            is_req_sub = await is_req_subscribed(client, message)
            is_sub = await is_subscribed(client, message)

            if not (is_req_sub and is_sub):
                try:
                    invite_link = await client.create_chat_invite_link(int(AUTH_CHANNEL), creates_join_request=True)
                except ChatAdminRequired:
                    logger.error("Make sure Bot is admin in Forcesub channel")
                    return
                
                btn = []

                # Only add buttons if the user is not subscribed
                if not is_req_sub:
                    btn.append([InlineKeyboardButton("⊛ Jᴏɪɴ Uᴘᴅᴀᴛᴇꜱ CʜᴀɴɴᴇL ¹⊛", url=invite_link.invite_link)])

                if not is_sub:
                    btn.append([InlineKeyboardButton("⊛ Jᴏɪɴ Uᴘᴅᴀᴛᴇꜱ CʜᴀɴɴᴇL ²⊛", url="https://t.me/Bot_Cracker")])

                if len(message.command) > 1 and message.command[1] != "subscribe":
                    try:
                        kk, file_id = message.command[1].split("_", 1)
                        btn.append([InlineKeyboardButton("↻ Tʀʏ Aɢᴀɪɴ ↻", callback_data=f"checksub#{kk}#{file_id}")])
                    except (IndexError, ValueError):
                        btn.append([InlineKeyboardButton("↻ Tʀʏ Aɢᴀɪɴ ↻", url=f"https://t.me/{temp.U_NAME}?start={message.command[1]}")])

                await client.send_message(
                    chat_id=message.from_user.id,
                    text="Jᴏɪɴ Oᴜʀ Uᴘᴅᴀᴛᴇꜱ Cʜᴀɴɴᴇʟ ᴀɴᴅ Tʜᴇɴ Cʟɪᴄᴋ Oɴ ᴛʀʏ ᴀɢᴀɪɴ ᴛᴏ ɢᴇᴛ ʏᴏᴜʀ ʀᴇǫᴜᴇꜱᴛᴇᴅ ꜰɪʟᴇ.",
                    reply_markup=InlineKeyboardMarkup(btn),
                    parse_mode=enums.ParseMode.MARKDOWN
                )
                return
        except Exception as e:
            logger.error(f"Error in subscription check: {e}")
            await client.send_message(chat_id=1733124290, text="FORCE  SUB  ERROR ......  CHECK LOGS")

        
    if len(message.command) == 2 and message.command[1] in ["subscribe", "error", "okay", "help"]:
        buttons = [[
                    InlineKeyboardButton('☒ Δᴅᴅ Mᴇ Tᴏ Yᴏᴜʀ Gʀᴏᴜᴩ ☒', url=f'http://telegram.me/{temp.U_NAME}?startgroup=true')
                ],[
                    InlineKeyboardButton('⌬ ᴇΔʀɴ ꪑᴏꫝᴇꪗ ⌬', callback_data="shortlink_info"),
                    InlineKeyboardButton('⚝ ᴜᴘᦔΔᴛꫀ𝘴 ⚝', callback_data='channels')
                ],[
                    InlineKeyboardButton('⇱  ᴄ0ᴍᴍᴀɴᴅꜱ  ⇲', callback_data='help'),
                    InlineKeyboardButton('⊛ Δʙᴏᴜᴛ ⊛', callback_data='about')
                ],[
                    InlineKeyboardButton("◎ Sꪊʙꜱᴄʀɪᴩᴛɪꪮɴ - Fяᴇᴇ Δɴ' Pᴀɪᴅ ◎", callback_data="premium_info")
                  ]]
        m=await message.reply_text("<i>ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ <b>ᴍʀ ᴍᴏᴠɪᴇꜱ ꜰɪʟᴇ ʙᴏᴛ</b>.\nʜᴏᴘᴇ ʏᴏᴜ'ʀᴇ ᴅᴏɪɴɢ ᴡᴇʟʟ...</i>")
        await asyncio.sleep(0.6)
        await m.delete()
        await message.reply_text(
             text="<b>Sᴇɴᴅ Mᴏᴠɪᴇ Nᴀᴍᴇ Hᴇʀᴇ..!😊 \n@MovSearch_X_Bot</b>",   
             reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🥶 ʀᴇǫᴜᴇsᴛ ʜᴇʀᴇ 🥶", url=f"https://t.me/+5n7vViwKXJJiMjhl")]])
        )
        return
    data = message.command[1]
    if data.split("-", 1)[0] == "SyD":
        user_id = int(data.split("-", 1)[1])
        syd = await referal_add_user(user_id, message.from_user.id)
        if syd and PREMIUM_AND_REFERAL_MODE == True:
            await message.reply(f"<i>Yσᴜ ʜᴀᴠᴇ ꜱᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙʏ ʙᴏᴛ ᴜꜱɪɴɢ ᴛʜᴇ <b>ʀᴇꜰʀʀᴇʟ ʟɪɴᴋ</b> ᴏꜰ ᴀ ᴜꜱᴇʀ \n\nSᴇɴᴅ /start Δɢᴀɪɴ To Uꜱᴇ Tʜᴇ Бᴏᴛ</i>")
            num_referrals = await get_referal_users_count(user_id)
            await client.send_message(chat_id = user_id, text = "<i>{} Sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ ᴡɪᴛʜ ʏᴏᴜʀ ʀᴇꜰᴇʀʀᴇʟ ʟɪɴᴋ\n\nTᴏᴛᴀʟ Rᴇꜰᴇʀꜱ - {}/10</i>".format(message.from_user.mention, num_referrals))
            if num_referrals == REFERAL_COUNT:
                time = REFERAL_PREMEIUM_TIME       
                seconds = await get_seconds(time)
                if seconds > 0:
                    expiry_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
                    user_data = {"id": user_id, "expiry_time": expiry_time} 
                    await db.update_user(user_data)  # Use the update_user method to update or insert user data
                    await delete_all_referal_users(user_id)
                    await client.send_message(chat_id = user_id, text = "<i>You Have Successfully Completed Total Referal.\n\nYou Added In Premium For {}</i>".format(REFERAL_PREMEIUM_TIME))
                    return 
        else:
             buttons = [[
                 InlineKeyboardButton('⤬ Aᴅᴅ Mᴇ Tᴏ Yᴏᴜʀ Gʀᴏᴜᴘ ⤬', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
             ],[
                 InlineKeyboardButton('✧ ᴇΔʀꪀ ꪑᴏꫝᴇꪗ ✧', callback_data="shortlink_info"),
                 InlineKeyboardButton('⌬ Mᴏᴠɪᴇ Gʀᴏᴜᴘ', url=GRP_LNK)
             ],[
                 InlineKeyboardButton('〄 Hᴇʟᴘ', callback_data='help'),
                 InlineKeyboardButton('⍟ Aʙᴏᴜᴛ', callback_data='about')
             ],[
                 InlineKeyboardButton('✇ Jᴏɪɴ Uᴘᴅᴀᴛᴇs Cʜᴀɴɴᴇʟ ✇', url=CHNL_LNK)
             ]]
             reply_markup = InlineKeyboardMarkup(buttons)
             m=await message.reply_sticker("CAACAgUAAxkBAAEDePpmZFgm0WcwNuK93-xyFlxcuERvuAACuRMAAlxlKFdLjAYn7DUluh4E") 
             await asyncio.sleep(1)
             await m.delete()
             await message.reply_photo(
                  photo=random.choice(PICS),
                  caption=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
                  reply_markup=reply_markup,
                  parse_mode=enums.ParseMode.HTML
             )
             return 
    

    
                    [
                        [
                            InlineKeyboardButton('📁 ᴅᴏᴡɴʟᴏᴀᴅ 📁', url=g)
                        ], [
                            InlineKeyboardButton('⚡ ʜᴏᴡ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ⚡', url=await get_tutorial(chat_id))
                        ], [
                            InlineKeyboardButton('✨ ʙᴜʏ ꜱᴜʙꜱᴄʀɪᴘᴛɪᴏɴ : ʀᴇᴍᴏᴠᴇ ᴀᴅꜱ ✨', callback_data="seeplans")                            
                        ]
                    ]
                )
            )
            await asyncio.sleep(600)
            await k.edit("<b>ʏᴏᴜʀ ᴍᴇꜱꜱᴀɢᴇ ɪꜱ ᴅᴇʟᴇᴛᴇᴅ !\nᴋɪɴᴅʟʏ ꜱᴇᴀʀᴄʜ ᴀɢᴀɪɴ.</b>")
            return


from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from urllib.parse import quote_plus

@Client.on_message(filters.private & (filters.document | filters.video))
async def link(client, message: Message):
    try:
        user_id = message.from_user.id
        username = message.from_user.mention
        file_id = message.document.file_id if message.document else message.video.file_id

        # Send file to log channel
        log_msg = await client.send_cached_media(
            chat_id=LOG_CHANNEL,
            file_id=file_id,
        )

        # Prepare file info and links
        file_name = message.document.file_name if message.document else message.video.file_name
        encoded_name = quote_plus(file_name)
        lazy_stream = f"{URL}watch/{str(log_msg.id)}/{encoded_name}?hash={get_hash(log_msg)}"
        lazy_download = f"{URL}{str(log_msg.id)}/{encoded_name}?hash={get_hash(log_msg)}"

   
        # Prepare buttons
        
        buttons = [[
            InlineKeyboardButton("〄 Ғᴀꜱᴛ Dᴏᴡɴʟᴏᴀᴅ", url=hp_link),
            InlineKeyboardButton("Wᴀᴛᴄʜ Oɴʟɪɴᴇ 〄", url=ph_link)
        ], [
            InlineKeyboardButton('! Hᴏᴡ ᴛᴏ ᴏᴘᴇɴ ʟɪɴK !', url=STREAMHTO)
        ]]

        # Send links to user
        await message.reply_text(
            text=f"<b>Here is your download and stream link:</b>",
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True
        )

        # Log it
        await log_msg.reply_text(
            text=f"#LinkGenerated\n\nIᴅ : <code>{user_id}</code>\nUꜱᴇʀɴᴀᴍᴇ : {username}\n\nNᴀᴍᴇ : {file_name}",
            quote=True,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("〄 Ғᴀꜱᴛ Dᴏᴡɴʟᴏᴀᴅ", url=hp_link),
                InlineKeyboardButton('Wᴀᴛᴄʜ Oɴʟɪɴᴇ 〄', url=ph_link)
            ]])
        )

    except Exception as e:
        print(e)
        await message.reply_text(f"⚠️ SOMETHING WENT WRONG \n\n{e}")
