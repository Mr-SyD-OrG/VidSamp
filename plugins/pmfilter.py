# Kanged From @TroJanZheX
# Thanks @SyD_XyZ
import asyncio, re, ast, math, random, pytz
from datetime import datetime, timedelta, date, time
lock = asyncio.Lock()
from database.users_chats_db import db
from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from Script import script
import pyrogram
from database.connections_mdb import active_connection, all_connections, delete_connection, if_active, make_active, \
    make_inactive
from urllib.parse import quote_plus
from info import *
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid
from utils import get_size, is_req_subscribed, get_poster, search_gagala, temp, get_settings, save_group_settings, get_shortlink, get_tutorial, send_all, get_cap, encode_file_name
from database.users_chats_db import db
from database.ia_filterdb import Media, get_file_details, get_search_results, get_bad_files
from database.filters_mdb import (
    del_all,
    find_filter,
    get_filters,
)
from database.gfilters_mdb import (
    find_gfilter,
    get_gfilters,
    del_allg
)
import logging
from urllib.parse import quote_plus
from util.file_properties import get_name, get_hash, get_media_file_size

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

import requests
import string
import tracemalloc
# Enable tracemalloc
tracemalloc.start()

TIMEZONE = "Asia/Kolkata"
BUTTON = {}
BUTTONS = {}
FRESH = {}
BUTTONS0 = {}
BUTTONS1 = {}
BUTTONS2 = {}
SPELL_CHECK = {}
# ENABLE_SHORTLINK = ""

def generate_random_alphanumeric():
    """Generate a random 8-letter alphanumeric string."""
    characters = string.ascii_letters + string.digits
    random_chars = ''.join(random.choice(characters) for _ in range(8))
    return random_chars
  
def get_shortlink_sync(url):
    try:
        rget = requests.get(f"https://{STREAM_SITE}/api?api={STREAM_API}&url={url}&alias={generate_random_alphanumeric()}")
        rjson = rget.json()
        if rjson["status"] == "success" or rget.status_code == 200:
            return rjson["shortenedUrl"]
        else:
            return url
    except Exception as e:
        print(f"Error in get_shortlink_sync: {e}")
        return url

async def get_shortlink(url):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, get_shortlink_sync, url)


    
#@Client.on_message(filters.private & filters.text & filters.incoming)
async def pm_text(bot, message):
    content = message.text
    if content.startswith("/") or content.startswith("#"): return  # ignore commands and hashtags
    
    await message.reply_text(
          text="<i><b>Sᴇɴᴅ ꜰɪʟᴇ ᴛᴏ ɢᴇᴛ ᴡᴀᴛᴄʜ ᴏɴʟɪɴᴇ ᴀɴᴅ ꜰᴀꜱᴛ ᴅᴏᴡɴʟᴏᴀᴅ ʟɪɴᴋ.</b></i>",   
          reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🥶 ʀᴇǫᴜᴇsᴛ ʜᴇʀᴇ 🥶", url=f"https://t.me/MovSearch_X1_Bot")]])
    )
    return
    
