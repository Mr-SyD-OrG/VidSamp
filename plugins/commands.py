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
from info import CHANNELS, ADMINS, AUTH_CHANNEL, URL, LOG_CHANNEL, PICS, BATCH_FILE_CAPTION, CUSTOM_FILE_CAPTION, PROTECT_CONTENT, CHNL_LNK, GRP_LNK, REQST_CHANNEL, SUPPORT_CHAT_ID, SUPPORT_CHAT, MAX_B_TN, VERIFY, HOWTOVERIFY, SHORTLINK_API, SHORTLINK_URL, TUTORIAL, IS_TUTORIAL, PREMIUM_USER, PICS, SUBSCRIPTION, REFERAL_PREMEIUM_TIME, REFERAL_COUNT, PREMIUM_AND_REFERAL_MODE
from utils import get_settings, get_size, is_req_subscribed, is_subscribed, save_group_settings, temp, verify_user, check_token, check_verification, get_token, get_shortlink, get_tutorial
from database.connections_mdb import active_connection
# from plugins.pm_filter import ENABLE_SHORTLINK
import re, asyncio, os, sys
import json
from util.file_properties import get_name, get_hash, get_media_file_size

import base64
logger = logging.getLogger(__name__)

TIMEZONE = "Asia/Kolkata"


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
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(message.from_user.id, message.from_user.mention))
 
    if len(message.command) != 2:
        buttons = [[
                    InlineKeyboardButton('✲ Uᴩᴅᴀᴛᴇꜱ', url='https://t.me/Bot_cracker'),
                    InlineKeyboardButton('Mᴏᴠɪᴇꜱ ✲', url='https://t.me/Mod_Moviez_X')
                ],[
                    InlineKeyboardButton('⌬ Hᴇʟᴩ ⌬', callback_data='help')
                ], [
                    InlineKeyboardButton('⚝ Oᴡɴᴇʀ', user_id=1733124290),
                    InlineKeyboardButton("Bᴏᴛꜱ ⚝", url="https://t.me/Bot_Cracker/17")
                ],[
                    InlineKeyboardButton('◎ Gʀᴏᴜᴩ ◎', url='https://t.me/+5n7vViwKXJJiMjhl')
                ]]
       
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML
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
                    InlineKeyboardButton('✲ Uᴩᴅᴀᴛᴇꜱ', url='https://t.me/Bot_cracker'),
                    InlineKeyboardButton('Mᴏᴠɪᴇꜱ ✲', url='https://t.me/Mod_Moviez_X')
                ],[
                    InlineKeyboardButton('⌬ Hᴇʟᴩ ⌬', callback_data='help')
                ],[
                    InlineKeyboardButton('⚝ Oᴡɴᴇʀ', user_id=1733124290),
                    InlineKeyboardButton('Bᴏᴛꜱ ⚝', url="https://t.me/Bot_Cracker/17")
                ],[
                    InlineKeyboardButton('◎ Gʀᴏᴜᴩ ◎', url='https://t.me/+5n7vViwKXJJiMjhl')
                ]]
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML
        )
        return
    


from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

