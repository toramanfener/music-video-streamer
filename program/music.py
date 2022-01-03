# Copyright (C) 2021 By logi music-player
# Commit Start Date 20/10/2021
# Finished On 28/10/2021

import re
import asyncio

from config import ASSISTANT_NAME, BOT_USERNAME, IMG_1, IMG_2, OWNER_NAME
from driver.filters import command, other_filters
from driver.queues import QUEUE, add_to_queue
from driver.veez import call_py, user
from driver.utils import bash
from pyrogram import Client
from pyrogram.errors import UserAlreadyParticipant, UserNotParticipant
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pytgcalls import StreamType
from pytgcalls.types.input_stream import AudioPiped
from youtubesearchpython import VideosSearch


def ytsearch(query: str):
    try:
        search = VideosSearch(query, limit=1).result()
        data = search["result"][0]
        songname = data["title"]
        url = data["link"]
        duration = data["duration"]
        thumbnail = f"https://i.ytimg.com/vi/{data['id']}/hqdefault.jpg"
        return [songname, url, duration, thumbnail]
    except Exception as e:
        print(e)
        return 0



async def ytdl(format: str, link: str):
    stdout, stderr = await bash(f'youtube-dl -g -f "{format}" {link}')
    if stdout:
        return 1, stdout.split("\n")[0]
    return 0, stderr


