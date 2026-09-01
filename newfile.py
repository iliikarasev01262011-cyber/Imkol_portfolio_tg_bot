import os
import telebot
from telebot import types
from flask import Flask
import sqlite3


# Токен из настроек Render
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8287534964 # Твой ID (проверь, что он верный)

bot = telebot.TeleBot(TOKEN)

# Настройка веб-сервера, чтобы Render не убивал бота
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

# --- База данных ---
def init_db():
    conn = sqlite3.connect('MemoryBase.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER UNIQUE,
        name TEXT,
        balance INTEGER DEFAULT 0
    )""")
    conn.commit()
    conn.close()

init_db()

# --- Состояния ---
user_state = {} 

# --- Меню ---
def main_menu():
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Мои навыки", callback_data="naviki")
    btn2 = types.InlineKeyboardButton("Мои услуги", callback_data="uslugi")
    btn3 = types.InlineKeyboardButton("Мой прайс", callback_data="price")
    btn4 = types.InlineKeyboardButton("Время работ", callback_data="rabot")
    btn5 = types.InlineKeyboardButton("Гарантия", callback_data="garant")
    btn6 = types.InlineKeyboardButton("График", callback_data="grafik")
    btn7 = types.InlineKeyboardButton("📝 Оставить заявку", callback_data="zayavka")
    btn8 = types.InlineKeyboardButton("Связь", url="https://t.me/imkol_official_channel")
    btn9 = types.InlineKeyboardButton("Новостной канал", url = "https://t.me/imkol_dev")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9)
    return markup

# --- Обработчики ---
@bot.message_handler(commands=["start"])
def welcome(message):
    bot.send_message(message.chat.id, "**Добро пожаловать в моё портфолио!**\n\nЯ — разработчик Telegram-ботов на Python.\n⬇️ **Выберите раздел:**", reply_markup=main_menu(), parse_mode="Markdown")

@bot.message_handler(content_types=['text', 'contact'])
def handle_text(message):
    user_id = message.chat.id
    if user_state.get(user_id) == 'waiting_name':
        user_state[user_id] = 'waiting_phone'
        user_state['name'] = message.text
        bot.send_message(user_id, "Отлично! Теперь отправьте ваш номер телефона (нажмите кнопку ниже).", reply_markup=phone_keyboard())
    elif user_state.get(user_id) == 'waiting_phone':
        if message.contact:
            phone = message.contact.phone_number
        else:
            phone = message.text
        name = user_state.get('name')
        username = message.from_user.username
        conn = sqlite3.connect('MemoryBase.db', check_same_thread=False)
        cur = conn.cursor()
        cur.execute("INSERT OR IGNORE INTO users (user_id, name, balance) VALUES (?, ?, 0)", (user_id, name))
        conn.commit()
        conn.close()
        try:
            bot.send_message(ADMIN_ID, f"🔥 Новая заявка!\n\n👤 Имя: {name}\n📱 Телефон: {phone}\n🆔 @{username}")
        except:
            pass
        bot.send_message(user_id, "✅ Заявка принята! Мы свяжемся с вами в ближайшее время.", reply_markup=types.ReplyKeyboardRemove())
        user_state[user_id] = None

@bot.callback_query_handler(func=lambda call: True)
def handle_inline(call):
    bot.answer_callback_query(call.id)
    if call.data == "naviki":
        text = "**Наши навыки:**\n\n• Python\n• Telebot\n• SQLite (базы данных)\n• Inline-кнопки\n• Регистрация и анкеты\n• Админ-панели и рассылки"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 Назад", callback_data="main_menu"))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=markup, parse_mode="Markdown")
    elif call.data == "uslugi":
        text = "**Наши услуги:**\n\n• Бот-визитка с кнопками и меню\n• Бот с регистрацией и базой данных\n• Бот с админ-панелью и рассылками\n• Бот с инлайн-меню и разделами"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 Назад", callback_data="main_menu"))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=markup, parse_mode="Markdown")
    elif call.data == "price":
        text = "**Мой прайс:**\n\n• Бот-визитка — от 700 ₽\n• Бот с БД и регистрацией — от 2500 ₽\n• Бот с админ-панелью — от 4000 ₽"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 Назад", callback_data="main_menu"))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=markup, parse_mode="Markdown")
    elif call.data == "rabot":
        text = "**Время работ:**\n\n• Бот-визитка — 1–2 дня\n• Бот с БД — 2–4 дня\n• Бот с админкой — 3–5 дней"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 Назад", callback_data="main_menu"))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=markup, parse_mode="Markdown")
    elif call.data == "garant":
        text = "**Гарантия:**\n\n1 месяц бесплатной поддержки и исправления багов."
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 Назад", callback_data="main_menu"))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=markup, parse_mode="Markdown")
    elif call.data == "grafik":
        text = "**График работы:**\n\nПн–Пт: 17:00–22:00\nСб: 17:00–02:00\nВс: выходной\n\nЧасовой пояс: МСК"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 Назад", callback_data="main_menu"))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=markup, parse_mode="Markdown")
    elif call.data == "zayavka":
        user_state[call.message.chat.id] = 'waiting_name'
        bot.send_message(call.message.chat.id, "Введите ваше имя:", reply_markup=types.ReplyKeyboardRemove())
    elif call.data == "main_menu":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="**Добро пожаловать в моё портфолио!**\n\nЯ — разработчик Telegram-ботов на Python.\n⬇️ **Выберите раздел:**", reply_markup=main_menu(), parse_mode="Markdown")

def phone_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn = types.KeyboardButton("📱 Отправить мой номер", request_contact=True)
    markup.add(btn)
    return markup

# --- Запуск ---
if __name__ == '__main__':
    import threading
    # Запускаем бота в отдельном потоке
    threading.Thread(target=bot.infinity_polling, daemon=True).start()
    
    # Запускаем Flask-сервер, чтобы Render думал, что у нас сайт (и не убивал нас)
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
