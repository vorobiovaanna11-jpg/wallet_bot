import telebot
from telebot import types
 
bot = telebot.TeleBot('8625638528:AAGupcSdRPzmnoass7ZmBCOu_iV5C9--DmE')
 
user_data = {}   # { chat_id: { 'income': {}, 'expenses': {} } }
user_state = {}  # { chat_id: 'income' | 'expenses' | None }

menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
menu.add(
    types.KeyboardButton("➕ Добавить доход"),
    types.KeyboardButton("➖ Добавить расход"),
    types.KeyboardButton("📊 Итого"),
    types.KeyboardButton("Обнулить данные")
)
 
back = types.ReplyKeyboardMarkup(resize_keyboard=True)
back.add(types.KeyboardButton("🔙 Назад"))

def get_user_data(chat_id):
    if chat_id not in user_data:
        user_data[chat_id] = {'income': {}, 'expenses': {}}
    return user_data[chat_id]
 
@bot.message_handler(commands=['start'])
def start_message(message):
    chat_id = message.chat.id
    user_state[chat_id] = None
    bot.send_message(
        chat_id,
        "Привет! 💸\n\n"
        "Выбери действие в меню.\n\n"
        "После нажатия кнопки введи запись в формате:\n"
        "<b>категория сумма</b>\n\n"
        "Пример: <code>еда 500</code>",
        parse_mode='HTML',
        reply_markup=menu
    )
 
@bot.message_handler(content_types=['text'])
def text_messages(message):
    chat_id = message.chat.id
    text = message.text
    data = get_user_data(chat_id)
 
    if text == "🔙 Назад":
        user_state[chat_id] = None
        bot.send_message(chat_id, "Главное меню:", reply_markup=menu)
 
    elif text == "➕ Добавить доход":
        user_state[chat_id] = 'income'
        bot.send_message(
            chat_id,
            "Введи доход в формате:\n<b>категория сумма</b>\n\nПример: <code>зарплата 50000</code>",
            parse_mode='HTML',
            reply_markup=back
        )
 
    elif text == "➖ Добавить расход":
        user_state[chat_id] = 'expenses'
        bot.send_message(
            chat_id,
            "Введи расход в формате:\n<b>категория сумма</b>\n\nПример: <code>еда 500</code>",
            parse_mode='HTML',
            reply_markup=back
        )
 
    elif text == "📊 Итого":
        show_total(chat_id, data)

    elif text == "Обнулить данные":
        user_data[chat_id] = {'income': {}, 'expenses': {}}
        bot.send_message(chat_id, "Данные обнулены. Ты можешь начать заново!", reply_markup=menu)
 
    else:
        state = user_state.get(chat_id)
        if state in ('income', 'expenses'):
            handle_entry(message, chat_id, data, state)
        else:
            bot.send_message(
                chat_id,
                "Сначала выбери действие в меню 👇",
                reply_markup=menu
            )
 
def handle_entry(message, chat_id, data, state):
    try:
        parts = message.text.strip().split()
        if len(parts) != 2:
            raise ValueError("Неверный формат")
 
        category = parts[0].lower()
        amount = float(parts[1])
 
        if amount <= 0:
            raise ValueError("Сумма должна быть положительной")
 
        storage = data[state]
        storage[category] = storage.get(category, 0) + amount
 
        label = "Доход" if state == 'income' else "Расход"
        bot.send_message(
            chat_id,
            f"✅ {label} добавлен: <b>{category}</b> — {amount:,.0f}\n\n"
            f"Можешь добавить ещё или вернись назад.",
            parse_mode='HTML',
            reply_markup=back
        )
 
    except (ValueError, IndexError):
        bot.send_message(
            chat_id,
            "⚠️ Ошибка! Введи в формате:\n<b>категория сумма</b>\n\nПример: <code>еда 500</code>",
            parse_mode='HTML',
            reply_markup=back
        )
 
 
def show_total(chat_id, data):
    income = data['income']
    expenses = data['expenses']
 
    if not income and not expenses:
        bot.send_message(chat_id, "У тебя пока нет ни доходов, ни расходов.", reply_markup=menu)
        return
 
    response = ""
 
    if income:
        total_in = sum(income.values())
        response += "📈 <b>Доходы:</b>\n"
        for category, amount in income.items():
            response += f"  • {category}: {amount:,.0f}\n"
        response += f"<b>Итого доходов: {total_in:,.0f}</b>\n\n"
 
    if expenses:
        total_sp = sum(expenses.values())
        response += "📉 <b>Расходы:</b>\n"
        for category, amount in expenses.items():
            response += f"  • {category}: {amount:,.0f}\n"
        response += f"<b>Итого расходов: {total_sp:,.0f}</b>\n\n"
 
    if income and expenses:
        balance = sum(income.values()) - sum(expenses.values())
        emoji = "✅" if balance >= 0 else "❌"
        response += f"{emoji} <b>Баланс: {balance:,.0f}</b>"
 
    bot.send_message(chat_id, response, parse_mode='HTML', reply_markup=menu)
 
 
bot.infinity_polling()