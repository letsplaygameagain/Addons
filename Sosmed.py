# Ayra - UserBot
# Copyright (C) 2021-2022 senpai80
#
# This file is a part of < https://github.com/senpai80/Ayra/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/senpai80/Ayra/blob/main/LICENSE/>.
"""
◈ Perintah Tersedia

•`{i}sosmed <link url>`
    Download Video Tiktok, Instagram, Twitter Tanpa Watermark
    
• `{i}pinter <link/id>`
    Unduh dan kirim pinterest
"""



import glob
import io
import os
from asyncio.exceptions import TimeoutError as AsyncTimeout

try:
    import cv2
except ImportError:
    cv2 = None

try:
    from htmlwebshot import WebShot
except ImportError:
    WebShot = None
from telethon.errors.rpcerrorlist import MessageTooLongError, YouBlockedUserError
from telethon.tl.types import (
    ChannelParticipantAdmin,
    ChannelParticipantsBots,
    DocumentAttributeVideo,
)

from Ayra.fns.tools import metadata, translate

from . import (
    HNDLR,
    LOGS,
    AyConfig,
    async_searcher,
    bash,
    check_filename,
    con,
    eor,
    fast_download,
    get_string,
)
from . import humanbytes as hb
from . import inline_mention, is_url_ok, mediainfo, ayra_cmd

@ayra_cmd(pattern="sosmed(?: |$)(.*)")
async def _(event):
    xxnx = event.pattern_match.group(1)
    if xxnx:
        d_link = xxnx
    elif event.is_reply:
        d_link = await event.get_reply_message()
    else:
        return await eod(
            event,
            "**Berikan Link Pesan atau Reply Link Untuk di Download**",
        )
    xx = await eor(event, "`Video Sedang Diproses...`")
    chat = "@thisvidbot"
    async with event.client.conversation(chat) as conv:
        try:
            msg_start = await conv.send_message("/start")
            r = await conv.get_response()
            msg = await conv.send_message(d_link)
            details = await conv.get_response()
            video = await conv.get_response()
            text = await conv.get_response()
            await event.client.send_read_acknowledge(conv.chat_id)
        except YouBlockedUserError:
            await event.client(UnblockRequest(chat))
            msg_start = await conv.send_message("/start")
            r = await conv.get_response()
            msg = await conv.send_message(d_link)
            details = await conv.get_response()
            video = await conv.get_response()
            text = await conv.get_response()
            await event.client.send_read_acknowledge(conv.chat_id)
        await event.client.send_file(event.chat_id, video)
        await event.client.delete_messages(
            conv.chat_id, [msg_start.id, r.id, msg.id, details.id, video.id, text.id]
        )
        await xx.delete()
        
@ayra_cmd(
    pattern="pinter( (.*)|$)",
)
async def pinterest(e):
    m = e.pattern_match.group(1).strip()
    if not m:
        return await e.eor("`Berikan tautan pinterest.`", time=3)
    soup = await async_searcher(
        "https://www.expertstool.com/download-pinterest-video/",
        data={"url": m},
        post=True,
    )
    try:
        _soup = bs(soup, "html.parser").find("table").tbody.find_all("tr")
    except BaseException:
        return await e.eor("`Tautan salah atau pin pribadi.`", time=5)
    file = _soup[1] if len(_soup) > 1 else _soup[0]
    file = file.td.a["href"]
    await e.client.send_file(e.chat_id, file, caption=f"Pin:- {m}")
