from pyrogram import InlineKeyboardButton, InlineKeyboardMarkup, Client

from app.utils import admin_id


def rec(client: Client, chat_id):
    text = """[100 yillik kapsula haqida eshitganmisiz?](https://t.me/joinchat/Q8PMM2I_iaq99WU8)

[Birinchi eksperimental aerosikl nechanchi yilda ixtiro qilinganini bilasizmi?](https://t.me/joinchat/Q8PMM2I_iaq99WU8)

[Jangovar samalyotlar ishlab chiqaradigan zavod ustiga shaxar qurilganligini bilarmidingiz?](https://t.me/joinchat/Q8PMM2I_iaq99WU8)

Bizning kanalda barcha savollarga javob suratlarda aks etgan. Tarixga oid qiziqarli suratlarni [@PhotoTarix](https://t.me/joinchat/Q8PMM2I_iaq99WU8) kanalimizda ko'rishingiz mumkin.

Link👉 [@PhotoTarix](https://t.me/joinchat/Q8PMM2I_iaq99WU8)"""

    client.send_photo(chat_id, 'https://t.me/ek_uzb/13', caption=text,
                      parse_mode='Markdown')
