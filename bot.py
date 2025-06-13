import os
from telegram.ext import Updater, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputFile
import random, re
from dotenv import load_dotenv

load_dotenv()

generated_cache = {}

def luhn_checksum(card_number):
    digits = [int(d) for d in str(card_number)]
    checksum = 0; is_even = True
    for d in reversed(digits):
        if is_even:
            d *= 2
            if d > 9: d -= 9
        checksum += d
        is_even = not is_even
    return (10 - checksum % 10) % 10

def detect_brand(bin_code):
    if bin_code.startswith('4'): return "Visa"
    if bin_code.startswith(('51','52','53','54','55')): return "MasterCard"
    if bin_code.startswith(('34','37')): return "American Express"
    if bin_code.startswith('6'): return "Discover"
    return "Unknown"

def generate_cc_full(bin_code, exp_month=None, exp_year=None):
    rand_len = 15 - len(bin_code)
    base = bin_code + ''.join(str(random.randint(0,9)) for _ in range(rand_len))
    cc = base + str(luhn_checksum(base))
    month = exp_month or f"{random.randint(1,12):02d}"
    year = exp_year or str(random.randint(2025,2032))
    cvv = f"{random.randint(0,999):03d}"
    return f"{cc}|{month}|{year}|{cvv}"

def generate_txt(data): return "\n".join(data).encode('utf-8')
def generate_csv(data):
    header = "CC Number,Expiry Month,Expiry Year,CVV\n"
    rows = [",".join(item.split("|")) for item in data]
    return (header + "\n".join(rows)).encode('utf-8')

def handle_message(update, context):
    text = update.message.text.strip()
    if not text.startswith(".gen"): return

    bin_match = re.search(r"\.gen\s+(\d{1,15})", text)
    count_match = re.search(r"x(\d{1,3})", text)
    exp_match = re.search(r"exp=(\d{2})\|(\d{4})", text)

    if not bin_match:
        update.message.reply_text("Usage: `.gen <BIN> x<amount> exp=MM|YYYY`", parse_mode="Markdown")
        return

    bin_code = bin_match.group(1)
    count = min(int(count_match.group(1)) if count_match else 1, 50)
    exp_month, exp_year = (exp_match.group(1), exp_match.group(2)) if exp_match else (None, None)

    results = [generate_cc_full(bin_code, exp_month, exp_year) for _ in range(count)]
    generated_cache[update.message.chat_id] = results

    brand = detect_brand(bin_code)
    display = "\n".join(f"{i+1}. {cc}" for i, cc in enumerate(results[:10]))
    if len(results) > 10:
        display += f"\n...and {len(results)-10} more"

    keyboard = [[
        InlineKeyboardButton("⬇️ Export .txt", callback_data='export_txt'),
        InlineKeyboardButton("⬇️ Export .csv", callback_data='export_csv')
    ]]
    update.message.reply_text(f"💳 *{brand} Cards Generated:*\n\n{display}",
                              parse_mode="Markdown",
                              reply_markup=InlineKeyboardMarkup(keyboard))

def export_callback(update, context):
    query = update.callback_query
    data = generated_cache.get(query.message.chat_id)
    if not data:
        query.answer("No recent generation found.")
        return

    if query.data == 'export_txt':
        file_data, name = generate_txt(data), "cards.txt"
    else:
        file_data, name = generate_csv(data), "cards.csv"

    query.answer()
    context.bot.send_document(chat_id=query.message.chat_id,
                             document=InputFile(file_data, name))

def main():
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    if not BOT_TOKEN:
        print("BOT_TOKEN not set in environment!")
        return
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dp.add_handler(CallbackQueryHandler(export_callback))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