@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):
    ident, req, key, offset = query.data.split("_")
    curr_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    try:
        offset = int(offset)
    except:
        offset = 0
    if BUTTONS.get(key)!=None:
        search = BUTTONS.get(key)
    else:
        search = FRESH.get(key)
    if not search:
        await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name),show_alert=True)
        return

    files, n_offset, total = await get_search_results(query.message.chat.id, search, offset=offset, filter=True)
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return
    temp.GETALL[key] = files
    temp.SHORT[query.from_user.id] = query.message.chat.id
    settings = await get_settings(query.message.chat.id)
    pre = 'filep' if settings['file_secure'] else 'file'
    if settings['button']:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"📁 {get_size(file.file_size)} ▷ {' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@') and not x.startswith('www.'), file.file_name.split()))}", url=f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}"
                ),
            ]
            for file in files
        ]


        btn.insert(0, 
            [
                InlineKeyboardButton("⇈ ꜱᴇʟᴇᴄᴛ ᴏᴘᴛɪᴏɴꜱ ʜᴇʀᴇ ⇈", 'reqinfo')
            ]
        )
        btn.insert(0, 
            [
                InlineKeyboardButton(f'ǫᴜᴀʟɪᴛʏ', callback_data=f"qualities#{key}"),
                InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇ", callback_data=f"languages#{key}"),
                InlineKeyboardButton("ꜱᴇᴀsᴏɴ",  callback_data=f"seasons#{key}")
            ]
        )
        btn.insert(0, [
            InlineKeyboardButton("𓅪 ꜱᴇɴᴅ ᴀʟʟ ꜰɪʟᴇꜱ 𓅪", url=f"https://telegram.me/{temp.U_NAME}?start=sendfiles_{key}")
        ])

    else:
        btn = []
        btn.insert(0, 
            [
                InlineKeyboardButton("⇈ ꜱᴇʟᴇᴄᴛ ᴏᴘᴛɪᴏɴꜱ ʜᴇʀᴇ ⇈", 'reqinfo')
            ]
        )
        btn.insert(0, 
            [
                InlineKeyboardButton(f'Qᴜᴀʟɪᴛʏ', callback_data=f"qualities#{key}"),
                InlineKeyboardButton("Lᴀɴɢᴜᴀɢᴇ", callback_data=f"languages#{key}"),
                InlineKeyboardButton("Sᴇᴀsᴏɴ",  callback_data=f"seasons#{key}")
            ]
        )
        btn.insert(0, [
            InlineKeyboardButton("𓅪 ꜱᴇɴᴅ ᴀʟʟ ꜰɪʟᴇꜱ 𓅪", url=f"https://telegram.me/{temp.U_NAME}?start=sendfiles_{key}")
        ])

    try:
        if settings['max_btn']:
            if 0 < offset <= 10:
                off_set = 0
            elif offset == 0:
                off_set = None
            else:
                off_set = offset - 10
            if n_offset == 0:
                btn.append(
                    [InlineKeyboardButton("⋞ ʙΔᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}"), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages")]
                )
            elif off_set is None:
                btn.append([InlineKeyboardButton("ᴘᴀGᴇ", callback_data="pages"), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"), InlineKeyboardButton("ɴᴇxᴛ ⋟", callback_data=f"next_{req}_{key}_{n_offset}")])
            else:
                btn.append(
                    [
                        InlineKeyboardButton("⋞ ʙΔᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}"),
                        InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"),
                        InlineKeyboardButton("ɴᴇXᴛ ⋟", callback_data=f"next_{req}_{key}_{n_offset}")
                    ],
                )
        else:
            if 0 < offset <= int(MAX_B_TN):
                off_set = 0
            elif offset == 0:
                off_set = None
            else:
                off_set = offset - int(MAX_B_TN)
            if n_offset == 0:
                btn.append(
                    [InlineKeyboardButton("⋞ ʙΔᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}"), InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages")]
                )
            elif off_set is None:
                btn.append([InlineKeyboardButton("ᴘᴀGᴇ", callback_data="pages"), InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages"), InlineKeyboardButton("ɴᴇxᴛ ⋟", callback_data=f"next_{req}_{key}_{n_offset}")])
            else:
                btn.append(
                    [
                        InlineKeyboardButton("⋞ ʙΔᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}"),
                        InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages"),
                        InlineKeyboardButton("ɴᴇXᴛ ⋟", callback_data=f"next_{req}_{key}_{n_offset}")
                    ],
                )
    except KeyError:
        await save_group_settings(query.message.chat.id, 'max_btn', True)
        if 0 < offset <= 10:
            off_set = 0
        elif offset == 0:
            off_set = None
        else:
            off_set = offset - 10
        if n_offset == 0:
            btn.append(
                [InlineKeyboardButton("⋞ ʙΔᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}"), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages")]
            )
        elif off_set is None:
            btn.append([InlineKeyboardButton("ᴘᴀGᴇ", callback_data="pages"), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"), InlineKeyboardButton("ɴᴇxᴛ ⋟", callback_data=f"next_{req}_{key}_{n_offset}")])
        else:
            btn.append(
                [
                    InlineKeyboardButton("⋞ ʙΔᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}"),
                    InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"),
                    InlineKeyboardButton("ɴᴇXᴛ ⋟", callback_data=f"next_{req}_{key}_{n_offset}")
                ],
            )
    if not settings["button"]:
        cur_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
        time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(curr_time.second+(curr_time.microsecond/1000000)))
        remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
        cap = await get_cap(settings, remaining_seconds, files, query, total, search)
        try:
            await query.message.edit_text(text=cap, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)
        except MessageNotModified:
            pass
    else:
        try:
            await query.edit_message_reply_markup(
                reply_markup=InlineKeyboardMarkup(btn)
            )
        except MessageNotModified:
            pass
    await query.answer()

@Client.on_callback_query(filters.regex(r"^spol"))
async def advantage_spoll_choker(bot, query):
    _, user, movie_ = query.data.split('#')
    movies = SPELL_CHECK.get(query.message.reply_to_message.id)
    if not movies:
        return await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    if int(user) != 0 and query.from_user.id != int(user):
        return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    if movie_ == "close_spellcheck":
        return await query.message.delete()
    movie = movies[(int(movie_))]
    movie = re.sub(r"[:\-]", " ", movie)
    movie = re.sub(r"\s+", " ", movie).strip()
    await query.answer(script.TOP_ALRT_MSG)
    gl = await global_filters(bot, query.message, text=movie)
    if gl == False:
        k = await manual_filters(bot, query.message, text=movie)
        if k == False:
            files, offset, total_results = await get_search_results(query.message.chat.id, movie, offset=0, filter=True)
            if files:
                k = (movie, files, offset, total_results)
                await auto_filter(bot, query, k)
            else:
                reqstr1 = query.from_user.id if query.from_user else 0
                reqstr = await bot.get_users(reqstr1)
                if NO_RESULTS_MSG:
                    await bot.send_message(chat_id=6727173021, text=movie)
                    await bot.send_message(chat_id=LOG_CHANNEL, text=(script.NORSLTS.format(reqstr.id, reqstr.mention, movie)))
                k = await query.message.edit(script.MVE_NT_FND)
                await asyncio.sleep(10)
                await k.delete()
#Qualities 
@Client.on_callback_query(filters.regex(r"^qualities#"))
async def qualities_cb_handler(client: Client, query: CallbackQuery):

    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer(
                f"⚠️ ʜᴇʟʟᴏ {query.from_user.first_name},\nᴛʜɪꜱ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ᴍᴏᴠɪᴇ ʀᴇǫᴜᴇꜱᴛ,\nʀᴇǫᴜᴇꜱᴛ ʏᴏᴜʀ'ꜱ.... Pʟᴇᴀꜱᴇ... 💫",
                show_alert=True,
            )
    except:
        pass
    _, key = query.data.split("#")
    # if BUTTONS.get(key+"1")!=None:
    #     search = BUTTONS.get(key+"1")
    # else:
    #     search = BUTTONS.get(key)
    #     BUTTONS[key+"1"] = search
    search = FRESH.get(key)
    search = search.replace(' ', '_')
    btn = []
    for i in range(0, len(QUALITIES)-1, 2):
        btn.append([
            InlineKeyboardButton(
                text=QUALITIES[i].title(),
                callback_data=f"fq#{QUALITIES[i].lower()}#{key}"
            ),
            InlineKeyboardButton(
                text=QUALITIES[i+1].title(),
                callback_data=f"fq#{QUALITIES[i+1].lower()}#{key}"
            ),
        ])

    btn.insert(
        0,
        [
            InlineKeyboardButton(
                text="⇊ ꜱᴇʟᴇᴄᴛ ǫᴜᴀʟɪᴛʏ ⇊", callback_data="ident"
            )
        ],
    )
    req = query.from_user.id
    offset = 0
    btn.append([InlineKeyboardButton(text="↭ ʙᴀᴄᴋ ᴛᴏ ꜰɪʟᴇs ↭", callback_data=f"fq#homepage#{key}")])

    await query.edit_message_reply_markup(InlineKeyboardMarkup(btn))
 

@Client.on_callback_query(filters.regex(r"^fq#"))
async def filter_qualities_cb_handler(client: Client, query: CallbackQuery):
    _, qual, key = query.data.split("#")
    curr_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
    search = FRESH.get(key)
    search = search.replace("_", " ")
    baal = qual in search
    if baal:
        search = search.replace(qual, "")
    else:
        search = search
    req = query.from_user.id
    chat_id = query.message.chat.id
    message = query.message
    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer(
                f"⚠️ ʜᴇʟʟᴏ {query.from_user.first_name},\nᴛʜɪꜱ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ᴍᴏᴠɪᴇ ʀᴇǫᴜᴇꜱᴛ,\nʀᴇǫᴜᴇꜱᴛ ʏᴏᴜʀ'ꜱ...Pʟᴇᴀꜱᴇ... 💫",
                show_alert=True,
            )
    except:
        pass
    if qual != "homepage":
        search = f"{search} {qual}" 
    BUTTONS[key] = search

    files, offset, total_results = await get_search_results(chat_id, search, offset=0, filter=True)
    if not files:
        await query.answer("🚫 ɴᴏ ꜰɪʟᴇꜱ ᴡᴇʀᴇ ꜰᴏᴜɴᴅ 🚫 ʀᴇᴩᴏʀᴛ ᴛᴏ ᴛɢᴇ ᴀᴅᴍɪɴ.. 💥", show_alert=1)
        return
    temp.GETALL[key] = files
    settings = await get_settings(message.chat.id)
    pre = 'filep' if settings['file_secure'] else 'file'
    if settings["button"]:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"📁 {get_size(file.file_size)} ▷ {' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@') and not x.startswith('www.'), file.file_name.split()))}", url=f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}"
                ),
            ]
            for file in files
        ]
        btn.insert(0, 
            [
                InlineKeyboardButton("⇈ ꜱᴇʟᴇᴄᴛ ᴏᴘᴛɪᴏɴꜱ ʜᴇʀᴇ ⇈", 'reqinfo')
            ]
        )
        btn.insert(0, 
            [
                InlineKeyboardButton(f'Qᴜᴀʟɪᴛʏ', callback_data=f"qualities#{key}"),
                InlineKeyboardButton("Lᴀɴɢᴜᴀɢᴇ", callback_data=f"languages#{key}"),
                InlineKeyboardButton("Sᴇᴀsᴏɴ",  callback_data=f"seasons#{key}")
            ]
        )
        btn.insert(0, [
            InlineKeyboardButton("𓅪 ꜱᴇɴᴅ ᴀʟʟ ꜰɪʟᴇꜱ 𓅪", url=f"https://telegram.me/{temp.U_NAME}?start=sendfiles_{key}")
        ])

    else:
        btn = []
        btn.insert(0, 
            [
                InlineKeyboardButton("⇈ ꜱᴇʟᴇᴄᴛ ᴏᴘᴛɪᴏɴꜱ ʜᴇʀᴇ ⇈", 'reqinfo')
            ]
        )
        btn.insert(0, 
            [
                InlineKeyboardButton(f'Qᴜᴀʟɪᴛʏ', callback_data=f"qualities#{key}"),
                InlineKeyboardButton("Lᴀɴɢᴜᴀɢᴇ", callback_data=f"languages#{key}"),
                InlineKeyboardButton("Sᴇᴀsᴏɴ",  callback_data=f"seasons#{key}")
            ]
        )
        btn.insert(0, [
            InlineKeyboardButton("𓅪 ꜱᴇɴᴅ ᴀʟʟ ꜰɪʟᴇꜱ 𓅪", callback_data=f"sendfiles#{key}")
        ])

    if offset != "":
        try:
            if settings['max_btn']:
                btn.append(
                    [InlineKeyboardButton("ᴘᴀGᴇ", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="ɴᴇxᴛ ⋟",callback_data=f"next_{req}_{key}_{offset}")]
                )
    
            else:
                btn.append(
                    [InlineKeyboardButton("ᴘᴀGᴇ", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/int(MAX_B_TN))}",callback_data="pages"), InlineKeyboardButton(text="ɴᴇxᴛ ⋟",callback_data=f"next_{req}_{key}_{offset}")]
                )
        except KeyError:
            await save_group_settings(query.message.chat.id, 'max_btn', True)
            btn.append(
                [InlineKeyboardButton("ᴘᴀGᴇ", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="ɴᴇxᴛ ⋟",callback_data=f"next_{req}_{key}_{offset}")]
            )
    else:
        btn.append(
            [InlineKeyboardButton(text="↭ Nᴏ ᴍᴏʀᴇ ᴘᴀɢᴇꜱ ᴀᴠᴀɪʟᴀʙʟE ↭",callback_data="pages")]
        )
    
    if not settings["button"]:
        cur_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
        time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(curr_time.second+(curr_time.microsecond/1000000)))
        remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
        cap = await get_cap(settings, remaining_seconds, files, query, total_results, search)
        try:
            await query.message.edit_text(text=cap, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)
        except MessageNotModified:
            pass
    else:
        try:
            await query.edit_message_reply_markup(
                reply_markup=InlineKeyboardMarkup(btn)
            )
        except MessageNotModified:
            pass
    await query.answer()

#languages

@Client.on_callback_query(filters.regex(r"^languages#"))
async def languages_cb_handler(client: Client, query: CallbackQuery):
    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer(
                f"⚠️ ʜᴇʟʟᴏ {query.from_user.first_name},\nᴛʜɪꜱ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ᴍᴏᴠɪᴇ ʀᴇǫᴜᴇꜱᴛ,\nʀᴇǫᴜᴇꜱᴛ ʏᴏᴜʀ'ꜱ...",
                show_alert=True,
            )
    except:
        pass
    _, key = query.data.split("#")
    # if BUTTONS.get(key+"1")!=None:
    #     search = BUTTONS.get(key+"1")
    # else:
    #     search = BUTTONS.get(key)
    #     BUTTONS[key+"1"] = search
    search = FRESH.get(key)
    search = search.replace(' ', '_')
    btn = []
    for i in range(0, len(LANGUAGES)-1, 2):
        btn.append([
            InlineKeyboardButton(
                text=LANGUAGES[i].title(),
                callback_data=f"fl#{LANGUAGES[i].lower()}#{key}"
            ),
            InlineKeyboardButton(
                text=LANGUAGES[i+1].title(),
                callback_data=f"fl#{LANGUAGES[i+1].lower()}#{key}"
            ),
        ])

    btn.insert(
        0,
        [
            InlineKeyboardButton(
                text="⇊ ꜱᴇʟᴇᴄᴛ ʟᴀɴɢᴜᴀɢᴇ ⇊", callback_data="ident"
            )
        ],
    )
    req = query.from_user.id
    offset = 0
    btn.append([InlineKeyboardButton(text="↭ ʙΔᴄᴋ ᴛᴏ ꜰɪʟᴇs ​↭", callback_data=f"fl#homepage#{key}")])

    await query.edit_message_reply_markup(InlineKeyboardMarkup(btn))
    

@Client.on_callback_query(filters.regex(r"^fl#"))
async def filter_languages_cb_handler(client: Client, query: CallbackQuery):
    _, lang, key = query.data.split("#")
    curr_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
    search = FRESH.get(key)
    search = search.replace("_", " ")
    baal = lang in search
    if baal:
        search = search.replace(lang, "")
    else:
        search = search
    req = query.from_user.id
    chat_id = query.message.chat.id
    message = query.message
    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer(
                f"⚠️ Hᴇʟʟᴏ {query.from_user.first_name},\nᴛʜɪꜱ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ᴍᴏᴠɪᴇ ʀᴇǫᴜᴇꜱᴛ,\nʀᴇǫᴜᴇꜱᴛ ʏᴏᴜʀ'ꜱ... ᴩʟᴇᴀꜱᴇ.. 😇",
                show_alert=True,
            )
    except:
        pass
    if lang != "homepage":
        search = f"{search} {lang}" 
    BUTTONS[key] = search

    files, offset, total_results = await get_search_results(chat_id, search, offset=0, filter=True)
    if not files:
        await query.answer("🚫Sᴏʀʀʏ ɴᴏ ꜰɪʟᴇꜱ ᴡᴇʀᴇ ꜰᴏᴜɴᴅ 🚫 ʀᴇᴩᴏʀᴛ ᴛᴏ ᴛʜᴇ ᴏᴡɴᴇʀ..ɪᴍᴍᴇᴅɪᴀᴛᴇʟʏ.. 💥", show_alert=1)
        return
    temp.GETALL[key] = files
    settings = await get_settings(message.chat.id)
    pre = 'filep' if settings['file_secure'] else 'file'
    if settings["button"]:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"📁 {get_size(file.file_size)} ▷ {' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@') and not x.startswith('www.'), file.file_name.split()))}", url=f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}"
                ),
            ]
            for file in files
        ]
        btn.insert(0, 
            [
                InlineKeyboardButton("⇈ ꜱᴇʟᴇᴄᴛ ᴏᴘᴛɪᴏɴꜱ ʜᴇʀᴇ ⇈", 'reqinfo')
            ]
        )
        btn.insert(0, 
            [
                InlineKeyboardButton(f'Qᴜᴀʟɪᴛʏ', callback_data=f"qualities#{key}"),
                InlineKeyboardButton("Lᴀɴɢᴜᴀɢᴇ", callback_data=f"languages#{key}"),
                InlineKeyboardButton("Sᴇᴀsᴏɴ",  callback_data=f"seasons#{key}")
            ]
        )
        btn.insert(0, [
            InlineKeyboardButton("𓅪 ꜱᴇɴᴅ ᴀʟʟ ꜰɪʟᴇꜱ 𓅪", callback_data=f"sendfiles#{key}")
        ])

    else:
        btn = []
        btn.insert(0, 
            [
                InlineKeyboardButton("⇈ ꜱᴇʟᴇᴄᴛ ᴏᴘᴛɪᴏɴꜱ ʜᴇʀᴇ ⇈", 'reqinfo')
            ]
        )
        btn.insert(0, 
            [
                InlineKeyboardButton(f'Qᴜᴀʟɪᴛʏ', callback_data=f"qualities#{key}"),
                InlineKeyboardButton("Lᴀɴɢᴜᴀɢᴇ", callback_data=f"languages#{key}"),
                InlineKeyboardButton("Sᴇᴀsᴏɴ",  callback_data=f"seasons#{key}")
            ]
        )
        btn.insert(0, [
            InlineKeyboardButton("𓅪 ꜱᴇɴᴅ ᴀʟʟ ꜰɪʟᴇꜱ 𓅪", url=f"https://telegram.me/{temp.U_NAME}?start=sendfiles_{key}")
        ])

    if offset != "":
        try:
            if settings['max_btn']:
                btn.append(
                    [InlineKeyboardButton("ᴘᴀGᴇ", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="ɴᴇxᴛ ⋟",callback_data=f"next_{req}_{key}_{offset}")]
                )
    
            else:
                btn.append(
                    [InlineKeyboardButton("ᴘᴀGᴇ", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/int(MAX_B_TN))}",callback_data="pages"), InlineKeyboardButton(text="ɴᴇxᴛ ⋟",callback_data=f"next_{req}_{key}_{offset}")]
                )
        except KeyError:
            await save_group_settings(query.message.chat.id, 'max_btn', True)
            btn.append(
                [InlineKeyboardButton("ᴘᴀGᴇ", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="ɴᴇxᴛ ⋟",callback_data=f"next_{req}_{key}_{offset}")]
            )
    else:
        btn.append(
            [InlineKeyboardButton(text="↭ Nᴏ ᴍᴏʀᴇ ᴘᴀɢᴇꜱ ᴀᴠᴀɪʟᴀʙʟE ↭",callback_data="pages")]
        )
    
    if not settings["button"]:
        cur_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
        time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(curr_time.second+(curr_time.microsecond/1000000)))
        remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
        cap = await get_cap(settings, remaining_seconds, files, query, total_results, search)
        try:
            await query.message.edit_text(text=cap, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)
        except MessageNotModified:
            pass
    else:
        try:
            await query.edit_message_reply_markup(
                reply_markup=InlineKeyboardMarkup(btn)
            )
        except MessageNotModified:
            pass
    await query.answer()
    
    
    
