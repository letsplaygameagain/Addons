# Ayra - UserBot
# Copyright (C) 2021-2022 senpai80
#
# This file is a part of < https://github.com/senpai80/Ayra/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/senpai80/Ayra/blob/main/LICENSE/>.
"""
◈ Perintah Tersedia

• `{i}tts` `LanguageCode <reply to a message>`

• `{i}stt` `<reply to audio file>`
  `Convert Speech to Text...`
  `Note - Sometimes Not 100% Accurate`
"""

import os
import subprocess
from datetime import datetime

import speech_recognition as sr
from gtts import gTTS

from . import *

reco = sr.Recognizer()


@ayra_cmd(
    pattern="tts ?(.*)",
)
async def _(event):
    input_str = event.pattern_match.group(1)
    start = datetime.now()
    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        text = previous_message.message
        lan = input_str
    elif "|" in input_str:
        lan, text = input_str.split("|")
    else:
        await event.eor("Sintaks tidak valid. Modul berhenti.")
        return
    text = text.strip()
    lan = lan.strip()
    if not os.path.isdir("downloads/"):
        os.makedirs("downloads/")
    required_file_name = "downloads/voice.ogg"
    try:
        tts = gTTS(text, lang=lan)
        tts.save(required_file_name)
        command_to_execute = [
            "ffmpeg",
            "-i",
            required_file_name,
            "-map",
            "0:a",
            "-codec:a",
            "libopus",
            "-b:a",
            "100k",
            "-vbr",
            "on",
            required_file_name + ".opus",
        ]
        try:
            subprocess.check_output(command_to_execute, stderr=subprocess.STDOUT)
        except (subprocess.CalledProcessError, NameError, FileNotFoundError) as exc:
            await event.eor(str(exc))
        else:
            os.remove(required_file_name)
            required_file_name = required_file_name + ".opus"
        end = datetime.now()
        ms = (end - start).seconds
        await event.reply(
            file=required_file_name,
        )
        os.remove(required_file_name)
        await eod(event, "Diproses {} ({}) di {} detik!".format(text[0:97], lan, ms))
    except Exception as e:
        await event.eor(str(e))


@ayra_cmd(pattern="stt")
async def speec_(e):
    reply = await e.get_reply_message()
    if not (reply and reply.media):
        return await eod(e, "`Balas ke Audio-File..`")
    # Not Hard Checking File Types
    re = await reply.download_media()
    fn = re + ".wav"
    await bash(f'ffmpeg -i "{re}" -vn "{fn}"')
    with sr.AudioFile(fn) as source:
        audio = reco.record(source)
    try:
        text = reco.recognize_google(audio, language="id-ID")
    except Exception as er:
        return await e.eor(str(er))
    out = "**Extracted Text :**\n `" + text + "`"
    await e.eor(out)
    os.remove(fn)
    os.remove(re)