@Client.on_message(command(["oynat", f"oynat@{BOT_USERNAME}"]) & other_filters)
async def play(c: Client, m: Message):
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
                        "🕊Yapımcı", url=f"https://t.me/Dnztrmn"
                    )
                ],
        ]
    )
    if m.sender_chat:
        return await m.reply_text("Şuan __anonim__ yöneticisin !\n\n» Lütfen anonim yöneticilikten çıkıp kimliğini belirle.")
    try:
        aing = await c.get_me()
    except Exception as e:
        return await m.reply_text(f"error:\n\n{e}")
    a = await c.get_chat_member(chat_id, aing.id)
    if a.status != "administrator":
        await m.reply_text(
            f"💡 Kullanabilmek için **Yönetici** olmam gerekiyor gerekli **izinler**:\n\n» ❌ __Mesajları silme__\n» ❌ __Kullanıcıları ekleme__\n» ❌ __Sesli sohbetleri yönetme__\n\nYönetici listesini **güncelle** /reload komutu ile **Yetkilendirdikten sonra**"
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
                f"@{ASSISTANT_NAME} **Gruptan yasaklandı** {m.chat.title}\n\n» **Asistanın banını kaldırın aksi takdirde bot çalısmayacaktır.**"
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
        if replied.audio or replied.voice:
            suhu = await replied.reply("📥 **Dosya indiriliyor...**")
            dl = await replied.download()
            link = replied.link
            if replied.audio:
                if replied.audio.title:
                    songname = replied.audio.title[:70]
                else:
                    if replied.audio.file_name:
                        songname = replied.audio.file_name[:70]
                    else:
                        songname = "Audio"
            elif replied.voice:
                songname = "Voice Note"
            if chat_id in QUEUE:
                pos = add_to_queue(chat_id, songname, dl, link, "Audio", 0)
                await suhu.delete()
                await m.reply_photo(
                    photo=f"{IMG_1}",
                    caption=f"💡 **Geçerli parçaya atladı »** `{pos}`\n\n🏷 **İsim:** [{songname}]({link}) | `music`\n💭 **Chat:** `{chat_id}`\n🎧 **Talep eden:** {m.from_user.mention()} \n💚**İletişim İçin :** [🕊.⋆Yapımcı](https://t.me/dnztrmn)",
                    reply_markup=keyboard,
                )
            else:
             try:
                await suhu.edit("🔄 **Katılıyor...**")
                await call_py.join_group_call(
                    chat_id,
                    AudioPiped(
                        dl,
                    ),
                    stream_type=StreamType().local_stream,
                )
                add_to_queue(chat_id, songname, dl, link, "Audio", 0)
                await suhu.delete()
                requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                await m.reply_photo(
                    photo=f"{IMG_2}",
                    caption=f"🏷 **İsim:** [{songname}]({link})\n💭 **Chat:** `{chat_id}`\n💡 **Durum:** `Oynuyor`\n🎧 **Talep eden:** {requester}\n📹 **Yayın türü:** `Müzik` \n💚**İletişim için  :** [🕊.⋆Yapımcı](https://t.me/dnztrmn)",
                    reply_markup=keyboard,
                )
             except Exception as e:
                await suhu.delete()
                await m.reply_text(f"🚫 error:\n\n» {e}")
        else:
            if len(m.command) < 2:
                await m.reply(
                    "» Lütfen bana **ses dosyası** veya **şarkı ismi  verin.**"
                )
            else:
                suhu = await c.send_message(chat_id, "🔍 **Arıyor...**")
                query = m.text.split(None, 1)[1]
                search = ytsearch(query)
                if search == 0:
                    await suhu.edit("❌ **Sonuç bulunamadı.**")
                else:
                    songname = search[0]
                    url = search[1]
                    duration = search[2]
                    thumbnail = search[3]
                    format = "bestaudio[ext=m4a]"
                    veez, ytlink = await ytdl(format, url)
                    if veez == 0:
                        await suhu.edit(f"❌ yt-dl issues detected\n\n» `{ytlink}`")
                    else:
                        if chat_id in QUEUE:
                            pos = add_to_queue(
                                chat_id, songname, ytlink, url, "Audio", 0
                            )
                            await suhu.delete()
                            requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                            await m.reply_photo(
                                photo=thumbnail,
                                caption=f"💡 **Oynatma listesine eklendi »** `{pos}`\n\n🏷 **İsim:** [{songname}]({url}) | `music`\n**⏱ Süre:** `{duration}`\n🎧 **Talep eden:** {requester} \n💚**İletişim için :** [🕊.⋆Yapımcı](https://t.me/Dnztrmn)",
                                reply_markup=keyboard,
                            )
                        else:
                            try:
                                await suhu.edit("🔄 **Katılıyor...**")
                                await call_py.join_group_call(
                                    chat_id,
                                    AudioPiped(
                                        ytlink,
                                    ),
                                    stream_type=StreamType().local_stream,
                                )
                                add_to_queue(chat_id, songname, ytlink, url, "Audio", 0)
                                await suhu.delete()
                                requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                                await m.reply_photo(
                                    photo=thumbnail,
                                    caption=f"🏷 **İsim:** [{songname}]({url})\n**⏱ Süre:** `{duration}`\n💡 **Durum:** `Oynuyor`\n🎧 **Talep eden:** {requester}\n📹 **Yayın türü:** `Müzik` \n💚**İletişim için :** [🕊.⋆Yapımcı](https://t.me/dnztrmn)",
                                    reply_markup=keyboard,
                                )
                            except Exception as ep:
                                await suhu.delete()
                                await m.reply_text(f"🚫 error: `{ep}`")

    else:
        if len(m.command) < 2:
            await m.reply(
                "» Lütfen bana **ses dosyası** veya **Şarkı ismi  verin.**"
            )
        else:
            suhu = await c.send_message(chat_id, "🔍 **Aranıyor...**")
            query = m.text.split(None, 1)[1]
            search = ytsearch(query)
            if search == 0:
                await suhu.edit("❌ **no results found.**")
            else:
                songname = search[0]
                url = search[1]
                duration = search[2]
                thumbnail = search[3]
                format = "bestaudio[ext=m4a]"
                veez, ytlink = await ytdl(format, url)
                if veez == 0:
                    await suhu.edit(f"❌ yt-dl issues detected\n\n» `{ytlink}`")
                else:
                    if chat_id in QUEUE:
                        pos = add_to_queue(chat_id, songname, ytlink, url, "Audio", 0)
                        await suhu.delete()
                        requester = (
                            f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                        )
                        await m.reply_photo(
                            photo=thumbnail,
                            caption=f"💡 **Oynatma listesine eklendi »** `{pos}`\n\n🏷 **İsim:** [{songname}]({url}) | `music`\n**⏱ Süre:** `{duration}`\n🎧 **Talep eden:** {requester}\n💚**İletişim için :** [🕊.⋆Yapımcı](https://t.me/Dnztrmn)",
                            reply_markup=keyboard,
                        )
                    else:
                        try:
                            await suhu.edit("🔄 **Katılıyor...**")
                            await call_py.join_group_call(
                                chat_id,
                                AudioPiped(
                                    ytlink,
                                ),
                                stream_type=StreamType().local_stream,
                            )
                            add_to_queue(chat_id, songname, ytlink, url, "Audio", 0)
                            await suhu.delete()
                            requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                            await m.reply_photo(
                                photo=thumbnail,
                                caption=f"🏷 **İsim:** [{songname}]({url})\n**⏱ Süre:** `{duration}`\n💡 **Durum:** `Oynuyor`\n🎧 **Talep eden:** {requester}\n📹 **Yayın türü:** `Müzik`\n💚**İletişim için :** [🕊.⋆Yapımcı](https://t.me/Dnztrmn)",
                                reply_markup=keyboard,
                            )
                        except Exception as ep:
                            await suhu.delete()
                            await m.reply_text(f"🚫 error: `{ep}`")