@Client.on_callback_query(filters.regex(r"^seasons#"))
async def seasons_cb_handler(client: Client, query: CallbackQuery):
    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer(
                f"⚠️ ʜᴇʟʟᴏ {query.from_user.first_name},\nᴛʜɪꜱ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ᴍᴏᴠɪᴇ ʀᴇǫᴜᴇꜱᴛ,\nʀᴇǫᴜᴇꜱᴛ ʏᴏᴜʀ'ꜱ...",
                show_alert=True,
            )
    except:
        pass
    _, key = query.data.split("#")
    # if BUTTONS.get(key+"2")!=None:
    #     search = BUTTONS.get(key+"2")
    # else:
    #     search = BUTTONS.get(key)
    #     BUTTONS[key+"2"] = search
    search = FRESH.get(key)
    BUTTONS[key] = None
    search = search.replace(' ', '_')
    btn = []
    for i in range(0, len(SEASONS)-1, 2):
        btn.append([
            InlineKeyboardButton(
                text=SEASONS[i].title(),
                callback_data=f"fs#{SEASONS[i].lower()}#{key}"
            ),
            InlineKeyboardButton(
                text=SEASONS[i+1].title(),
                callback_data=f"fs#{SEASONS[i+1].lower()}#{key}"
            ),
        ])

    btn.insert(
        0,
        [
            InlineKeyboardButton(
                text="⇊ ꜱᴇʟᴇᴄᴛ ꜱᴇᴀꜱᴏɴ ⇊", callback_data="ident"
            )
        ],
    )
    req = query.from_user.id
    offset = 0
    btn.append([InlineKeyboardButton(text="↭ ʙΔᴄᴋ ᴛᴏ ꜰɪʟᴇs ​↭", callback_data=f"next_{req}_{key}_{offset}")])

    await query.edit_message_reply_markup(InlineKeyboardMarkup(btn))


