# Copyright (C) 2021 By logi Music-Project
# Commit Start Date 20/10/2021
# Finished On 28/10/2021

import re
import asyncio

from config import ASSISTANT_NAME, BOT_USERNAME, IMG_1, IMG_2,  OWNER_NAME
from driver.filters import command, other_filters
from driver.queues import QUEUE, add_to_queue
from driver.veez import call_py, user
from pyrogram import Client
from pyrogram.errors import UserAlreadyParticipant, UserNotParticipant
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pytgcalls import StreamType
from pytgcalls.types.input_stream import AudioVideoPiped
from pytgcalls.types.input_stream.quality import (
    HighQualityAudio,
    HighQualityVideo,
    LowQualityVideo,
    MediumQualityVideo,
)
from youtubesearchpython import VideosSearch


def ytsearch(query: str):
    try:
        search = VideosSearch(query, limit=1).result()
        data = search["sonuç"][0]
        songname = data["başlık"]
        url = data["link"]
        duration = data["süre"]
        thumbnail = f"https://i.ytimg.com/vi/{data['id']}/hqdefault.jpg"
        return [songname, url, duration, thumbnail]
    except Exception as e:
        print(e)
        return 0


async def ytdl(link):
    proc = await asyncio.create_subprocess_exec(
        "yt-dlp",
        "-g",
        "-f",
        "best[height<=?720][width<=?1280]",
        f"{link}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if stdout:
        return 1, stdout.decode().split("\n")[0]
    else:
        return 0, stderr.decode()


@Client.on_message(command(["izlet", f"izlet@{BOT_USERNAME}"]) & other_filters)
async def vplay(c: Client, m: Message):
    await m.delete()
    replied = m.reply_to_message
    chat_id = m.chat.id
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="• Menü", callback_data="cbmenu"),
                InlineKeyboardButton(text="• Kapat", callback_data="cls"),
            ],
            [
                    InlineKeyboardButton(
                        "🕊.Yapımcı", url=f"https://t.me/Dnztrmn"
                    )
                ],
        ]
    )
    if m.sender_chat:
        return await m.reply_text("you're an __Anonymous__ Admin !\n\n» revert back to user account from admin rights.")
    try:
        aing = await c.get_me()
    except Exception as e:
        return await m.reply_text(f"error:\n\n{e}")
    a = await c.get_chat_member(chat_id, aing.id)
    if a.status != "administrator":
        await m.reply_text(
            f"💡 Kullanabilmek için **Yönetici** olmam gerekiyor gerekli **izinler**:\n\n» ❌ __Mesajları silme__\n» ❌ __Kullanıcıları ekleme__\n» ❌ __Sesli sohbetleri yönetme__\n\nYönetici listesini **güncelle** /reload komutu ile **Yetkilindirdikten sonra**"
        )
        return
    if not a.can_manage_voice_chats:
        await m.reply_text(
            "Gerekli izin:" + "\n\n» ❌ __Sesli sohbetleri yönetme__"
        )
        return
    if not a.can_delete_messages:
        await m.reply_text(
            "Gerekli izin:" + "\n\n» ❌ __Mesajları silme__"
        )
        return
    if not a.can_invite_users:
        await m.reply_text("Gerekli izin:" + "\n\n» ❌ __Kullanıcıları ekle__")
        return
    try:
        ubot = (await user.get_me()).id
        b = await c.get_chat_member(chat_id, ubot)
        if b.status == "atıldı":
            await m.reply_text(
                f"@{ASSISTANT_NAME} **Gruptan yasaklandı** {m.chat.title}\n\n» **Asistanın banını kaldırın aksi takdirde bot çalışmayacaktır.**"
            )
            return
    except UserNotParticipant:
        if m.chat.username:
            try:
                await user.join_chat(m.chat.username)
            except Exception as e:
                await m.reply_text(f"❌ **Asistan sohbete katılamadı**\n\n**sebep**: `{e}`")
                return
        else:
            try:
                invitelink = await c.export_chat_invite_link(
                    m.chat.id
                )
                if invitelink.startswith("https://t.me/+"):
                    invitelink = invitelink.replace(
                        "https://t.me/+", "https://t.me/joinchat/"
                    )
                await user.join_chat(invitelink)
            except UserAlreadyParticipant:
                pass
            except Exception as e:
                return await m.reply_text(
                    f"❌ **Asistan sohbete katılamadı**\n\n**sebep**: `{e}`"
                )

    if replied:
        if replied.video or replied.document:
            loser = await replied.reply("📥 **Video dosyası indiriliyor...**")
            dl = await replied.download()
            link = replied.link
            if len(m.command) < 2:
                Q = 720
            else:
                pq = m.text.split(None, 1)[1]
                if pq == "720" or "480" or "360":
                    Q = int(pq)
                else:
                    Q = 720
                    await loser.edit(
                        "» __bir tek 720, 480, 360 izin verilmiş__ \n💡 **Şuanki video akışı 720p**"
                    )
            try:
                if replied.video:
                    songname = replied.video.file_name[:70]
                elif replied.document:
                    songname = replied.document.file_name[:70]
            except BaseException:
                songname = "Video"

            if chat_id in QUEUE:
                pos = add_to_queue(chat_id, songname, dl, link, "Video", Q)
                await loser.delete()
                requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                await m.reply_photo(
                    photo=f"{IMG_1}",
                    caption=f"💡 **Sıraya eklendi »** `{pos}`\n\n🏷 **İsim:** [{songname}]({link}) | `video`\n💭 **Chat:** `{chat_id}`\n🎧 **Talep eden:** {requester} \n💚**İletişim için :** [🕊.⋆Sahip](https://t.me/Dnztrmn)",
                    reply_markup=keyboard,
                )
            else:
                if Q == 720:
                    amaze = HighQualityVideo()
                elif Q == 480:
                    amaze = MediumQualityVideo()
                elif Q == 360:
                    amaze = LowQualityVideo()
                await loser.edit("🔄 **Katılıyor...**")
                await call_py.join_group_call(
                    chat_id,
                    AudioVideoPiped(
                        dl,
                        HighQualityAudio(),
                        amaze,
                    ),
                    stream_type=StreamType().local_stream,
                )
                add_to_queue(chat_id, songname, dl, link, "Video", Q)
                await loser.delete()
                requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                await m.reply_photo(
                    photo=f"{IMG_2}",
                    caption=f"🏷 **İsim:** [{songname}]({link})\n💭 **Chat:** `{chat_id}`\n💡 **Durum:** `Oynuyor`\n🎧 **Talep eden:** {requester}\n📹 **Yayın türü:** `Video` \n💚**İletişim için :**[🕊.⋆Yapımcı](https://t.me/Dnztrmn)",
                    reply_markup=keyboard,
                )
        else:
            if len(m.command) < 2:
                await m.reply(
                    "» Lütfen bana **video dosyası** veya **video ismi belirtin.**"
                )
            else:
                loser = await c.send_message(chat_id, "🔍 **Aranıyor...**")
                query = m.text.split(None, 1)[1]
                search = ytsearch(query)
                Q = 720
                amaze = HighQualityVideo()
                if search == 0:
                    await loser.edit("❌ **Sonuç bulunamadı.**")
                else:
                    songname = search[0]
                    url = search[1]
                    duration = search[2]
                    thumbnail = search[3]
                    veez, ytlink = await ytdl(url)
                    if veez == 0:
                        await loser.edit(f"❌ yt-dl issues detected\n\n» `{ytlink}`")
                    else:
                        if chat_id in QUEUE:
                            pos = add_to_queue(
                                chat_id, songname, ytlink, url, "Video", Q
                            )
                            await loser.delete()
                            requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                            await m.reply_photo(
                                photo=thumbnail,
                                caption=f"💡 **Oynatma listesine eklendi »** `{pos}`\n\n🏷 **İsim:** [{songname}]({url}) | `video`\n⏱ **Süre:** `{duration}`\n🎧 **Talep eden:** {requester}",
                                reply_markup=keyboard,
                            )
                        else:
                            try:
                                await loser.edit("🔄 **Katılıyor...**")
                                await call_py.join_group_call(
                                    chat_id,
                                    AudioVideoPiped(
                                        ytlink,
                                        HighQualityAudio(),
                                        amaze,
                                    ),
                                    stream_type=StreamType().local_stream,
                                )
                                add_to_queue(chat_id, songname, ytlink, url, "Video", Q)
                                await loser.delete()
                                requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                                await m.reply_photo(
                                    photo=thumbnail,
                                    caption=f"🏷 **İsim:** [{songname}]({url})\n⏱ **Süre:** `{duration}`\n💡 **Durum:** `Oynuyor`\n🎧 **Talep eden:** {requester}\n📹 **Yayın türü:** `Video`",
                                    reply_markup=keyboard,
                                )
                            except Exception as ep:
                                await loser.delete()
                                await m.reply_text(f"🚫 error: `{ep}`")

    else:
        if len(m.command) < 2:
            await m.reply(
                "» Lütfen bana **video dosyası** veya  **video ismi belirtin.**"
            )
        else:
            loser = await c.send_message(chat_id, "🔍 **Aranıyor...**")
            query = m.text.split(None, 1)[1]
            search = ytsearch(query)
            Q = 720
            amaze = HighQualityVideo()
            if search == 0:
                await loser.edit("❌ **Sonuç bulunamadı.**")
            else:
                songname = search[0]
                url = search[1]
                duration = search[2]
                thumbnail = search[3]
                veez, ytlink = await ytdl(url)
                if veez == 0:
                    await loser.edit(f"❌ yt-dl issues detected\n\n» `{ytlink}`")
                else:
                    if chat_id in QUEUE:
                        pos = add_to_queue(chat_id, songname, ytlink, url, "Video", Q)
                        await loser.delete()
                        requester = (
                            f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                        )
                        await m.reply_photo(
                            photo=thumbnail,
                            caption=f"💡 **Sıraya eklendi »** `{pos}`\n\n🏷 **İsim:** [{songname}]({url}) | `video`\n⏱ **Süre:** `{duration}`\n🎧 **Talep eden:** {requester} \n💚**İletişim için :**[🕊.⋆Yapımcı](https://t.me/Dnztrmn)",
                            reply_markup=keyboard,
                        )
                    else:
                        try:
                            await loser.edit("🔄 **Katılıyor...**")
                            await call_py.join_group_call(
                                chat_id,
                                AudioVideoPiped(
                                    ytlink,
                                    HighQualityAudio(),
                                    amaze,
                                ),
                                stream_type=StreamType().local_stream,
                            )
                            add_to_queue(chat_id, songname, ytlink, url, "Video", Q)
                            await loser.delete()
                            requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                            await m.reply_photo(
                                photo=thumbnail,
                                caption=f"🏷 **İsim:** [{songname}]({url})\n⏱ **Süre:** `{duration}`\n💡 **Durum:** `Oynuyor`\n🎧 **Talep eden:** {requester}\n📹 **Yayın türü:** `Video`\n💚**İletişim için :**[🕊.⋆Yapımcı](https://t.me/Dnztrmn)",
                                reply_markup=keyboard,
                            )
                        except Exception as ep:
                            await loser.delete()
                            await m.reply_text(f"🚫 error: `{ep}`")


