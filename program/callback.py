# Copyright (C) 2021 By VeezMusicProject

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from config import (
    ASSISTANT_NAME,
    BOT_NAME,
    BOT_USERNAME,
    GROUP_SUPPORT,
    OWNER_NAME,
    UPDATES_CHANNEL,
)


@Client.on_callback_query(filters.regex("cbstart"))
async def cbstart(_, query: CallbackQuery):
    await query.edit_message_text(
        f"""✨ **Hoşgeldin [{query.message.chat.first_name}](tg://user?id={query.message.chat.id}) !**\n
💭 **[{BOT_NAME}](https://t.me/{BOT_USERNAME}) Bu bot güvenli ve sorunsuz şekilde gruplarınızda video ve müzik oynatmanız için yapılmıştır kılavuzu ve komutları okumanız bot hakkında bilgi sahibi olmanızı sağlar!**

💡 **Bot komutları botun tüm özelliklerinden yararlanmanıza olanak tanır bunun için okumanız tavsiye edilir » 📚 Komutlar butonu!**


🛠 [Yapımcı](https://t.me/Dnztrmn) **Bot hakkında sorunlarınızı ve önerilerinizi iletebilirsiniz**

❔ **Temel kılavuz bot hakkında bilgi almanız ve kullanımı kolaylaştırmak için harika bir yoldur okumanız gerekir yaşıyabileceğiniz tüm sorunların çözümü burda mevcuttur» ❓ Temel Kılavuz!**""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "➕ Gruba Ekle ➕",
                        url=f"https://t.me/{BOT_USERNAME}?startgroup=true",
                    )
                ],
                [InlineKeyboardButton("❓ Temel Kılavuz", callback_data="cbhowtouse")],
                [
                    InlineKeyboardButton("📚 Komutlar", callback_data="cbcmds"),
                    InlineKeyboardButton("❤ Yapımcı", url=f"https://t.me/Dnztrmn"),
                ],
                [
                    InlineKeyboardButton(
                        "👥 Sohbet Grubu", url=f"https://t.me/Keyfialemsohbet"
                    ),
                    InlineKeyboardButton(
                        "📣 Resmi Kanal", url=f"https://t.me/yalnzadmlr"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "🕊Yapımcı", url="https://t.me/Dnztrmn"
                    )
                ],
            ]
        ),
        disable_web_page_preview=True,
    )


@Client.on_callback_query(filters.regex("cbhowtouse"))
async def cbguides(_, query: CallbackQuery):
    await query.edit_message_text(
        f"""❓ **Bot hakkında temel kılavuz:**

1.) **İlk olarak beni bir gruba ekle.**
2.) **Gerekli tüm izinleri ver (ban yetkisi grup bilgisi değiştirme hariç).**
3.) **Grubuna @{ASSISTANT_NAME} /gel komutu ile asistanı ekle asistan gruba katılmazsa elle eklemen gerekebilir.**
4.) **Sesli sohbeti başlat ve artık hazır sorunsuz şekilde kullanabilirsin kasma olduğu zaman komutu "/" yerine "." olarak başlat ve /reload komutu ile yenile.**
5.) **Şimdi botta mevcut olan tüm komutları ögrenme zamanı » 📚 Komutlara ulaşmak için ana ekrana dönmeniz gerekiyor bunu   » Geri Dön butonuna tıklayarak gerçekleştirebilirsin**

💡 **Sorunlarınız ve önerileriniz için sizi sohbet grubumuza bekleriz: @Keyfialemsohbet**

⚡ __Powered by {BOT_NAME} A.I__""",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔙 Geri Dön", callback_data="cbstart")]]
        ),
    )


@Client.on_callback_query(filters.regex("cbcmds"))
async def cbhelps(_, query: CallbackQuery):
    await query.edit_message_text(
        f"""📚 Komut listesi:

» /oynat - sesli sohbette müzik oynatabilirsiniz
» /yayın - Sesli sohbette radio yayını yapabilirsiniz
» /izlet - Sesli sohbette video oynatabilirsiniz
» /canlı - Sesli sohbette canlı yayın oynatabilirsiniz canlı yayın linkini komutun yanina yapıştırmanız yeterli
» /liste - aktif oynatma listesini gösterir
» /video (sorgu) - Youtubeden video indirebilirsiniz
» /indir (sorgu) - Youtubeden müzik indirebilirsiniz
» /sözler (sorgu) - Herhangi bir şarkının sözlerini getirir
» /ara (sorgu) - İstediğiniz videonun yada şarkının linkini bulabilirsiniz
» /sıra - sıra listesini gösterir (Yönetici kullanabilir)
» /dur - Yayını durdurur (Yönetici Kullanabilir)
» /devam - Yayına devam eder (Yönetici kullanabilir)
» /gec - Geçerli parçaya atlar (Yönetici kullanabilir)
» /bitir - Yayını bitirir  (Yönetici kullanabilir)
» /gel - Asistanı gruba daveteder (Yönetici kullanabilir)
» /defol - Asistanı gruptan çıkarır (Yönetoci kullanabilir)
» /reload - Yönetici listesini günceller (Yönetici kullanabilir)

⚡ __Powered by {BOT_NAME} AI__""",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔙 Geri Dön", callback_data="cbstart")]]
        ),
    )


@Client.on_callback_query(filters.regex("cls"))
async def close(_, query: CallbackQuery):
    await query.message.delete()
