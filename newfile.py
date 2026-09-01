import sqlite3
import telebot
from telebot import types

TOKEN = "8626286911:AAEgd1UDS3vlJ_Mqg8xeoRE0Xb9JgJvJvb8"
ADMIN_ID = 8792648631
bot = telebot.TeleBot(TOKEN)

def init_db():
    conn = sqlite3.connect("MemoryBase.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER UNIQUE,
            name TEXT,
            balance INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

init_db()

@bot.message_handler(commands=["start"])
def welcome(message):
    u_id = message.from_user.id
    u_name = message.from_user.first_name

    conn = sqlite3.connect("MemoryBase.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO users (user_id, name, balance) VALUES (?, ?, 0)",
        (u_id, u_name),
    )
    conn.commit()

    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (u_id,))
    balance = cursor.fetchone()[0]
    conn.close()

    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("О нас", callback_data="o_nas")
    btn2 = types.InlineKeyboardButton("Прайс", callback_data="price")
    btn3 = types.InlineKeyboardButton("Купить 50 монет за 1 stars", callback_data="buy_stars")
    markup.add(btn1, btn2)
    markup.add(btn3)

    if u_id == ADMIN_ID:
        btn_admin = types.InlineKeyboardButton("Рассылка", callback_data="admin_broadcast")
        markup.add(btn_admin)

    bot.send_message(
        message.chat.id,
        f"Привет, **{u_name}**!\n"
        f"Баланс: **{balance}** coins\n"
        f"Выбор раздела: ",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    bot.answer_callback_query(call.id)
    u_id = call.from_user.id

    if call.data == "o_nas":
        markup = types.InlineKeyboardMarkup()
        btn_back = types.InlineKeyboardButton("Назад", callback_data="main_menu")
        markup.add(btn_back)

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Мы команда разработчиков на python\n\nГлавный разработчик — #imkol",
            reply_markup=markup
        )

    elif call.data == "price":
        markup = types.InlineKeyboardMarkup()
        btn_back = types.InlineKeyboardButton("Назад", callback_data="main_menu")
        markup.add(btn_back)

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="**Прайс-лист:**\n• 1 бот — от 1000₽\n• Бот с базой данных — от 2500₽",
            reply_markup=markup,
            parse_mode="Markdown",
        )

    elif call.data == "buy_stars":
        prices = [types.LabeledPrice(label="50 игровых монет", amount=1)]
        bot.send_invoice(
            chat_id=call.message.chat.id,
            title="Покупка 50 монет",
            description="Мгновенное пополнение игрового баланса из Telegram stars",
            invoice_payload="buy_50_coins_payload",
            provider_token="",
            currency="XTR",
            prices=prices,
            start_parameter="buy-stars-shop",
        )

    elif call.data == "admin_broadcast" and u_id == ADMIN_ID:
        msg = bot.send_message(
            call.message.chat.id,
            "Введите текст объявления для рассылки по всей базе данных:",
        )
        bot.register_next_step_handler(msg, step_broadcast)

    elif call.data == "main_menu":
        conn = sqlite3.connect("MemoryBase.db")
        cursor = conn.cursor()
        cursor.execute("SELECT balance FROM users WHERE user_id = ?", (u_id,))
        balance = cursor.fetchone()[0]
        conn.close()

        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("О нас", callback_data="o_nas")
        btn2 = types.InlineKeyboardButton("Прайс", callback_data="price")
        btn3 = types.InlineKeyboardButton("Купить 50 монет за 1 Stars", callback_data="buy_stars")
        markup.add(btn1, btn2)
        markup.add(btn3)

        if u_id == ADMIN_ID:
            btn_admin = types.InlineKeyboardButton("Рассылка", callback_data="admin_broadcast")
            markup.add(btn_admin)

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"Главное меню:\n\nТвой баланс: **{balance} монет** ",
            reply_markup=markup,
            parse_mode="Markdown",
        )

def step_broadcast(message):
    bc_text = message.text

    conn = sqlite3.connect("MemoryBase.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    all_users = cursor.fetchall()
    conn.close()

    success = 0
    for user in all_users:
        user_id = user[0]
        try:
            bot.send_message(
                user_id,
                f"**ОФИЦИАЛЬНОЕ ОБЪЯВЛЕНИЕ:**\n\n{bc_text}",
                parse_mode="Markdown",
            )
            success += 1
        except Exception:
            pass

    bot.send_message(
        message.chat.id,
        f"**Рассылка завершена!** Успешно доставлено: **{success}** пользователям из базы.",
        parse_mode="Markdown",
    )

@bot.pre_checkout_query_handler(func=lambda query: True)
def process_pre_checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@bot.message_handler(content_types=["successful_payment"])
def process_successful_payment(message):
    u_id = message.from_user.id
    stars_paid = message.successful_payment.total_amount
    coins_to_add = stars_paid * 50

    conn = sqlite3.connect("MemoryBase.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET balance = balance + ? WHERE user_id = ?",
        (coins_to_add, u_id),
    )
    conn.commit()

    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (u_id,))
    new_balance = cursor.fetchone()[0]
    conn.close()

    bot.send_message(
        message.chat.id,
        f"**ОПЛАТА ЗВЁЗДАМИ УСПЕШНА!**\n\n"
        f"• Списано: **{stars_paid} **\n"
        f"• Зачислено: **+{coins_to_add} монет** \n"
        f"Новый баланс в SQLite: **{new_balance} монет**",
        parse_mode="Markdown",
    )

print("imkol_dev")
bot.infinity_polling()