@Client.on_message(command(["yayin", f"yayin@{BOT_USERNAME}"]) & other_filters)
async def vstream(c: Client, m: Message):
    await m.delete()
    chat_id = m.chat.id
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="• Menü", callback_data="cbmenu"),
                InlineKeyboardButton(text="• Kapat", callback_data="cls"),
            ],
            [
                    InlineKeyboardButton(
                        "🕊.Yapımcı", url=f"https://t.me/Dnztrmn"
                    )
                ],
        ]
    )
    if m.sender_chat:
        return await m.reply_text("Şuan __anonim__ yöneticisin !\n\n» lütfen anonim yöneticilikten çıkıp kimliğini belirle.")
    try:
        aing = await c.get_me()
    except Exception as e:
        return await m.reply_text(f"error:\n\n{e}")
    a = await c.get_chat_member(chat_id, aing.id)
    if a.status != "administrator":
        await m.reply_text(
            f"💡 Beni kullanabilmek için **yönetici** olmam gerekiyor gerekli **izinler**:\n\n» ❌ __Mesajları silme__\n» ❌ __Kullanıcıları ekleme__\n» ❌ __Sesli sohbetleri yönetme__\n\nYönetici listesini **güncelle** /reload komutu ile **yetkilendirdikten sonra**"
        )
        return
    if not a.can_manage_voice_chats:
        await m.reply_text(
            "Gerekli izin:" + "\n\n» ❌ __Sesli sohbetleri yönetme__"
        )
        return
    if not a.can_delete_messages:
        await m.reply_text(
            "Gerekli izin:" + "\n\n» ❌ __Mesajları silme__"
        )
        return
    if not a.can_invite_users:
        await m.reply_text("Gerekli izin:" + "\n\n» ❌ __Kullanıcıları ekleme__")
        return
    try:
        ubot = (await user.get_me()).id
        b = await c.get_chat_member(chat_id, ubot)
        if b.status == "atıldı":
            await m.reply_text(
                f"@{ASSISTANT_NAME} **Gruptan yasaklandı** {m.chat.title}\n\n» **Asistanın banını kaldırın aksi takdirde bot çalışmayacaktır.**"
            )
            return
    except UserNotParticipant:
        if m.chat.username:
            try:
                await user.join_chat(m.chat.username)
            except Exception as e:
                await m.reply_text(f"❌ **Asistan sohbete katılamadı**\n\n**sebep**: `{e}`")
                return
        else:
            try:
                invitelink = await c.export_chat_invite_link(
                    m.chat.id
                )
                if invitelink.startswith("https://t.me/+"):
                    invitelink = invitelink.replace(
                        "https://t.me/+", "https://t.me/joinchat/"
                    )
                await user.join_chat(invitelink)
            except UserAlreadyParticipant:
                pass
            except Exception as e:
                return await m.reply_text(
                    f"❌ **Asistan sohbete katılamadı**\n\n**sebep**: `{e}`"
                )

    if len(m.command) < 2:
        await m.reply("» give me a live-link/m3u8 url/youtube link to stream.")
    else:
        if len(m.command) == 2:
            link = m.text.split(None, 1)[1]
            Q = 720
            loser = await c.send_message(chat_id, "🔄 **processing stream...**")
        elif len(m.command) == 3:
            op = m.text.split(None, 1)[1]
            link = op.split(None, 1)[0]
            quality = op.split(None, 1)[1]
            if quality == "720" or "480" or "360":
                Q = int(quality)
            else:
                Q = 720
                await m.reply(
                    "» __only 720, 480, 360 allowed__ \n💡 **now streaming video in 720p**"
                )
            loser = await c.send_message(chat_id, "🔄 **processing stream...**")
        else:
            await m.reply("**/vstream {link} {720/480/360}**")

        regex = r"^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+"
        match = re.match(regex, link)
        if match:
            veez, livelink = await ytdl(link)
        else:
            livelink = link
            veez = 1

        if veez == 0:
            await loser.edit(f"❌ yt-dl issues detected\n\n» `{livelink}`")
        else:
            if chat_id in QUEUE:
                pos = add_to_queue(chat_id, "Live Stream", livelink, link, "Video", Q)
                await loser.delete()
                requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                await m.reply_photo(
                    photo=f"{IMG_1}",
                    caption=f"💡 **Track added to queue »** `{pos}`\n\n💭 **Chat:** `{chat_id}`\n🎧 **Request by:** {requester}\n💚**Any issues contact :**[🕊.⋆𝙆𝙄𝙉𝙂](https://t.me/cl_me_logesh)",
                    reply_markup=keyboard,
                )
            else:
                if Q == 720:
                    amaze = HighQualityVideo()
                elif Q == 480:
                    amaze = MediumQualityVideo()
                elif Q == 360:
                    amaze = LowQualityVideo()
                try:
                    await loser.edit("🔄 **Joining vc...**")
                    await call_py.join_group_call(
                        chat_id,
                        AudioVideoPiped(
                            livelink,
                            HighQualityAudio(),
                            amaze,
                        ),
                        stream_type=StreamType().live_stream,
                    )
                    add_to_queue(chat_id, "Live Stream", livelink, link, "Video", Q)
                    await loser.delete()
                    requester = (
                        f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                    )
                    await m.reply_photo(
                        photo=f"{IMG_2}",
                        caption=f"💡 **[Video live]({link}) stream started.**\n\n💭 **Chat:** `{chat_id}`\n💡 **Status:** `Playing`\n🎧 **Request by:** {requester}\n💚**Any issues contact :** [🕊.⋆𝙆𝙄𝙉𝙂](https://t.me/cl_me_logesh)",
                        reply_markup=keyboard,
                    )
                except Exception as ep:
                    await loser.delete()
                    await m.reply_text(f"🚫 error: `{ep}`")
