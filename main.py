from telegram.ext import ApplicationBuilder, ContextTypes
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from telegram.constants import ParseMode
import urllib.parse
import os
from dotenv import load_dotenv
import threading
import re

from modules.cian import Cian

load_dotenv()

chat_ids = [
    558161625, 185947915
]

bot_token = os.getenv("BOT_TOKEN")
application = ApplicationBuilder().token(bot_token).build()

def preprocess(text):
    return re.sub(r'[_*[\]()~>#\+\-=|{}.!]', lambda x: '\\' + x.group(), text)

async def new_offer_callback(context: ContextTypes.DEFAULT_TYPE):
    msg = "[*Новая квартира\!*]({})\n{}\n*Адрес:* {}\n*Метро:* {}\n*Цена:* `{}`\n{}\n\n`Выложено {}`".format(
        context.job.data["url"],
        preprocess(context.job.data["info"]),
        "[{}]({})".format(
            preprocess(context.job.data["address"]),
            "https://yandex.ru/maps/?ol=geo&text={}".format(urllib.parse.quote_plus(context.job.data["address"]))
        ),
        preprocess(context.job.data["underground"]),
        preprocess(context.job.data["price"]),
        preprocess(context.job.data["additional"]),
        preprocess(context.job.data["created_at"]),
    )
    photos = [InputMediaPhoto(media=img) for img in context.job.data["imgs"]]
    for chat_id in chat_ids:
        await context.bot.send_media_group(
            chat_id=chat_id,
            media=photos,
            caption=msg,
            parse_mode=ParseMode.MARKDOWN_V2,
        )

def monitor_cian(last_offers: dict, cian: Cian):
    while True:
        for offer in cian.parse_offers():
            if offer["id"] > last_offers["cian"]:
                last_offers["cian"] = offer["id"]
                print(offer["id"])
                application.job_queue.run_once(new_offer_callback, 0, data=offer)

def main() -> None:
    last_offers = {
        "cian": -1,
    }
    cian = Cian()
    last_offers["cian"] = cian.get_last_offer()

    t1 = threading.Thread(target=monitor_cian, args=(last_offers, cian))
    t2 = threading.Thread(target=cian.refresher, args=())
    t1.start()
    t2.start()
    application.run_polling()
    t1.join()
    t2.join()
            
if __name__ == "__main__":
    main()