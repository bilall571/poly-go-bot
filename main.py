import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice
from datetime import datetime
import os
from threading import Thread
from flask import Flask

# --- 1. XAVFSIZ KALITLAR ---
BOT_TOKEN = os.environ.get("8890786241:AAE4LGeObJnCNRpgpsKVRCd__WScgYW2wfU")
ADMIN_ID = 8450078536  # Sening maxsus ID raqaming

bot = telebot.TeleBot(BOT_TOKEN)

# --- 2. SERVER UCHUN VEB-SAYT (24/7 ishlashi uchun) ---
app = Flask('')

@app.route('/')
def home():
    return "Polygo Bot 24/7 rejimida muvaffaqiyatli ishlamoqda!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- 3. BAZA VA STATISTIKA ---
def save_user(user_id):
    if not os.path.exists('users.txt'):
        with open('users.txt', 'w') as f: f.write(f"{user_id}\n")
        return
    with open('users.txt', 'r') as f: users = f.read().splitlines()
    if str(user_id) not in users:
        with open('users.txt', 'a') as f: f.write(f"{user_id}\n")

def get_users_count():
    if not os.path.exists('users.txt'): return 0
    with open('users.txt', 'r') as f: return len(f.read().splitlines())

def add_stars_to_stats(amount):
    current = 0
    if os.path.exists('stars.txt'):
        with open('stars.txt', 'r') as f:
            try: current = int(f.read().strip())
            except: current = 0
    with open('stars.txt', 'w') as f: f.write(str(current + amount))

def get_total_stars():
    if os.path.exists('stars.txt'):
        with open('stars.txt', 'r') as f:
            try: return int(f.read().strip())
            except: return 0
    return 0

# --- 4. MENYULAR ---
def main_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    btn1 = InlineKeyboardButton("🚀 Muallif loyihalari", callback_data='projects')
    btn2 = InlineKeyboardButton("⭐️ Loyihaga hissa qo'shish", callback_data='donate')
    btn3 = InlineKeyboardButton("📞 Admin bilan aloqa", callback_data='contact')
    btn4 = InlineKeyboardButton("🌐 Ijtimoiy tarmoqlar", callback_data='socials')
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    return markup

def admin_menu():
    markup = InlineKeyboardMarkup(row_width=1)
    btn1 = InlineKeyboardButton("📊 Bot Statistikasi", callback_data='admin_stats')
    btn2 = InlineKeyboardButton("📢 Barchaga xabar yuborish", callback_data='admin_broadcast')
    btn3 = InlineKeyboardButton("🔙 Bosh menyuga qaytish", callback_data='back_to_main')
    markup.add(btn1, btn2, btn3)
    return markup

# --- 5. ASOSIY BUYRUQLAR ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    save_user(message.chat.id)
    text = (f"Salom, {message.from_user.first_name}!\n\n"
            f"Men dasturchi Bilolning rasmiy botiman.\n"
            f"Quyidagi menyu orqali kerakli bo'limni tanlang 👇")
    bot.send_message(message.chat.id, text, reply_markup=main_menu())

@bot.message_handler(commands=['admin'])
def open_admin_panel(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(message.chat.id, "🔐 **POLYGO BOT - ADMIN PANEL**\n\nXush kelibsiz, Bilol!", reply_markup=admin_menu(), parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "❌ Bu bo'lim faqat bot asoschisi uchun!")

# --- 6. TUGMALARNI BOSHQARISH (CALLBACK) ---
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == 'admin_stats':
        if call.message.chat.id != ADMIN_ID: return
        bot.send_message(call.message.chat.id, f"📊 **POLYGO STATISTIKA**\n\n👥 **A'zolar:** {get_users_count()} ta\n⭐️ **Donat:** {get_total_stars()} Stars", parse_mode="Markdown", reply_markup=admin_menu())

    elif call.data == 'admin_broadcast':
        if call.message.chat.id != ADMIN_ID: return
        msg = bot.send_message(call.message.chat.id, "📢 Barchaga yuboriladigan xabarni yozing:")
        bot.register_next_step_handler(msg, process_broadcast)

    elif call.data == 'back_to_main':
        bot.send_message(call.message.chat.id, "Bosh menyu:", reply_markup=main_menu())

    elif call.data == 'projects':
        text = "**Mening Loyihalarim:**\n\n📚 **EEW**\nLink: https://eew-one.vercel.app/\n\n🌍 **Polygo**\nDomen: http://polygo.uz/"
        bot.send_message(call.message.chat.id, text, parse_mode="Markdown", disable_web_page_preview=True)

    elif call.data == 'contact':
        bot.send_message(call.message.chat.id, "👨‍💻 Admin: @mrbilal4")

    elif call.data == 'socials':
        text = "**Ijtimoiy Tarmoqlar:**\n\n🎮 Steam: [Profil](https://steamcommunity.com/profiles/76561199259961267/)\n👾 Discord: bilol1bey\n💻 GitHub: [bilall571](https://github.com/bilall571)"
        bot.send_message(call.message.chat.id, text, parse_mode="Markdown", disable_web_page_preview=True)

    elif call.data == 'donate':
        msg = bot.send_message(call.message.chat.id, "Nechta yulduz (Stars ⭐️) yubormoqchisiz?\nFaqat raqam yozing:")
        bot.register_next_step_handler(msg, process_stars_amount)

# --- 7. XABAR TARQATISH VA TO'LOV TIZIMI ---
def process_broadcast(message):
    if message.chat.id != ADMIN_ID: return
    if not os.path.exists('users.txt'): return
    with open('users.txt', 'r') as f: users = f.read().splitlines()
    for user_id in users:
        try: bot.send_message(int(user_id), message.text)
        except: continue
    bot.send_message(ADMIN_ID, "✅ Xabar muvaffaqiyatli tarqatildi!")

def process_stars_amount(message):
    try:
        amount = int(message.text)
        if amount < 1: return
        prices = [LabeledPrice(label="Polygo va EEW rivoji uchun", amount=amount)]
        bot.send_invoice(message.chat.id, title="Loyihaga Hissa ⭐️", description=f"Polygo uchun {amount} ta yulduz yuborish.", invoice_payload="polygo_donation", provider_token="", currency="XTR", prices=prices)
    except:
        bot.send_message(message.chat.id, "Iltimos, faqat raqam kiriting.")

@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    stars_amount = message.successful_payment.total_amount
    add_stars_to_stats(stars_amount)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    receipt_text = f"🧾 **POLYGO CHEK** 🧾\n━━━━━━━━━━━━━\n👤 **Hissa qo'shuvchi:** {message.from_user.first_name}\n⭐️ **Miqdor:** {stars_amount} Stars\n📅 **Vaqt:** {current_time}\n\nStatus: ✅ Muvaffaqiyatli!"

    if os.path.exists('logo.png'):
        with open('logo.png', 'rb') as photo:
            bot.send_photo(message.chat.id, photo, caption=receipt_text, parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, receipt_text, parse_mode="Markdown")

# --- 8. BOTNI ISHGA TUSHIRISH ---
if __name__ == '__main__':
    keep_alive()
    print("🚀 Polygo Bot muvaffaqiyatli ishga tushdi...")
    bot.infinity_polling()



# Process the response
        try: # <--- MANA SHU SO'Z YETISHMAYAPTI
            bot.reply_to(message, response.text, parse_mode="Markdown")

        except Exception as e: # <--- Endi bu yerdagi qizil chiziq yo'qoladi!
            bot.reply_to(message, "Kechirasiz, xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")
            print(f"Xatolik: {e}")
