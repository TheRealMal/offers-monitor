from telegram.ext import ApplicationBuilder, ContextTypes
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from telegram.constants import ParseMode
import urllib.parse
import os
import threading
import re

from modules.cian import Cian

chat_ids = [
    558161625
]

bot_token = ""
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

def monitor_cian(last_offers: dict, cian: Cian, application):
    while True:
        for offer in cian.parse_offers():
            if offer["id"] > last_offers["cian"]:
                last_offers["cian"] = offer["id"]
                print(offer["id"])
                application.job_queue.run_once(new_offer_callback, 0, data=offer)

def main() -> None:
    last_offers = {
        "cian": 0,
    }
    cian = Cian(
        config='{"query":{"geo":{"type":"geo","value":[{"name":"Выделенная область","type":"polygon","coordinates":[["37.485679434077895","55.924208530196694"],["37.45322063338472","55.91828501733163"],["37.43049946423207","55.90119286721603"],["37.404938148935344","55.88226873419615"],["37.391548882350804","55.8640198332477"],["37.38465137838131","55.846218861597826"],["37.379782556420025","55.82772456823048"],["37.39966359181062","55.810592345145956"],["37.418733132110276","55.79276679617156"],["37.43374534553959","55.77561911546829"],["37.4641754827976","55.763496850258875"],["37.49582282554593","55.74976896207237"],["37.5278759034577","55.73283121617271"],["37.55384295391789","55.71496992316358"],["37.58914191313718","55.70763983956673"],["37.62200646137583","55.70237048883059"],["37.65730542059512","55.70007924419467"],["37.68895276334345","55.71451183340212"],["37.70842805118858","55.732602277154065"],["37.7157312841305","55.7511419692618"],["37.71289113798639","55.76944409490886"],["37.70558790504447","55.78705174472042"],["37.67840364909398","55.80670798803897"],["37.65487100961448","55.82521231621453"],["37.64472763052845","55.84576231873926"],["37.64472763052845","55.8640198332477"],["37.662985712883255","55.882724846378146"],["37.67799791393057","55.901420812317305"],["37.64513336569192","55.918740704442065"],["37.61105161196295","55.92124688739648"],["37.57656412307051","55.9221581863095"],["37.54410530999533","55.92261382769752"],["37.51002355626636","55.9221581863095"],["37.477970478354564","55.92010773349807"],["37.441454313644954","55.9059794318683"]]}]},"price":{"value":{"gte":45000,"lte":65000},"type":"range"},"engine_version":{"value":"2","type":"term"},"region":{"type":"terms","value":[1]},"for_day":{"value":"!1","type":"term"},"total_area":{"type":"range","value":{"gte":30}},"sort":{"type":"term","value":"creation_date_desc"},"objects_on_images":{"value":[],"type":"terms"},"outdated_repair":{"value":false,"type":"term"},"with_neighbors":{"value":false,"type":"term"},"limit":{"value":20,"type":"term"},"page":{"value":1,"type":"term"},"bbox":{"type":"term","value":[[37.792723782201364,56.064596450425725],[37.338119359589626,55.565132328609153]]},"building_status":{"type":"term","value":1},"_type":"flatrent","room":{"value":[2,1],"type":"terms"}}}'.encode()
    )
    last_offers["cian"] = cian.get_last_offer()

    t1 = threading.Thread(target=monitor_cian, args=(last_offers, cian, application))
    t2 = threading.Thread(target=cian.refresher, args=())
    t1.start()
    t2.start()
    application.run_polling()
    t1.join()
    t2.join()
            
if __name__ == "__main__":
    main()