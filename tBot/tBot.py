import logging
import aiogram.utils.markdown
import time
from data_base.sqlite_base import cdb
from RSS.rssparser import parsRSS
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

logging.basicConfig(filename="./info.log", filemode="a", level=logging.INFO,
                    format="%(asctime)s - [%(levelname)s] - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s")


def main_menu_button():
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    mb1 = InlineKeyboardButton("Профиль", callback_data=("send_profile"))
    md2 = InlineKeyboardButton("Новости", callback_data=("news"))
    return InlineKeyboardMarkup().add(mb1, md2)


def back_button():
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup().add(InlineKeyboardButton("<<назад", callback_data="main_menu"))


def is_rss(string: str):
    if string.split("/")[0:-1] == ['https:', '', 'freelance.habr.com', 'user_rss_tasks']:
        return string
    else:
        return False


def tb(TOKEN):
    bot = Bot(token=TOKEN)
    dp = Dispatcher(bot)
    logging.info("connect bot")
    db = cdb()
    rss = parsRSS()

    @dp.message_handler(commands=['start'])
    async def process_start_command(message: types.Message):
        await bot.send_message(message.from_user.id,
                               f"Привет! Я бот, который парсит RSS сайта freelance.habr.com. \nТы можешь мне отправить ссылку на свой RSS, и я буду присылать тебе новые заказы.\n {aiogram.utils.markdown.link('Rss на freelance habr', 'https://telegra.ph/Rss-na-freelancehabrcom-11-12')}",
                               parse_mode="Markdown")

    @dp.message_handler(commands=["help"])
    async def process_help_command(message: types.Message):
        await bot.send_message(message.from_user.id,
                               f"Отправь ссылку на свой RSS, и я буду присылать тебе новые заказы.\n {aiogram.utils.markdown.link('Rss на freelance habr', 'https://telegra.ph/Rss-na-freelancehabrcom-11-12')}",
                               parse_mode="Markdown")

    @dp.message_handler(commands=["menu"])
    async def main_menu(message: types.Message):
        await bot.send_message(message.from_user.id,
                               f"В профиле тебе доступна статистика.",
                               parse_mode="Markdown", reply_markup=main_menu_button())

    @dp.message_handler()
    async def message_user(message: types.Message):
        if is_rss(message.text):
            await bot.send_message(message.from_user.id, "OK")
            db.add_info(message.from_user.id, message.from_user.username, message.text, 0, str(time.time()))
        else:
            await bot.send_message(message.from_user.id, "Я тебя не понимаю")

    @dp.callback_query_handler(lambda c: c.data == 'send_profile')
    async def process_callback_button1(callback_query: types.CallbackQuery):
        await bot.answer_callback_query(callback_query.id)
        a = db.get_info(callback_query.from_user.id)
        await callback_query.message.edit_text(
            f"Имя `{a[1]}`\nОтправлено статей: `{a[3]}`\nСылка на RSS [Тык]({a[2]})\nПоследний заказ `{time.strftime('%a, %d %b %Y %H:%M:%S', time.gmtime(float(a[4])))}`",
            parse_mode="Markdown", reply_markup=back_button())

    @dp.callback_query_handler(lambda c: c.data == 'main_menu')
    async def process_callback_button2(callback_query: types.CallbackQuery):
        await bot.answer_callback_query(callback_query.id)
        await callback_query.message.edit_text(
            f"В профиле тебе доступна статистика.",
            parse_mode="Markdown", reply_markup=main_menu_button())

    @dp.callback_query_handler(lambda c: c.data == 'news')
    async def process_callback_button2(callback_query: types.CallbackQuery):
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        await bot.answer_callback_query(callback_query.id)
        await callback_query.message.edit_text("Три секунды")
        data = rss.get_new_feed(callback_query.from_user.id)[::-1]
        await callback_query.message.delete()
        for i in data:
            try:
                await bot.send_message(callback_query.from_user.id,
                                       f"<b>{i['title']}</b>\n<ins>{i['published'][0:-6]}</ins>\n\n{i['summary'].replace('<br />', '').replace('</br>', '')}",
                                       parse_mode="HTML",
                                       reply_markup=InlineKeyboardMarkup().add(
                                           InlineKeyboardButton("Ссылка", url=i["id"])))
            except:
                await bot.send_message(callback_query.from_user.id,
                                       f"<b>{i['title']}</b>\n<ins>{i['published'][0:-6]}</ins>",
                                       parse_mode="HTML",
                                       reply_markup=InlineKeyboardMarkup().add(
                                           InlineKeyboardButton("Ссылка", url=i["id"])))
        await bot.send_message(callback_query.from_user.id,
                               f"Всего {len(data)} новых заказов" if len(data) != 0 else "Пусто, новых заказов нет",
                               reply_markup=main_menu_button())
        db.add_send_order(callback_query.from_user.id, len(data))
        logging.info(f"send {len(data)} from user_id={callback_query.from_user.id}")

    executor.start_polling(dp)
