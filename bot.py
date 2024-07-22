
TOKEN = '6161388093:AAGEb3v2_DvG_ODtFaA5kqB6S_CFLyWwEcE'

GAME_URL = 'https://hzhdlrp.github.io'


from flask import Flask, request, jsonify
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, InlineQueryHandler, CallbackContext
import logging

# Имя вашей игры
GAME_NAME = "gymgame"

# Включаем логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота и Flask-приложения
bot = Bot(token=TOKEN)
app = Flask(__name__)

# Словарь для хранения запросов
queries = {}


# Команда /help
async def help_command(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("This bot implements a T-Rex jumping game. Say /game if you want to play.")


# Команда /game или /start
async def game_command(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    await bot.send_game(chat_id=chat_id, game_short_name=GAME_NAME)


# Обработка callback-запросов
async def callback_query_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    if query.game_short_name != GAME_NAME:
        await bot.answer_callback_query(callback_query_id=query.id,
                                        text=f"Sorry, '{query.game_short_name}' is not available.")
    else:
        queries[query.id] = query
        await bot.answer_callback_query(callback_query_id=query.id, url=GAME_URL)


# Обработка inline-запросов
async def inline_query_handler(update: Update, context: CallbackContext) -> None:
    query = update.inline_query
    results = [{
        "type": "game",
        "id": "0",
        "game_short_name": GAME_NAME
    }]
    await bot.answer_inline_query(inline_query_id=query.id, results=results)


# Обработка запроса на установку рекорда
@app.route("/highscore/<int:score>", methods=["GET"])
def highscore(score: int):
    query_id = request.args.get('id')
    if query_id not in queries:
        return jsonify({"error": "Invalid query ID"}), 400
    query = queries[query_id]
    options = {"chat_id": query.message.chat.id, "message_id": query.message.message_id} if query.message else {
        "inline_message_id": query.inline_message_id}
    bot.set_game_score(user_id=query.from_user.id, score=score, **options)
    return jsonify({"status": "success"})


# Запуск сервера
if __name__ == '__main__':
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler(["start", "game"], game_command))
    application.add_handler(CallbackQueryHandler(callback_query_handler))
    application.add_handler(InlineQueryHandler(inline_query_handler))

    # Запускаем бота в отдельном потоке
    application.run_polling()

    # Запуск Flask-сервера
    app.run(port=5000)