@Client.on_message(filters.private & (filters.document | filters.video))
async def link(client, message):
    try:
        user_id = message.from_user.id
        username = message.from_user.mention
        file_id = message.document.file_id if message.document else message.video.file_id

        log_msg = await client.send_cached_media(
            chat_id=LOG_CHANNEL,
            file_id=file_id,
        )

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
                        btn.append([InlineKeyboardButton("↻ Tʀʏ Aɢᴀɪɴ ↻", callback_data=f"checksyd#{log_msg.id}")])
                        
                    await client.send_message(
                        chat_id=message.from_user.id,
                        text="Jᴏɪɴ Oᴜʀ Uᴘᴅᴀᴛᴇꜱ Cʜᴀɴɴᴇʟ ᴀɴᴅ Tʜᴇɴ Cʟɪᴄᴋ Oɴ ᴛʀʏ ᴀɢᴀɪɴ ᴛᴏ ɢᴇᴛ ʏᴏᴜʀ ʀᴇǫᴜᴇꜱᴛᴇᴅ ꜰɪʟᴇ.",
                        reply_markup=InlineKeyboardMarkup(btn),
                        parse_mode=enums.ParseMode.MARKDOWN
                    )
                    await db.store_file_id_if_not_subscribed(user_id, log_msg.id)
                    return
            except Exception as e:
                logger.error(f"Error in subscription check: {e}")
                await client.send_message(chat_id=1733124290, text="FORCE  SUB  ERROR ......  CHECK LOGS")

        # Send file to log channel
        
        # Prepare file info and links
        file_name = message.document.file_name if message.document else message.video.file_name
        encoded_name = quote_plus(file_name)
        stream = f"{URL}watch/{str(log_msg.id)}/{encoded_name}?hash={get_hash(log_msg)}"
        download = f"{URL}{str(log_msg.id)}/{encoded_name}?hash={get_hash(log_msg)}"

   
        # Prepare buttons
        
        buttons = [[
            InlineKeyboardButton("〄 Ғᴀꜱᴛ Dᴏᴡɴʟᴏᴀᴅ", url=download),
            InlineKeyboardButton("Wᴀᴛᴄʜ Oɴʟɪɴᴇ 〄", url=stream)
        ], [
            InlineKeyboardButton('! Sᴜᴩᴩᴏʀᴛ Uꜱ !', url="https://t.me/Mod_Moviez_X")
        ]]

        # Send links to user
        await message.reply_text(
            text=f"<b>Hᴇʀᴇ ɪꜱ ʏᴏᴜʀ ᴅᴏᴡɴʟᴏᴀᴅ ᴀɴᴅ ꜱᴛʀᴇᴀᴍ ʟɪɴᴋ:\n\n✧ ᴡᴀᴛᴄʜ ᴏɴʟɪɴᴇ <code>{stream}</code>\n✧ ꜰᴀꜱᴛ ᴅᴏᴡɴʟᴏᴀᴅ: <code>{download}</code>\n\n<blockquote>♻️ ᴛʜɪs ʟɪɴᴋ ɪs ᴘᴇʀᴍᴀɴᴇɴᴛ ᴀɴᴅ ᴡᴏɴ'ᴛ ɢᴇᴛs ᴇxᴘɪʀᴇᴅ [ɪɴ ᴄᴀꜱᴇ ɪꜰ ᴇxᴩɪʀᴇᴅ ɢᴇɴᴇʀᴀᴛᴇ ᴀɢᴀɪɴ] ♻️</blockquote></b>",
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True
        )

        # Log it
        await log_msg.reply_text(
            text=f"#LinkGenerated\n\nIᴅ : <code>{user_id}</code>\nUꜱᴇʀɴᴀᴍᴇ : {username}\n\nNᴀᴍᴇ : {file_name}",
            quote=True,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("〄 Ғᴀꜱᴛ Dᴏᴡɴʟᴏᴀᴅ", url=download),
                InlineKeyboardButton("Wᴀᴛᴄʜ Oɴʟɪɴᴇ 〄", url=stream)
            ]])
        )

    except Exception as e:
        print(e)
        await message.reply_text(f"⚠️ SOMETHING WENT WRONG \n\n{e}")



@Client.on_callback_query(filters.regex(r"checksyd"))
async def check_subscription_callback(client, query):
    try:
        file_id = query.data.split("#")[1]
        user_id = query.from_user.id
        is_req_sub = await is_req_subscribed(client, query)
        is_sub = await is_subscribed(client, query)
        if not (is_req_sub and is_sub):
            await query.answer("Jᴏɪɴ ᴏᴜʀ ᴜᴘᴅᴀᴛᴇꜱ ᴄʜᴀɴɴᴇʟ ᴍᴀʜɴ! ᴩʟᴇᴀꜱᴇ... 🥺", show_alert=True)
            return

        doc = await client.get_messages(LOG_CHANNEL, int(file_id))
        file_name = doc.document.file_name if doc.document else doc.video.file_name
        encoded_name = quote_plus(file_name)

        stream = f"{URL}watch/{msg_id}/{encoded_name}?hash={get_hash(doc)}"
        download = f"{URL}{msg_id}/{encoded_name}?hash={get_hash(doc)}"

        buttons = [[
            InlineKeyboardButton("〄 Ғᴀꜱᴛ Dᴏᴡɴʟᴏᴀᴅ", url=download),
            InlineKeyboardButton("Wᴀᴛᴄʜ Oɴʟɪɴᴇ 〄", url=stream)
        ]]

        await query.message.edit_text(
            text=f"<b>Hᴇʀᴇ ɪꜱ ʏᴏᴜʀ ᴅᴏᴡɴʟᴏᴀᴅ ᴀɴᴅ ꜱᴛʀᴇᴀᴍ ʟɪɴᴋ:\n\n✧ ᴡᴀᴛᴄʜ ᴏɴʟɪɴᴇ <code>{stream}</code>\n✧ ꜰᴀꜱᴛ ᴅᴏᴡɴʟᴏᴀᴅ: <code>{download}</code>\n\n<blockquote>♻️ ᴛʜɪs ʟɪɴᴋ ɪs ᴘᴇʀᴍᴀɴᴇɴᴛ ᴀɴᴅ ᴡᴏɴ'ᴛ ɢᴇᴛs ᴇxᴘɪʀᴇᴅ [ɪɴ ᴄᴀꜱᴇ ɪꜰ ᴇxᴩɪʀᴇᴅ ɢᴇɴᴇʀᴀᴛᴇ ᴀɢᴀɪɴ] ♻️</blockquote></b>",
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True
        )

        # Remove file_id from DB if stored
        

    except Exception as e:
        await query.message.edit_text(f"⚠️ Failed to generate link\n\n{e}")