@Client.on_callback_query(filters.regex(r"^fs#"))
async def filter_seasons_cb_handler(client: Client, query: CallbackQuery):
    _, seas, key = query.data.split("#")
    curr_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
    search = FRESH.get(key)
    search = search.replace("_", " ")
    sea = ""
    season_search = ["s01","s02", "s03", "s04", "s05", "s06", "s07", "s08", "s09", "s10", "season 01","season 02","season 03","season 04","season 05","season 06","season 07","season 08","season 09","season 10", "season 1","season 2","season 3","season 4","season 5","season 6","season 7","season 8","season 9"]
    for x in range (len(season_search)):
        if season_search[x] in search:
            sea = season_search[x]
            break
    if sea:
        search = search.replace(sea, "")
    else:
        search = search
    
    req = query.from_user.id
    chat_id = query.message.chat.id
    message = query.message
    try:
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer(
                f"⚠️ ʜᴇʟʟᴏ {query.from_user.first_name},\nᴛʜɪꜱ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ᴍᴏᴠɪᴇ ʀᴇǫᴜᴇꜱᴛ,\nʀᴇǫᴜᴇꜱᴛ ʏᴏᴜʀ'ꜱ...Pʟᴇᴀꜱᴇ..💫",
                show_alert=True,
            )
    except:
        pass
    
    searchagn = search
    search1 = search
    search2 = search
    search = f"{search} {seas}"
    BUTTONS0[key] = search
    
    files, _, _ = await get_search_results(chat_id, search, max_results=10)
    files = [file for file in files if re.search(seas, file.file_name, re.IGNORECASE)]
    
    seas1 = "s01" if seas == "season 1" else "s02" if seas == "season 2" else "s03" if seas == "season 3" else "s04" if seas == "season 4" else "s05" if seas == "season 5" else "s06" if seas == "season 6" else "s07" if seas == "season 7" else "s08" if seas == "season 8" else "s09" if seas == "season 9" else "s10" if seas == "season 10" else ""
    search1 = f"{search1} {seas1}"
    BUTTONS1[key] = search1
    files1, _, _ = await get_search_results(chat_id, search1, max_results=10)
    files1 = [file for file in files1 if re.search(seas1, file.file_name, re.IGNORECASE)]
    
    if files1:
        files.extend(files1)
    
    seas2 = "season 01" if seas == "season 1" else "season 02" if seas == "season 2" else "season 03" if seas == "season 3" else "season 04" if seas == "season 4" else "season 05" if seas == "season 5" else "season 06" if seas == "season 6" else "season 07" if seas == "season 7" else "season 08" if seas == "season 8" else "season 09" if seas == "season 9" else "s010"
    search2 = f"{search2} {seas2}"
    BUTTONS2[key] = search2
    files2, _, _ = await get_search_results(chat_id, search2, max_results=10)
    files2 = [file for file in files2 if re.search(seas2, file.file_name, re.IGNORECASE)]

    if files2:
        files.extend(files2)
        
    if not files:
        await query.answer("🚫 Nᴏ ꜰɪʟᴇꜱ ᴡᴇʀᴇ ꜰᴏᴜɴᴅ 🚫 Rᴇᴩᴏʀᴛ ᴛᴏ ᴏᴡɴᴇʀ ᴩʟᴇᴀꜱᴇ.. ⚡", show_alert=1)
        return
    temp.GETALL[key] = files
    settings = await get_settings(message.chat.id)
    pre = 'filep' if settings['file_secure'] else 'file'
    if settings["button"]:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"📁 {get_size(file.file_size)} ▷ {' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@') and not x.startswith('www.'), file.file_name.split()))}", url="https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}"
                ),
            ]
            for file in files
        ]
        btn.insert(0, [
            InlineKeyboardButton("Sᴇɴᴅ ᴀʟʟ", callback_data=f"sendfiles#{key}"),
            InlineKeyboardButton("Sᴇʟᴇᴄᴛ ᴀɢᴀɪɴ", callback_data=f"seasons#{key}")
        ])
    else:
        btn = []
        btn.insert(0, 
            [
                InlineKeyboardButton("⇈ ꜱᴇʟᴇᴄᴛ ᴏᴘᴛɪᴏɴꜱ ʜᴇʀᴇ ⇈", 'reqinfo')
            ]
        )
        btn.insert(0, 
            [
                InlineKeyboardButton(f'Qᴜᴀʟɪᴛʏ', callback_data=f"qualities#{key}"),
                InlineKeyboardButton("Lᴀɴɢᴜᴀɢᴇ", callback_data=f"languages#{key}"),
                InlineKeyboardButton("Sᴇᴀsᴏɴ",  callback_data=f"seasons#{key}")
            ]
        )
        btn.insert(0, [
            InlineKeyboardButton("𓅪 ꜱᴇɴᴅ ᴀʟʟ ꜰɪʟᴇꜱ 𓅪", url=f"https://telegram.me/{temp.U_NAME}?start=sendfiles_{key}")
        ])
    
    offset = 0

    btn.append([
            InlineKeyboardButton(
                text="↭ ʙᴀᴄᴋ ᴛᴏ ꜰɪʟᴇs ​↭",
                callback_data=f"next_{req}_{key}_{offset}"
                ),
    ])
    
    if not settings["button"]:
        cur_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
        time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(curr_time.second+(curr_time.microsecond/1000000)))
        remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
        total_results = len(files)
        cap = await get_cap(settings, remaining_seconds, files, query, total_results, search)
        try:
            await query.message.edit_text(text=cap, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)
        except MessageNotModified:
            pass
    else:
        try:
            await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
        except MessageNotModified:
            pass
    await query.answer()

                
