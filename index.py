import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import sqlite3
from datetime import datetime

# Bot token va CHAT_ID
BOT_TOKEN = "7588639848:AAFDTvwheblrJTP210tSl3b64sgCyOdaZcE"
CHAT_ID = "7349754297"

bot = telebot.TeleBot(BOT_TOKEN)

# Ma'lumotlar bazasini yaratish
def init_db():
    conn = sqlite3.connect('cyber_users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS cyber_users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    full_name TEXT,
                    role TEXT,
                    position_or_course TEXT,
                    photo_id TEXT,
                    timestamp TEXT)''')
    conn.commit()
    conn.close()

# Foydalanuvchi ma'lumotlarini saqlash
def save_user_data(user_id, full_name, role, position_or_course, photo_id):
    conn = sqlite3.connect('cyber_users.db')
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO cyber_users (user_id, full_name, role, position_or_course, photo_id, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
              (user_id, full_name, role, position_or_course, photo_id, timestamp))
    conn.commit()
    conn.close()

# Foydalanuvchi holatini saqlash uchun vaqtinchalik ma'lumotlar
user_data = {}

# Klaviatura yaratish funksiyalari
def get_main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(KeyboardButton("📸 Rasm yuborish"))
    markup.add(KeyboardButton("❌ Bekor qilish"))
    return markup

def get_role_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(KeyboardButton("👨‍💼 Xodim"))
    markup.add(KeyboardButton("🎓 Talaba"))
    markup.add(KeyboardButton("❌ Bekor qilish"))
    return markup

def get_submit_menu():
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("🚀 Yuborish", callback_data="submit"),
               InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel"))
    return markup

# /start buyrug'i
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {'step': 'awaiting_photo'}
    bot.send_message(message.chat.id,
                     "🔥 *MESI FaceID botga xush kelibsiz!* 🔥\n"
                     "🌐 Tizimga ulanmoqda...\n"
                     "Birinchi qadam: Rasmingizni yuborish uchun quyidagi tugmani bosing! 📸",
                     parse_mode="Markdown", reply_markup=get_main_menu())

# Rasm yuborish tugmasi
@bot.message_handler(content_types=['text'], func=lambda message: message.text == "📸 Rasm yuborish")
def request_photo(message):
    user_id = message.from_user.id
    if user_id in user_data and user_data[user_id]['step'] == 'awaiting_photo':
        bot.send_message(message.chat.id,
                         "💾 *Tayyor!* Rasmingizni yuboring! 📸",
                         parse_mode="Markdown", reply_markup=get_main_menu())
    else:
        bot.send_message(message.chat.id,
                         "⚠️ *Xatolik!* /start buyrug'idan boshlang! 😎",
                         parse_mode="Markdown", reply_markup=get_main_menu())

# Bekor qilish tugmasi
@bot.message_handler(content_types=['text'], func=lambda message: message.text == "❌ Bekor qilish")
def cancel_action(message):
    user_id = message.from_user.id
    if user_id in user_data:
        del user_data[user_id]
    bot.send_message(message.chat.id,
                     "🛑 *Jarayon bekor qilindi!* Qayta boshlash uchun /start ni bosing! 😎",
                     parse_mode="Markdown", reply_markup=get_main_menu())

# Rasmni qabul qilish
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id
    if user_id in user_data and user_data[user_id]['step'] == 'awaiting_photo':
        user_data[user_id]['photo_id'] = message.photo[-1].file_id
        user_data[user_id]['step'] = 'awaiting_full_name'
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(KeyboardButton("🧑‍💻 Ism kiritish"))
        markup.add(KeyboardButton("❌ Bekor qilish"))
        bot.send_message(message.chat.id,
                         "🖥️ *Rasm qabul qilindi!* ✅\n"
                         "Endi to'liq ismingizni kiritish uchun tugmani bosing (masalan, Aliyev Ali). 🌌",
                         parse_mode="Markdown", reply_markup=markup)
    else:
        bot.send_message(message.chat.id,
                         "⚠️ *Xatolik!* /start buyrug'idan boshlang yoki rasmni to'g'ri yuboring! 😎",
                         parse_mode="Markdown", reply_markup=get_main_menu())

# Ism kiritish tugmasi
@bot.message_handler(content_types=['text'], func=lambda message: message.text == "🧑‍💻 Ism kiritish")
def request_full_name(message):
    user_id = message.from_user.id
    if user_id in user_data and user_data[user_id]['step'] == 'awaiting_full_name':
        bot.send_message(message.chat.id,
                         "🔒 *Ism kiritish vaqti!* To'liq ismingizni yuboring (masalan, Aliyev Ali). 💿",
                         parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id,
                         "⚠️ *Xatolik!* /start buyrug'idan boshlang! 😎",
                         parse_mode="Markdown", reply_markup=get_main_menu())

# To'liq ism va boshqa matnlarni qabul qilish
@bot.message_handler(content_types=['text'], func=lambda message: message.text not in ["📸 Rasm yuborish", "❌ Bekor qilish", "🧑‍💻 Ism kiritish", "👨‍💼 Xodim", "🎓 Talaba", "💼 Ma'lumot kiritish"])
def handle_text(message):
    user_id = message.from_user.id
    if user_id not in user_data:
        bot.send_message(message.chat.id,
                         "⚠️ *Tizimga kirish rad etildi!* /start buyrug'idan boshlang! 😎",
                         parse_mode="Markdown", reply_markup=get_main_menu())
        return

    if user_data[user_id]['step'] == 'awaiting_full_name':
        user_data[user_id]['full_name'] = message.text
        user_data[user_id]['step'] = 'awaiting_role'
        bot.send_message(message.chat.id,
                         "🔒 *Ism qabul qilindi!* ✅\n"
                         "Siz xodim yoki talabamisiz? Quyidagi tugmalardan birini tanlang! 👇",
                         parse_mode="Markdown", reply_markup=get_role_menu())

    elif user_data[user_id]['step'] == 'awaiting_position':
        user_data[user_id]['position_or_course'] = message.text
        full_name = user_data[user_id]['full_name']
        role = user_data[user_id]['role']
        position_or_course = user_data[user_id]['position_or_course']
        bot.send_message(message.chat.id,
                         f"🌟 *Ma'lumotlar to'plandi!*\n"
                         f"🧑‍💻 *Ism:* {full_name}\n"
                         f"👤 *Rol:* {role}\n"
                         f"💼 *Lavozim / Yo'nalish va Kurs:* {position_or_course}\n"
                         f"Ma'lumotlar to'g'ri bo'sa 'Yuborish' tugmasini bosing! 👾",
                         parse_mode="Markdown", reply_markup=get_submit_menu())

# Rol tanlash (Xodim yoki Talaba)
@bot.message_handler(content_types=['text'], func=lambda message: message.text in ["👨‍💼 Xodim", "🎓 Talaba"])
def handle_role(message):
    user_id = message.from_user.id
    if user_id in user_data and user_data[user_id]['step'] == 'awaiting_role':
        user_data[user_id]['role'] = message.text
        user_data[user_id]['step'] = 'awaiting_position'
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(KeyboardButton("💼 Ma'lumot kiritish"))
        markup.add(KeyboardButton("❌ Bekor qilish"))
        if message.text == "👨‍💼 Xodim":
            bot.send_message(message.chat.id,
                             "💼 *Xodim tanlandi!* Lavozimingizni kiritish uchun tugmani bosing "
                             "(masalan, O'qituvchi). 🌐",
                             parse_mode="Markdown", reply_markup=markup)
        else:
            bot.send_message(message.chat.id,
                             "🎓 *Talaba tanlandi!* Yo'nalish va kursingizni kiritish uchun tugmani bosing "
                             "(masalan, Axborot Texnologiyalari, 2-kurs). 🌐",
                             parse_mode="Markdown", reply_markup=markup)
    else:
        bot.send_message(message.chat.id,
                         "⚠️ *Xatolik!* /start buyrug'idan boshlang! 😎",
                         parse_mode="Markdown", reply_markup=get_main_menu())

# Ma'lumot kiritish tugmasi
@bot.message_handler(content_types=['text'], func=lambda message: message.text == "💼 Ma'lumot kiritish")
def request_position(message):
    user_id = message.from_user.id
    if user_id in user_data and user_data[user_id]['step'] == 'awaiting_position':
        role = user_data[user_id]['role']
        if role == "👨‍💼 Xodim":
            bot.send_message(message.chat.id,
                             "💼 *Lavozim kiritish vaqti!* Lavozimingizni yuboring (masalan, O'qituvchi). 🌐",
                             parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id,
                             "🎓 *Talaba ma'lumotlari!* Yo'nalish va kursingizni yuboring "
                             "(masalan, Axborot Texnologiyalari, 2-kurs). 🌐",
                             parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id,
                         "⚠️ *Xatolik!* /start buyrug'idan boshlang! 😎",
                         parse_mode="Markdown", reply_markup=get_main_menu())

# Yuborish va Bekor qilish tugmalari
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.from_user.id
    if call.data == "submit":
        if user_id in user_data and user_data[user_id].get('step') == 'awaiting_position':
            full_name = user_data[user_id]['full_name']
            role = user_data[user_id]['role']
            position_or_course = user_data[user_id]['position_or_course']
            photo_id = user_data[user_id]['photo_id']

            # Ma'lumotlarni bazaga saqlash
            save_user_data(user_id, full_name, role, position_or_course, photo_id)

            # Admin ga yuborish
            bot.send_photo(CHAT_ID, photo_id,
                           caption=f"📝 *Yangi foydalanuvchi ma'lumoti:*\n"
                                   f"🧑‍💻 *Ism:* {full_name}\n"
                                   f"👤 *Rol:* {role}\n"
                                   f"💼 *Lavozim / Yo'nalish va Kurs:* {position_or_course}\n"
                                   f"🆔 *User ID:* {user_id}\n"
                                   f"📅 *Vaqt:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                           parse_mode="Markdown")
            bot.send_message(call.message.chat.id,
                             "🎉 *Ma'lumotlaringiz yuborildi. Rahmat!* 🚀\n"
                             "Yana ma'lumot yuborish uchun /start ni bosing! 😎",
                             parse_mode="Markdown", reply_markup=get_main_menu())

            # Vaqtinchalik ma'lumotlarni tozalash
            del user_data[user_id]
        else:
            bot.send_message(call.message.chat.id,
                             "⚠️ *Xatolik!* /start buyrug'idan boshlang! 😎",
                             parse_mode="Markdown", reply_markup=get_main_menu())

    elif call.data == "cancel":
        if user_id in user_data:
            del user_data[user_id]
        bot.send_message(call.message.chat.id,
                         "🛑 *Jarayon bekor qilindi!* Qayta boshlash uchun /start ni bosing! 😎",
                         parse_mode="Markdown", reply_markup=get_main_menu())

# Botni ishga tushirish
if __name__ == "__main__":
    init_db()
    print("🌐 CyberHub Bot ishga tushdi... 🚀")
    bot.polling(none_stop=True)