from pyrogram import Client, filters, enums
from pyrogram.types import ChatJoinRequest
from database.users_chats_db import db
from info import ADMINS, AUTH_CHANNEL

@Client.on_chat_join_request(filters.chat(AUTH_CHANNEL))
async def join_reqs(client, message: ChatJoinRequest):
  user_id = message.from_user.id
  if not await db.find_join_req(user_id):
    await db.add_join_req(user_id)
    file_id = await db.get_stored_file_id(user_id)
    if not file_id:
        try:
            await client.send_message(user_id, "<b> Tʜᴀɴᴋꜱ ɢᴏᴛ ᴏɴᴇ ᴩʟᴇᴀꜱᴇ <u>ᴄᴏɴᴛɪɴᴜᴇ... </u>⚡ </b>")
        except:
            pass
        return
    doc = await client.get_messages(LOG_CHANNEL, int(file_id))
    file_name = doc.document.file_name if doc.document else doc.video.file_name
    encoded_name = quote_plus(file_name)

    stream = f"{URL}watch/{file_id}/{encoded_name}?hash={get_hash(doc)}"
    download = f"{URL}{file_id}/{encoded_name}?hash={get_hash(doc)}"

    buttons = [[
        InlineKeyboardButton("〄 Ғᴀꜱᴛ Dᴏᴡɴʟᴏᴀᴅ", url=download),
        InlineKeyboardButton("Wᴀᴛᴄʜ Oɴʟɪɴᴇ 〄", url=stream)
    ]]

    await client.send_message(
        user_id,
        text=f"<b>Hᴇʀᴇ ɪꜱ ʏᴏᴜʀ ᴅᴏᴡɴʟᴏᴀᴅ ᴀɴᴅ ꜱᴛʀᴇᴀᴍ ʟɪɴᴋ:\n\n✧ ᴡᴀᴛᴄʜ ᴏɴʟɪɴᴇ <code>{stream}</code>\n✧ ꜰᴀꜱᴛ ᴅᴏᴡɴʟᴏᴀᴅ: <code>{download}</code>\n\n<blockquote>♻️ ᴛʜɪs ʟɪɴᴋ ɪs ᴘᴇʀᴍᴀɴᴇɴᴛ ᴀɴᴅ ᴡᴏɴ'ᴛ ɢᴇᴛs ᴇxᴘɪʀᴇᴅ [ɪɴ ᴄᴀꜱᴇ ɪꜰ ᴇxᴩɪʀᴇᴅ ɢᴇɴᴇʀᴀᴛᴇ ᴀɢᴀɪɴ] ♻️</blockquote></b>",
        reply_markup=InlineKeyboardMarkup(buttons),
        disable_web_page_preview=True
    )
    await db.remove_stored_file_id(user_id)
    

@Client.on_message(filters.command("delreq") & filters.private & filters.user(ADMINS))
async def del_requests(client, message):
    await db.del_join_req()    
    await message.reply("<b>⚙ ꜱᴜᴄᴄᴇꜱꜱғᴜʟʟʏ ᴄʜᴀɴɴᴇʟ ʟᴇғᴛ ᴜꜱᴇʀꜱ ᴅᴇʟᴇᴛᴇᴅ</b>")
