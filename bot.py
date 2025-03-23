import random
import asyncio
import logging
import os
import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message
from aiogram.filters import Command
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")
AUTHORIZED_USERS = set(map(int, os.getenv("AUTHORIZED_USERS", "").split(',')))

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Список пользователей
users = set()

# Список смайликов
EMOJI_LIST = ["😎", "😂", "😍", "🔥", "🤩", "💪", "😆", "🎉", "👍", "🦍", "😈", "🫦", "🐗", "🐣", "😼", "👆", "🥵", "👹"]

# Счетчики сообщений
stats = {
    "daily": 0,
    "weekly": 0,
    "monthly": 0,
    "last_reset": datetime.datetime.now().date()
}

def reset_counters():
    today = datetime.datetime.now().date()
    if stats["last_reset"] < today:
        stats["daily"] = 0
        if today.weekday() == 0:  # Понедельник - сброс недельного счетчика
            stats["weekly"] = 0
        if today.day == 1:  # Первый день месяца - сброс месячного счетчика
            stats["monthly"] = 0
        stats["last_reset"] = today

@dp.message(Command("start"))
async def start(message: Message):
    commands_text = (
        "Доступные команды:\n\n"
        "/subscribe - Подписаться на рассылку\n"
        "/stats - Посмотреть статистику красований Артура\n"
        "/send - Отправить сообщение о красовании (только для жителей квартиры 33)\n"
        "/reset - Сбросить дневной счетчик (только для жителей квартиры 33)"
    )
    await message.reply(commands_text)

@dp.message(Command("subscribe"))
async def subscribe(message: Message):
    users.add(message.chat.id)
    await message.reply("Вы подписались на рассылку!")

@dp.message(Command("send"))
async def send_message(message: Message):
    if message.chat.id not in AUTHORIZED_USERS:
        await message.reply("Отправлять сообщения могут только жители квартиры 33!")
        return
   
    reset_counters()
    stats["daily"] += 1
    stats["weekly"] += 1
    stats["monthly"] += 1
   
    emoji1, emoji2 = random.sample(EMOJI_LIST, 2)
    text = f"Да, Артур сегодня красовался перед зеркалом {emoji1}{emoji2}\nУже {stats['daily']} раз(а)!"
   
    for user_id in users:
        try:
            await bot.send_message(user_id, text)
        except Exception as e:
            logging.error(f"Ошибка при отправке сообщения {user_id}: {e}")

@dp.message(Command("reset"))
async def reset_today_counter(message: Message):
    if message.chat.id not in AUTHORIZED_USERS:
        await message.reply("Сбрасывать счетчик могут только жители квартиры 33!")
        return
    
    # Вычитаем дневное значение из недельной и месячной статистики
    daily_count = stats["daily"]
    stats["weekly"] -= daily_count
    stats["monthly"] -= daily_count
    
    # Устанавливаем дневной счетчик в 0
    stats["daily"] = 0
    
    await message.reply(f"Дневной счетчик красований Артура сброшен до 0!")

@dp.message(Command("stats"))
async def send_stats(message: Message):
    reset_counters()
    stats_text = (
        f"Статистика красований Артура перед зеркалом:\n\n"
        f"Сегодня: {stats['daily']} раз(а)\n"
        f"За неделю: {stats['weekly']} раз(а)\n"
        f"За месяц: {stats['monthly']} раз(а)"
    )
    await message.reply(stats_text)

async def main():
    # Запуск бота
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())