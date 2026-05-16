import csv
import random
import asyncio
import threading

from http.server import HTTPServer, BaseHTTPRequestHandler

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.types.poll_answer import PollAnswer
from aiogram.filters import CommandStart

BOT_TOKEN = "8682058131:AAH9tvRDuEnndsziV3y9Wm6wztpr20XgrGs"

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

# Render uchun fake web server
class Handler(BaseHTTPRequestHandler):

    def do_GET(self):

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot ishlayapti')

def run_web():

    server = HTTPServer(("0.0.0.0", 10000), Handler)
    server.serve_forever()

threading.Thread(target=run_web).start()

# CSV yuklash
with open("telegram_quiz_questions.csv", encoding="utf-8") as f:

    questions = list(csv.DictReader(f))

# User data
users = {}

# START
@dp.message(CommandStart())
async def start(message: Message):

    buttons = []

    for i in range(1, 32):

        buttons.append(
            [KeyboardButton(text=f"TEST {i}")]
        )

    kb = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )

    await message.answer(
        "Quiz botga xush kelibsiz!",
        reply_markup=kb
    )

# TEST BOSHLASH
@dp.message(F.text == "30 TALIK TEST")
async def start_test(message: Message):

    selected = random.sample(questions, 30)

    users[message.chat.id] = {
        "questions": selected,
        "current": 0,
        "correct": 0
    }

    await send_question(message.chat.id)

# QAYTA ISHLASH
@dp.message(F.text == "🔁 QAYTA ISHLASH")
async def restart_test(message: Message):

    await start_test(message)

# SAVOL YUBORISH
async def send_question(chat_id):

    data = users[chat_id]

    if data["current"] >= 30:

        correct = data["correct"]
        wrong = 30 - correct
        percent = correct * 100 / 30

        if percent >= 90:
            grade = "🏆 A'lo"
        elif percent >= 70:
            grade = "🔥 Yaxshi"
        elif percent >= 50:
            grade = "🙂 Qoniqarli"
        else:
            grade = "😅 Past"

        result = (
            f"🏁 TEST TUGADI\n\n"
            f"✅ To'g'ri: {correct}\n"
            f"❌ Noto'g'ri: {wrong}\n"
            f"📊 Natija: {percent:.1f}%\n\n"
            f"{grade}"
        )

        kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🔁 QAYTA ISHLASH")]
            ],
            resize_keyboard=True
        )

        await bot.send_message(
            chat_id,
            result,
            reply_markup=kb
        )

        return

    q = data["questions"][data["current"]]

    question = q["Question"]

    options = []

    for i in range(1, 10):

        key = f"Option {i}"

        if key in q and q[key]:

            options.append(q[key][:100])

    correct = q["Correct Answer"]
    correct = correct[:100]

    if correct not in options:

        data["current"] += 1
        await send_question(chat_id)
        return

    correct_id = options.index(correct)

    msg = await bot.send_poll(
        chat_id,
        question=question[:300],
        options=options,
        type="quiz",
        correct_option_id=correct_id,
        is_anonymous=False,
        open_period=30
    )

    data["poll_id"] = msg.poll.id
    data["correct_id"] = correct_id

# JAVOB TEKSHIRISH
@dp.poll_answer()
async def handle_poll_answer(poll_answer: PollAnswer):

    user_id = poll_answer.user.id

    if user_id not in users:
        return

    data = users[user_id]

    if poll_answer.option_ids:

        selected = poll_answer.option_ids[0]

        if selected == data["correct_id"]:
            data["correct"] += 1

    data["current"] += 1

    await send_question(user_id)

# RUN
async def main():

    print("BOT ISHLADI")

    await dp.start_polling(bot)

asyncio.run(main())