@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    lazyData = query.data
    try:
        link = await client.create_chat_invite_link(int(REQST_CHANNEL))
    except:
        pass
    if query.data == "close_data":
        await query.message.delete()
    elif query.data == "gfiltersdeleteallconfirm":
        await del_allg(query.message, 'gfilters')
        await query.answer("Dᴏɴᴇ !")
        return
    elif query.data == "gfiltersdeleteallcancel": 
        await query.message.reply_to_message.delete()
        await query.message.delete()
        await query.answer("Pʀᴏᴄᴇꜱꜱ ᴄᴀɴᴄᴇʟʟᴇᴅ !")
        return
    elif query.data == "delallconfirm":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == enums.ChatType.PRIVATE:
            grpid = await active_connection(str(userid))
            if grpid is not None:
                grp_id = grpid
                try:
                    chat = await client.get_chat(grpid)
                    title = chat.title
                except:
                    await query.message.edit_text("Mᴀᴋᴇ sᴜʀᴇ I'ᴍ ᴘʀᴇsᴇɴᴛ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ!!", quote=True)
                    return await query.answer(MSG_ALRT)
            else:
                await query.message.edit_text(
                    "I'ᴍ ɴᴏᴛ ᴄᴏɴɴᴇᴄᴛᴇᴅ ᴛᴏ ᴀɴʏ ɢʀᴏᴜᴘs !\nCʜᴇᴄᴋ /connections ᴏʀ ᴄᴏɴɴᴇᴄᴛ ᴛᴏ ᴀɴʏ ɢʀᴏᴜᴘs.",
                    quote=True
                )
                return await query.answer(MSG_ALRT)

        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            title = query.message.chat.title

        else:
            return await query.answer(MSG_ALRT)

        st = await client.get_chat_member(grp_id, userid)
        if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
            await del_all(query.message, grp_id, title)
        else:
            await query.answer("Yᴏᴜ ɴᴇᴇᴅ ᴛᴏ ʙᴇ Gʀᴏᴜᴘ Oᴡɴᴇʀ ᴏʀ ᴀɴ Aᴜᴛʜ Usᴇʀ ᴛᴏ ᴅᴏ ᴛʜᴀᴛ !", show_alert=True)
    elif query.data == "delallcancel":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == enums.ChatType.PRIVATE:
            await query.message.reply_to_message.delete()
            await query.message.delete()

        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            st = await client.get_chat_member(grp_id, userid)
            if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
                await query.message.delete()
                try:
                    await query.message.reply_to_message.delete()
                except:
                    pass
            else:
                await query.answer("Tʜᴀᴛ's ɴᴏᴛ ғᴏʀ ʏᴏᴜ!!", show_alert=True)
    elif "groupcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        act = query.data.split(":")[2]
        hr = await client.get_chat(int(group_id))
        title = hr.title
        user_id = query.from_user.id

        if act == "":
            stat = "ᴄᴏɴɴᴇᴄᴛ"
            cb = "connectcb"
        else:
            stat = "ᴅɪꜱᴄᴏɴɴᴇᴄᴛ"
            cb = "disconnect"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{stat}", callback_data=f"{cb}:{group_id}"),
             InlineKeyboardButton("Dᴇʟᴇᴛᴇ", callback_data=f"deletecb:{group_id}")],
            [InlineKeyboardButton("Bᴀᴄᴋ", callback_data="backcb")]
        ])

        await query.message.edit_text(
            f"Gʀᴏᴜᴘ Nᴀᴍᴇ : **{title}**\nGʀᴏᴜᴘ ID : `{group_id}`",
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.MARKDOWN
        )
        return await query.answer(MSG_ALRT)
    elif "connectcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title

        user_id = query.from_user.id

        mkact = await make_active(str(user_id), str(group_id))

        if mkact:
            await query.message.edit_text(
                f"Cᴏɴɴᴇᴄᴛᴇᴅ ᴛᴏ **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text('Sᴏᴍᴇ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ!!', parse_mode=enums.ParseMode.MARKDOWN)
        return await query.answer(MSG_ALRT)
    elif "disconnect" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title
        user_id = query.from_user.id

        mkinact = await make_inactive(str(user_id))

        if mkinact:
            await query.message.edit_text(
                f"Dɪsᴄᴏɴɴᴇᴄᴛᴇᴅ ғʀᴏᴍ **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text(
                f"Sᴏᴍᴇ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ!!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return await query.answer(MSG_ALRT)
    elif "deletecb" in query.data:
        await query.answer()

        user_id = query.from_user.id
        group_id = query.data.split(":")[1]

        delcon = await delete_connection(str(user_id), str(group_id))

        if delcon:
            await query.message.edit_text(
                "Sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ᴄᴏɴɴᴇᴄᴛɪᴏɴ !"
            )
        else:
            await query.message.edit_text(
                f"Sᴏᴍᴇ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ!!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return await query.answer(MSG_ALRT)
    elif query.data == "backcb":
        await query.answer()

        userid = query.from_user.id

        groupids = await all_connections(str(userid))
        if groupids is None:
            await query.message.edit_text(
                "Tʜᴇʀᴇ ᴀʀᴇ ɴᴏ ᴀᴄᴛɪᴠᴇ ᴄᴏɴɴᴇᴄᴛɪᴏɴs!! Cᴏɴɴᴇᴄᴛ ᴛᴏ sᴏᴍᴇ ɢʀᴏᴜᴘs ғɪʀsᴛ....",
            )
            return await query.answer(MSG_ALRT)
        buttons = []
        for groupid in groupids:
            try:
                ttl = await client.get_chat(int(groupid))
                title = ttl.title
                active = await if_active(str(userid), str(groupid))
                act = " - ACTIVE" if active else ""
                buttons.append(
                    [
                        InlineKeyboardButton(
                            text=f"{title}{act}", callback_data=f"groupcb:{groupid}:{act}"
                        )
                    ]
                )
            except:
                pass
        if buttons:
            await query.message.edit_text(
                "Yᴏᴜʀ ᴄᴏɴɴᴇᴄᴛᴇᴅ ɢʀᴏᴜᴘ ᴅᴇᴛᴀɪʟs ;\n\n",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    elif "gfilteralert" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        reply_text, btn, alerts, fileid = await find_gfilter('gfilters', keyword)
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)
    elif "alertmessage" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        reply_text, btn, alerts, fileid = await find_filter(grp_id, keyword)
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)
        
    if query.data.startswith("file"):
        clicked = query.from_user.id
        try:
            typed = query.from_user.id
        except:
            typed = query.from_user.id
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('Nᴏ sᴜᴄʜ ғɪʟᴇ ᴇxɪsᴛ.')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        settings = await get_settings(query.message.chat.id)
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                       file_size='' if size is None else size,
                                                       file_caption='' if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
            f_caption = f_caption
        if f_caption is None:
            f_caption = f"{files.file_name}"

        try:
            if not await db.has_premium_access(clicked) and settings['is_shortlink']: #Don't change Anything without my permission @CodeluffyTG
                if clicked == query.from_user.id:
                    temp.SHORT[clicked] = query.message.chat.id
                    await query.answer(url=f"https://telegram.me/{temp.U_NAME}?start=short_{file_id}")
                    return
                else:
                    await query.answer(f"Hᴇʏ {query.from_user.first_name},\nTʜɪs Is Nᴏᴛ Yᴏᴜʀ Mᴏᴠɪᴇ Rᴇǫᴜᴇsᴛ.\nRᴇǫᴜᴇsᴛ Yᴏᴜʀ's !", show_alert=True)
            else:
                if clicked == query.from_user.id:
                    await query.answer(url=f"https://telegram.me/{temp.U_NAME}?start={ident}_{file_id}")
                    return
                else:
                    await query.answer(f"Hᴇʏ {query.from_user.first_name},\nTʜɪs Is Nᴏᴛ Yᴏᴜʀ Mᴏᴠɪᴇ Rᴇǫᴜᴇsᴛ.\nRᴇǫᴜᴇsᴛ Yᴏᴜʀ's !", show_alert=True)
        except UserIsBlocked:
            await query.answer('Uɴʙʟᴏᴄᴋ ᴛʜᴇ ʙᴏᴛ ᴍᴀʜɴ !', show_alert=True)
        except PeerIdInvalid:
            await query.answer(url=f"https://telegram.me/{temp.U_NAME}?start={ident}_{file_id}")
        except Exception as e:
            await query.answer(url=f"https://telegram.me/{temp.U_NAME}?start={ident}_{file_id}")
            
    elif query.data.startswith("sendfiles"):
        clicked = query.from_user.id
        ident, key = query.data.split("#")
        settings = await get_settings(query.message.chat.id)
        try:
            if not await db.has_premium_access(clicked) and settings['is_shortlink']: # Don't Change anything without my permission @CoderluffyTG
                await query.answer(url=f"https://telegram.me/{temp.U_NAME}?start=sendfiles1_{key}")
                return
            else:
                await query.answer(url=f"https://telegram.me/{temp.U_NAME}?start=allfiles_{key}")
                return
        except UserIsBlocked:
            await query.answer('Uɴʙʟᴏᴄᴋ ᴛʜᴇ ʙᴏᴛ ᴍᴀʜɴ !', show_alert=True)
        except PeerIdInvalid:
            await query.answer(url=f"https://telegram.me/{temp.U_NAME}?start=sendfiles3_{key}")
        except Exception as e:
            logger.exception(e)
            await query.answer(url=f"https://telegram.me/{temp.U_NAME}?start=sendfiles4_{key}")
    
    elif query.data.startswith("del"):
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('Nᴏ sᴜᴄʜ ғɪʟᴇ ᴇxɪsᴛ.')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        settings = await get_settings(query.message.chat.id)
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                       file_size='' if size is None else size,
                                                       file_caption='' if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
            f_caption = f_caption
        if f_caption is None:
            f_caption = f"{files.file_name}"
        await query.answer(url=f"https://telegram.me/{temp.U_NAME}?start=file_{file_id}")
    
    elif query.data.startswith("checksub"):
        if AUTH_CHANNEL and not await is_req_subscribed(client, query):
            await query.answer("Jᴏɪɴ ᴏᴜʀ ᴜᴘᴅᴀᴛᴇꜱ ᴄʜᴀɴɴᴇʟ ᴍᴀʜɴ! ᴩʟᴇᴀꜱᴇ... 🥺", show_alert=True)
            return
        ident, kk, file_id = query.data.split("#")
        await query.answer(url=f"https://t.me/{temp.U_NAME}?start={kk}_{file_id}")
    
    elif query.data == "pages":
        await query.answer()
    
    elif query.data.startswith("send_fsall"):
        temp_var, ident, key, offset = query.data.split("#")
        search = BUTTON0.get(key)
        if not search:
            await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name),show_alert=True)
            return
        files, n_offset, total = await get_search_results(query.message.chat.id, search, offset=int(offset), filter=True)
        await send_all(client, query.from_user.id, files, ident, query.message.chat.id, query.from_user.first_name, query)
        search = BUTTONS1.get(key)
        files, n_offset, total = await get_search_results(query.message.chat.id, search, offset=int(offset), filter=True)
        await send_all(client, query.from_user.id, files, ident, query.message.chat.id, query.from_user.first_name, query)
        search = BUTTONS2.get(key)
        files, n_offset, total = await get_search_results(query.message.chat.id, search, offset=int(offset), filter=True)
        await send_all(client, query.from_user.id, files, ident, query.message.chat.id, query.from_user.first_name, query)
        await query.answer(f"ʜᴇʏ {query.from_user.first_name}, ᴀʟʟ ꜰɪʟᴇꜱ ᴏɴ ᴛʜɪꜱ ᴘᴀɢᴇ ʜᴀꜱ ʙᴇᴇɴ ꜱᴇɴᴛ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴛᴏ ʏᴏᴜ ʙʏ ᴅᴍ !", show_alert=True)
        
    elif query.data.startswith("send_fall"):
        temp_var, ident, key, offset = query.data.split("#")
        if BUTTONS.get(key)!=None:
            search = BUTTONS.get(key)
        else:
            search = FRESH.get(key)
        if not search:
            await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name),show_alert=True)
            return
        files, n_offset, total = await get_search_results(query.message.chat.id, search, offset=int(offset), filter=True)
        await send_all(client, query.from_user.id, files, ident, query.message.chat.id, query.from_user.first_name, query)
        await query.answer(f"ʜᴇʏ {query.from_user.first_name}, ᴀʟʟ ꜰɪʟᴇꜱ ᴏɴ ᴛʜɪꜱ ᴘᴀɢᴇ ʜᴀꜱ ʙᴇᴇɴ ꜱᴇɴᴛ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴛᴏ ʏᴏᴜ ʙʏ ᴅᴍ !", show_alert=True)
        
    
    elif query.data.startswith("opnsetgrp"):
        ident, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        st = await client.get_chat_member(grp_id, userid)
        if (
                st.status != enums.ChatMemberStatus.ADMINISTRATOR
                and st.status != enums.ChatMemberStatus.OWNER
                and str(userid) not in ADMINS
        ):
            await query.answer("ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ʀɪɢʜᴛꜱ ᴛᴏ ᴅᴏ ᴛʜɪꜱ !", show_alert=True)
            return
        title = query.message.chat.title
        settings = await get_settings(grp_id)
        if settings is not None:
            buttons = [
                [
                    InlineKeyboardButton('ʀᴇꜱᴜʟᴛ ᴘᴀɢᴇ',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ʙᴜᴛᴛᴏɴ' if settings["button"] else 'ᴛᴇxᴛ',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ꜰɪʟᴇ ꜱᴇɴᴅ ᴍᴏᴅᴇ', callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ꜱᴛᴀʀᴛ' if settings["botpm"] else 'ᴀᴜᴛᴏ',
                                         callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ꜰɪʟᴇ ꜱᴇᴄᴜʀᴇ',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ᴇɴᴀʙʟᴇ' if settings["file_secure"] else 'ᴅɪꜱᴀʙʟᴇ',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ɪᴍᴅʙ ᴘᴏꜱᴛᴇʀ', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ᴇɴᴀʙʟᴇ' if settings["imdb"] else 'ᴅɪꜱᴀʙʟᴇ',
                                         callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ꜱᴘᴇʟʟ ᴄʜᴇᴄᴋ',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ᴇɴᴀʙʟᴇ' if settings["spell_check"] else 'ᴅɪꜱᴀʙʟᴇ',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ᴡᴇʟᴄᴏᴍᴇ ᴍꜱɢ', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ᴇɴᴀʙʟᴇ' if settings["welcome"] else 'ᴅɪꜱᴀʙʟᴇ',
                                         callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ',
                                         callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ᴇɴᴀʙʟᴇ' if settings["auto_delete"] else 'ᴅɪꜱᴀʙʟᴇ',
                                         callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ᴀᴜᴛᴏ ꜰɪʟᴛᴇʀ',
                                         callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ᴇɴᴀʙʟᴇ' if settings["auto_ffilter"] else 'ᴅɪꜱᴀʙʟᴇ',
                                         callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Mᴀx ʙᴜᴛᴛᴏɴꜱ',
                                         callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}'),
                    InlineKeyboardButton('10' if settings["max_btn"] else f'{MAX_B_TN}',
                                         callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Sʜᴏʀᴛʟɪɴᴋ',
                                         callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ᴇɴᴀʙʟᴇ' if settings["is_shortlink"] else 'ᴅɪꜱᴀʙʟᴇ',
                                         callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('⇋ ᴄʟᴏꜱᴇ ꜱᴇᴛᴛɪɴɢꜱ ᴍᴇɴᴜ ⇋', 
                                         callback_data='close_data'
                                         )
                ]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.edit_text(
                text=f"<b>ᴄʜᴀɴɢᴇ ʏᴏᴜʀ ꜱᴇᴛᴛɪɴɢꜱ ꜰᴏʀ {title} ᴀꜱ ʏᴏᴜ ᴡɪꜱʜ ⚙</b>",
                disable_web_page_preview=True,
                parse_mode=enums.ParseMode.HTML
            )
            await query.message.edit_reply_markup(reply_markup)
        
    elif query.data.startswith("opnsetpm"):
        ident, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        st = await client.get_chat_member(grp_id, userid)
        if (
                st.status != enums.ChatMemberStatus.ADMINISTRATOR
                and st.status != enums.ChatMemberStatus.OWNER
                and str(userid) not in ADMINS
        ):
            await query.answer("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢʜᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True)
            return
        title = query.message.chat.title
        settings = await get_settings(grp_id)
        btn2 = [[
                 InlineKeyboardButton("ᴄʜᴇᴄᴋ ᴍʏ ᴅᴍ 🗳️", url=f"telegram.me/{temp.U_NAME}")
               ]]
        reply_markup = InlineKeyboardMarkup(btn2)
        await query.message.edit_text(f"<b>ʏᴏᴜʀ sᴇᴛᴛɪɴɢs ᴍᴇɴᴜ ғᴏʀ {title} ʜᴀs ʙᴇᴇɴ sᴇɴᴛ ᴛᴏ ʏᴏᴜ ʙʏ ᴅᴍ.</b>")
        await query.message.edit_reply_markup(reply_markup)
        

    elif query.data.startswith("show_option"):
        ident, from_user = query.data.split("#")
        btn = [[
                InlineKeyboardButton("⚠️ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ ⚠️", callback_data=f"unavailable#{from_user}"),
                InlineKeyboardButton("🟢 ᴜᴘʟᴏᴀᴅᴇᴅ 🟢", callback_data=f"uploaded#{from_user}")
             ],[
                InlineKeyboardButton("♻️ ᴀʟʀᴇᴀᴅʏ ᴀᴠᴀɪʟᴀʙʟᴇ ♻️", callback_data=f"already_available#{from_user}")
              ]]
        btn2 = [[
                 InlineKeyboardButton("ᴠɪᴇᴡ ꜱᴛᴀᴛᴜꜱ", url=f"{query.message.link}")
               ]]
        if query.from_user.id in ADMINS:
            user = await client.get_users(from_user)
            reply_markup = InlineKeyboardMarkup(btn)
            await query.message.edit_reply_markup(reply_markup)
            await query.answer("Hᴇʀᴇ ᴀʀᴇ ᴛʜᴇ ᴏᴘᴛɪᴏɴs !")
        else:
            await query.answer("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢʜᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True)
        
    elif query.data.startswith("unavailable"):
        ident, from_user = query.data.split("#")
        btn = [[
                InlineKeyboardButton("⚠️ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ ⚠️", callback_data=f"unalert#{from_user}")
              ]]
        btn2 = [[
                 InlineKeyboardButton('ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ', url=link.invite_link),
                 InlineKeyboardButton("ᴠɪᴇᴡ ꜱᴛᴀᴛᴜꜱ", url=f"{query.message.link}")
               ]]
        if query.from_user.id in ADMINS:
            user = await client.get_users(from_user)
            reply_markup = InlineKeyboardMarkup(btn)
            content = query.message.text
            await query.message.edit_text(f"<b><strike>{content}</strike></b>")
            await query.message.edit_reply_markup(reply_markup)
            await query.answer("Sᴇᴛ ᴛᴏ Uɴᴀᴠᴀɪʟᴀʙʟᴇ !")
            try:
                await client.send_message(chat_id=int(from_user), text=f"<b>Hᴇʏ {user.mention}, Sᴏʀʀʏ Yᴏᴜʀ ʀᴇᴏ̨ᴜᴇsᴛ ɪs ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ. Sᴏ ᴏᴜʀ ᴍᴏᴅᴇʀᴀᴛᴏʀs ᴄᴀɴ'ᴛ ᴜᴘʟᴏᴀᴅ ɪᴛ.</b>", reply_markup=InlineKeyboardMarkup(btn2))
            except UserIsBlocked:
                await client.send_message(chat_id=int(SUPPORT_CHAT_ID), text=f"<b>Hᴇʏ {user.mention}, Sᴏʀʀʏ Yᴏᴜʀ ʀᴇᴏ̨ᴜᴇsᴛ ɪs ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ. Sᴏ ᴏᴜʀ ᴍᴏᴅᴇʀᴀᴛᴏʀs ᴄᴀɴ'ᴛ ᴜᴘʟᴏᴀᴅ ɪᴛ.\n\nNᴏᴛᴇ: Tʜɪs ᴍᴇssᴀɢᴇ ɪs sᴇɴᴛ ᴛᴏ ᴛʜɪs ɢʀᴏᴜᴘ ʙᴇᴄᴀᴜsᴇ ʏᴏᴜ'ᴠᴇ ʙʟᴏᴄᴋᴇᴅ ᴛʜᴇ ʙᴏᴛ. Tᴏ sᴇɴᴅ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴛᴏ ʏᴏᴜʀ PM, Mᴜsᴛ ᴜɴʙʟᴏᴄᴋ ᴛʜᴇ ʙᴏᴛ.</b>", reply_markup=InlineKeyboardMarkup(btn2))
        else:
            await query.answer("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢʜᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True)

    elif query.data.startswith("uploaded"):
        ident, from_user = query.data.split("#")
        btn = [[
                InlineKeyboardButton("🟢 ᴜᴘʟᴏᴀᴅᴇᴅ 🟢", callback_data=f"upalert#{from_user}")
              ]]
        btn2 = [[
                 InlineKeyboardButton('ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ', url=link.invite_link),
                 InlineKeyboardButton("ᴠɪᴇᴡ ꜱᴛᴀᴛᴜꜱ", url=f"{query.message.link}")
               ],[
                 InlineKeyboardButton("🔍 ꜱᴇᴀʀᴄʜ ʜᴇʀᴇ 🔎", url="https://t.me/MoviesLinkSearchBot2")
               ]]
        if query.from_user.id in ADMINS:
            user = await client.get_users(from_user)
            reply_markup = InlineKeyboardMarkup(btn)
            content = query.message.text
            await query.message.edit_text(f"<b><strike>{content}</strike></b>")
            await query.message.edit_reply_markup(reply_markup)
            await query.answer("Sᴇᴛ ᴛᴏ Uᴘʟᴏᴀᴅᴇᴅ !")
            try:
                await client.send_message(chat_id=int(from_user), text=f"<b>Hᴇʏ {user.mention}, Yᴏᴜʀ ʀᴇᴏ̨ᴜᴇsᴛ ʜᴀs ʙᴇᴇɴ ᴜᴘʟᴏᴀᴅᴇᴅ ʙʏ ᴏᴜʀ ᴍᴏᴅᴇʀᴀᴛᴏʀs. Kɪɴᴅʟʏ sᴇᴀʀᴄʜ ɪɴ ᴏᴜʀ Gʀᴏᴜᴘ.</b>", reply_markup=InlineKeyboardMarkup(btn2))
            except UserIsBlocked:
                await client.send_message(chat_id=int(SUPPORT_CHAT_ID), text=f"<b>Hᴇʏ {user.mention}, Yᴏᴜʀ ʀᴇᴏ̨ᴜᴇsᴛ ʜᴀs ʙᴇᴇɴ ᴜᴘʟᴏᴀᴅᴇᴅ ʙʏ ᴏᴜʀ ᴍᴏᴅᴇʀᴀᴛᴏʀs. Kɪɴᴅʟʏ sᴇᴀʀᴄʜ ɪɴ ᴏᴜʀ Gʀᴏᴜᴘ.\n\nNᴏᴛᴇ: Tʜɪs ᴍᴇssᴀɢᴇ ɪs sᴇɴᴛ ᴛᴏ ᴛʜɪs ɢʀᴏᴜᴘ ʙᴇᴄᴀᴜsᴇ ʏᴏᴜ'ᴠᴇ ʙʟᴏᴄᴋᴇᴅ ᴛʜᴇ ʙᴏᴛ. Tᴏ sᴇɴᴅ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴛᴏ ʏᴏᴜʀ PM, Mᴜsᴛ ᴜɴʙʟᴏᴄᴋ ᴛʜᴇ ʙᴏᴛ.</b>", reply_markup=InlineKeyboardMarkup(btn2))
        else:
            await query.answer("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True)

    elif query.data.startswith("already_available"):
        ident, from_user = query.data.split("#")
        btn = [[
                InlineKeyboardButton("♻️ ᴀʟʀᴇᴀᴅʏ ᴀᴠᴀɪʟᴀʙʟᴇ ♻️", callback_data=f"alalert#{from_user}")
              ]]
        btn2 = [[
                 InlineKeyboardButton('Jᴏɪɴ ᴄʜᴀɴɴᴇL', url=link.invite_link),
                 InlineKeyboardButton("Vɪᴇᴡ ꜱᴛᴀᴛᴜS", url=f"{query.message.link}")
               ],[
                 InlineKeyboardButton("🔍 ꜱᴇᴀʀᴄʜ ʜᴇʀᴇ 🔎", url="https://t.me/mr_Movie_file_Bot")
               ]]
        if query.from_user.id in ADMINS:
            user = await client.get_users(from_user)
            reply_markup = InlineKeyboardMarkup(btn)
            content = query.message.text
            await query.message.edit_text(f"<b><strike>{content}</strike></b>")
            await query.message.edit_reply_markup(reply_markup)
            await query.answer("Sᴇᴛ ᴛᴏ Aʟʀᴇᴀᴅʏ Aᴠᴀɪʟᴀʙʟᴇ !")
            try:
                await client.send_message(chat_id=int(from_user), text=f"<b>Hᴇʏ {user.mention}, Yᴏᴜʀ ʀᴇᴏ̨ᴜᴇsᴛ ɪs ᴀʟʀᴇᴀᴅʏ ᴀᴠᴀɪʟᴀʙʟᴇ ᴏɴ ᴏᴜʀ ʙᴏᴛ's ᴅᴀᴛᴀʙᴀsᴇ. Kɪɴᴅʟʏ sᴇᴀʀᴄʜ ɪɴ ᴏᴜʀ Gʀᴏᴜᴘ.</b>", reply_markup=InlineKeyboardMarkup(btn2))
            except UserIsBlocked:
                await client.send_message(chat_id=int(SUPPORT_CHAT_ID), text=f"<b>Hᴇʏ {user.mention}, Yᴏᴜʀ ʀᴇᴏ̨ᴜᴇsᴛ ɪs ᴀʟʀᴇᴀᴅʏ ᴀᴠᴀɪʟᴀʙʟᴇ ᴏɴ ᴏᴜʀ ʙᴏᴛ's ᴅᴀᴛᴀʙᴀsᴇ. Kɪɴᴅʟʏ sᴇᴀʀᴄʜ ɪɴ ᴏᴜʀ Gʀᴏᴜᴘ.\n\nNᴏᴛᴇ: Tʜɪs ᴍᴇssᴀɢᴇ ɪs sᴇɴᴛ ᴛᴏ ᴛʜɪs ɢʀᴏᴜᴘ ʙᴇᴄᴀᴜsᴇ ʏᴏᴜ'ᴠᴇ ʙʟᴏᴄᴋᴇᴅ ᴛʜᴇ ʙᴏᴛ. Tᴏ sᴇɴᴅ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴛᴏ ʏᴏᴜʀ PM, Mᴜsᴛ ᴜɴʙʟᴏᴄᴋ ᴛʜᴇ ʙᴏᴛ.</b>", reply_markup=InlineKeyboardMarkup(btn2))
        else:
            await query.answer("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True)

    
    elif query.data.startswith("upalert"):
        ident, from_user = query.data.split("#")
        if int(query.from_user.id) == int(from_user):
            user = await client.get_users(from_user)
            await query.answer(f"Hᴇʏ {user.first_name}, Yᴏᴜʀ Rᴇᴏ̨ᴜᴇsᴛ ɪs Uᴘʟᴏᴀᴅᴇᴅ !", show_alert=True)
        else:
            await query.answer("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True)
        
    elif query.data.startswith("unalert"):
        ident, from_user = query.data.split("#")
        if int(query.from_user.id) == int(from_user):
            user = await client.get_users(from_user)
            await query.answer(f"Hᴇʏ {user.first_name}, Yᴏᴜʀ Rᴇᴏ̨ᴜᴇsᴛ ɪs Uɴᴀᴠᴀɪʟᴀʙʟᴇ !", show_alert=True)
        else:
            await query.answer("Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴀɴᴛ ʀɪɢᴛs ᴛᴏ ᴅᴏ ᴛʜɪs !", show_alert=True)

    elif lazyData.startswith("generate_stream_link"):
        _, file_id = lazyData.split(":")
        try:
            user_id = query.from_user.id
            username = query.from_user.mention 
            log_msg = await client.send_cached_media(
                chat_id=LOG_CHANNEL,
                file_id=file_id,
            )
            fileName = {quote_plus(get_name(log_msg))}
            lazy_stream = f"{URL}watch/{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
            lazy_download = f"{URL}{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
            hp_link = await get_shortlink(lazy_download)
            ph_link = await get_shortlink(lazy_stream)
            buttons = []
            if await db.has_premium_access(user_id):                               
                buttons = [[
                    InlineKeyboardButton("〄 Ғᴀꜱᴛ Dᴏᴡɴʟᴏᴀᴅ", url=lazy_download),
                    InlineKeyboardButton("Wᴀᴛᴄʜ Oɴʟɪɴᴇ 〄", url=lazy_stream)
                ],[
                    InlineKeyboardButton('◈ Jᴏɪɴ Uᴘᴅᴀᴛᴇꜱ Cʜᴀɴɴᴇʟ ◈', url='https://t.me/Mod_Moviez_X')
                ]]
            else:
                await query.answer("🚸 ɴᴏᴛᴇ :\nᴀᴅ-ꜰʀᴇᴇ ꜱᴇʀᴠɪᴄᴇ ɪꜱ ᴏɴʟʏ ꜰᴏʀ ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀꜱ.\n\nᴛᴏ ᴋɴᴏᴡ ᴍᴏʀᴇ ᴄʜᴇᴄᴋ ᴘʟᴀɴꜱ.", show_alert=True)
                await query.message.reply_text(
                text="<b>‼️ ᴡᴀɴᴛ ᴛᴏ ʀᴇᴍᴏᴠᴇ ᴀᴅꜱ ?\n\n✅ ᴘᴜʀᴄʜᴀꜱᴇ ᴘʀᴇᴍɪᴜᴍ ᴀɴᴅ ᴇɴᴊᴏʏ ᴀᴅ-ꜰʀᴇᴇ ᴇxᴘᴇʀɪᴇɴᴄᴇ.</b>",
                quote=True,
                disable_web_page_preview=True,                  
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💸 ᴄʜᴇᴄᴋᴏᴜᴛ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴꜱ 💸", callback_data='seeplans')]]))
                buttons = [[
                    InlineKeyboardButton("〄 Ғᴀꜱᴛ Dᴏᴡɴʟᴏᴀᴅ", url=hp_link),
                    InlineKeyboardButton("Wᴀᴛᴄʜ Oɴʟɪɴᴇ 〄", url=ph_link)
                ],[
                    InlineKeyboardButton('! Hᴏᴡ ᴛᴏ ᴏᴘᴇɴ ʟɪɴK !', url=STREAMHTO)
                ]]
    
            query.message.reply_markup = query.message.reply_markup or []
            query.message.reply_markup.inline_keyboard.pop(0)
            query.message.reply_markup.inline_keyboard.insert(0, buttons)
            await query.message.edit_reply_markup(InlineKeyboardMarkup(buttons))
            await log_msg.reply_text(
                    text=f"#LinkGenrated\n\nIᴅ : <code>{user_id}</code>\nUꜱᴇʀɴᴀᴍᴇ : {username}\n\nNᴀᴍᴇ : {fileName}",
                    quote=True,
                    disable_web_page_preview=True,
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("〄 Ғᴀꜱᴛ Dᴏᴡɴʟᴏᴀᴅ", url=hp_link),
                                                        InlineKeyboardButton('Wᴀᴛᴄʜ Oɴʟɪɴᴇ 〄', url=ph_link)]]))  
        except Exception as e:
            print(e)  # print the error message
            await query.answer(f"⚠️ SOMETHING WENT WRONG \n\n{e}", show_alert=True)
            return

    # don't change anything without contacting me @creatorrio

    elif query.data == "start":
        user_id = query.from_user.id
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
        
        reply_markup = InlineKeyboardMarkup(buttons)
        
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.START_TXT.format(query.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        await query.answer(MSG_ALRT)

    elif query.data == "purchase":
        buttons = [[
            InlineKeyboardButton('💵 ᴘᴀʏ ᴠɪᴀ ᴜᴘɪ ɪᴅ 💵', callback_data='upi_info')
        ],[
            InlineKeyboardButton('📸 ꜱᴄᴀɴ ǫʀ ᴄᴏᴅᴇ 📸', callback_data='qr_info')
        ],[
            InlineKeyboardButton('⇋ ʙΔᴄᴋ ⇋', callback_data='premium_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.PURCHASE_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    

    elif query.data == "channels":
        buttons = [[
            InlineKeyboardButton('🎐 Jᴏɪɴ Uᴘᴅᴀᴛᴇꜱ Cʜᴀɴɴᴇʟ 🎐', url='https://t.me/Bot_cracker')
        ],[
            InlineKeyboardButton('🔍 Gʀᴏᴜᴘ¹', url='https://t.me/+DqCTrhaymr9mYWZl'),
            InlineKeyboardButton('Gʀᴏᴜᴘ² ', url='https://t.me/+5n7vViwKXJJiMjhl'),
            InlineKeyboardButton('Gʀᴏᴜᴘ³ 🔎', url='https://t.me/+kiyp-7aRHDE5YjY1')
        ],[
            InlineKeyboardButton('∞ Mᴏᴠɪᴇꜱ ∞', url='https://t.me/Mod_Moviez_X')
        ],[
            InlineKeyboardButton('⇋ ʜ0ᴍᴇ', callback_data='start'),
            InlineKeyboardButton('Bᴏᴛꜱ 👾', url='https://t.me/Bot_Cracker/17')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.CHANNELS.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "users":
        buttons = [[
            InlineKeyboardButton('⇋ ʙΔᴄᴋ ⇋', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.USERS_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    
    elif query.data == "admic":
        if query.from_user.id not in ADMINS:
            return await query.answer("⚠️ Yᴏᴜ'ʀᴇ ɴᴏᴛ ᴀ ʙᴏᴛ ᴀᴅᴍɪɴ !", show_alert=True)        
        buttons = [[
            InlineKeyboardButton('⇋ ʙΔᴄᴋ ⇋', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.ADMIC_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    

    elif query.data == "help":
        buttons = [[
            InlineKeyboardButton('!! ᴅɪꜱᴄʟᴀɪᴍᴇʀ !!', callback_data='disclaimer')
        ], [
            InlineKeyboardButton('✧ ꜱᴀᴍᴩʟᴇ', url='https://immense-tabbie-mrsydarise-9fae8c25.koyeb.app/watch/4649/Anime_Trailer_If_Whole_Anime_Was_Considered_As_One_WoRSyD_%40GetTGlinks.mkv?hash=AgADqh'),
            InlineKeyboardButton('ꜱᴛᴀᴛᴜꜱ ✧', callback_data='stats')
        ], [
            InlineKeyboardButton('⇋ ʜᴏᴍᴇ', callback_data='start'),
            InlineKeyboardButton('ᴀʙᴏᴜᴛ ◇', callback_data='about')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.HELP_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "xtra":
        buttons = [[
            InlineKeyboardButton('Tᴇʟᴇɢʀᴀᴩʜ', callback_data='telegraph'),
            InlineKeyboardButton('ʏᴛ-ᴅʟ', callback_data='ytdl')
        ], [
            InlineKeyboardButton('⇋ ʙΔᴄᴋ ⇋', callback_data='help')
        ], [
            InlineKeyboardButton('⇋ ʜ0ᴍᴇ ⇋', callback_data='start')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.HLP_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "telegraph":
            btn = [[
                    InlineKeyboardButton("⟸ Bᴀᴄᴋ", callback_data="xtra"),
                    InlineKeyboardButton("✆ Cᴏɴᴛᴀᴄᴛ ✆", user_id=1733124290)
                  ]]
            await client.edit_message_media(
                query.message.chat.id, 
                query.message.id, 
                InputMediaPhoto(random.choice(PICS))
            )
            reply_markup = InlineKeyboardMarkup(btn)
            await query.message.edit_text(
                text=(script.TELE_TXT),
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )
        
    
        
    elif query.data == "about":
        buttons = [[
           InlineKeyboardButton('⇋ Bᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('ᴄʟᴏꜱᴇ ⊖', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.ABOUT_TXT.format(temp.B_NAME, query.from_user.mention, query.from_user.last_name),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        
    elif query.data == "rendr":
        await query.answer("⚡️ Lɪᴠᴇ SʏSᴛᴇᴍ sᴛᴀᴛᴜs ⚡️\n\n❂ ʀᴀᴍ ●●●◌◌◌◌◌◌◌\n✇ ᴄᴘᴜ ●●●●●●◌◌◌◌\n✪ ᴅᴀᴛᴀ ᴛʀᴀꜰɪᴄs ●●●●◌◌◌◌◌◌ 🛰\n\nᴠ1.0 [Mɾ 𝘴ꪗᦔ 🎐] """, show_alert=True)

    elif query.data == "credits":
        buttons = [[
            InlineKeyboardButton('⇋ ʙΔᴄᴋ ⇋', callback_data='about')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.CREDITS_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    
    elif query.data == "stats":
        buttons = [[
            InlineKeyboardButton('⇇ Bᴀᴄᴋ', callback_data='help'),
            InlineKeyboardButton('⟲ ʀᴇғяᴇsʜ ⟲', callback_data='rfrsh')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.STATUS_TXT.format(users, chats, monsize, free),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "rfrsh":
        await query.answer("ꜰᴇᴛᴄʜɪɴɢ ᴍᴏɴɢᴏ-ᴅʙ ᴅᴀᴛᴀʙᴀꜱᴇ...")
        buttons = [[
            InlineKeyboardButton('⇇ Bᴀᴄᴋ', callback_data='about'),
            InlineKeyboardButton('⟲ RᴇғʀᴇsH ⟲', callback_data='rfrsh')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.STATUS_TXT.format(users, chats, monsize, free),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "shortlink_info":
            btn = [[
            InlineKeyboardButton("1 / 3", callback_data="pagesn1"),
            InlineKeyboardButton("ɴᴇXᴛ ⋟", callback_data="shortlink_info2")
            ],[
            InlineKeyboardButton('⇋ ʜ0ᴍᴇ ⇋', callback_data='start')
            ]]
            reply_markup = InlineKeyboardMarkup(btn)
            await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
           )
            await query.message.edit_text(
                text=script.SHORTLINK_INFO,
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )   
    elif query.data == "shortlink_info2":
            btn = [[
            InlineKeyboardButton("⋞ ʙΔᴄᴋ", callback_data="shortlink_info"),
            InlineKeyboardButton("2 / 3", callback_data="pagesn1"),
            InlineKeyboardButton("ɴᴇXᴛ ⋟", callback_data="shortlink_info3")
            ],[
            InlineKeyboardButton('⇋ ʜ0ᴍᴇ ⇋', callback_data='start')
            ]]
            reply_markup = InlineKeyboardMarkup(btn)
            await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
            )
            await query.message.edit_text(
                text=script.SHORTLINK_INFO2,
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )
    elif query.data == "shortlink_info3":
            btn = [[
            InlineKeyboardButton("⋞ ʙΔᴄᴋ", callback_data="shortlink_info2"),
            InlineKeyboardButton("3 / 3", callback_data="pagesn1")
            ],[
            InlineKeyboardButton('⇋ ʜ0ᴍᴇ ⇋', callback_data='start')
            ]]
            reply_markup = InlineKeyboardMarkup(btn)
            await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
            )
            await query.message.edit_text(
                text=script.SHORTLINK_INFO3,
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )   
    
    elif query.data == "disclaimer":
            btn = [[
                    InlineKeyboardButton("⇋ ʙᴀᴄᴋ ⇋", callback_data="help")
            ]]
            reply_markup = InlineKeyboardMarkup(btn)
            await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
            )
            await query.message.edit_text(
                text=script.DISCLAIMER_TXT,
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML 
            )
    elif query.data.startswith("setgs"):
        ident, set_type, status, grp_id = query.data.split("#")
        grpid = await active_connection(str(query.from_user.id))

        if str(grp_id) != str(grpid):
            await query.message.edit("Yᴏᴜʀ Aᴄᴛɪᴠᴇ Cᴏɴɴᴇᴄᴛɪᴏɴ Hᴀs Bᴇᴇɴ Cʜᴀɴɢᴇᴅ. Gᴏ Tᴏ /connections ᴀɴᴅ ᴄʜᴀɴɢᴇ ʏᴏᴜʀ ᴀᴄᴛɪᴠᴇ ᴄᴏɴɴᴇᴄᴛɪᴏɴ.")
            return await query.answer(MSG_ALRT)

        if set_type == 'is_shortlink' and query.from_user.id not in ADMINS:
            return await query.answer(text=f"Hey {query.from_user.first_name}, You can't change shortlink settings for your group !\n\nIt's an admin only setting !", show_alert=True)

        if status == "True":
            await save_group_settings(grpid, set_type, False)
        else:
            await save_group_settings(grpid, set_type, True)

        settings = await get_settings(grpid)

        if settings is not None:
            buttons = [
                [
                    InlineKeyboardButton('Rᴇꜱᴜʟᴛ Pᴀɢᴇ',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                    InlineKeyboardButton('Bᴜᴛᴛᴏɴ' if settings["button"] else 'ᴛᴇXᴛ',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Fɪʟᴇ ꜱᴇɴᴅ ᴍᴏᴅᴇ', callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}'),
                    InlineKeyboardButton('Sᴛᴀʀᴛ' if settings["botpm"] else 'Δᴜᴛᴏ',
                                         callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Ғɪʟᴇ Sᴇᴄᴜʀᴇ',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ᴇɴΔʙʟᴇ' if settings["file_secure"] else 'ᴅɪꜱΔʙʟᴇ',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Iᴍᴅʙ Pᴏꜱᴛᴇʀ', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                    InlineKeyboardButton('ᴇɴΔʙʟᴇ' if settings["imdb"] else 'ᴅɪꜱΔʙʟᴇ',
                                         callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Sᴘᴇʟʟ Cʜᴇᴄᴋ',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                    InlineKeyboardButton('EɴΔʙʟᴇ' if settings["spell_check"] else 'DɪꜱΔʙʟᴇ',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Wᴇʟᴄᴏᴍᴇ Mꜱɢ', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                    InlineKeyboardButton('EɴΔʙʟᴇ' if settings["welcome"] else 'DɪꜱΔʙʟᴇ',
                                         callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Δᴜᴛᴏ ᴅᴇʟᴇᴛᴇ',
                                         callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}'),
                    InlineKeyboardButton('EɴΔʙʟᴇ' if settings["auto_delete"] else 'DɪꜱΔʙʟᴇ',
                                         callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Δᴜᴛᴏ ꜰɪʟᴛᴇʀ',
                                         callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}'),
                    InlineKeyboardButton('EɴΔʙʟᴇ' if settings["auto_ffilter"] else 'DɪꜱΔʙʟᴇ',
                                         callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Mᴀx ʙᴜᴛᴛᴏɴꜱ',
                                         callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}'),
                    InlineKeyboardButton('10' if settings["max_btn"] else f'{MAX_B_TN}',
                                         callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Sʜᴏʀᴛʟɪɴᴋ',
                                         callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}'),
                    InlineKeyboardButton('EɴΔʙʟᴇ' if settings["is_shortlink"] else 'DɪꜱΔʙʟᴇ',
                                         callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('✗ ᴄʟᴏꜱᴇ ✗', 
                                         callback_data='close_data'
                                         )
                ]
        ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.edit_reply_markup(reply_markup)
    await query.answer(MSG_ALRT)

     
