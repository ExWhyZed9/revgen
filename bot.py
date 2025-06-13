import os
import random
import re
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import (
    ApplicationBuilder, ContextTypes, MessageHandler, CallbackQueryHandler,
    CommandHandler, filters
)

load_dotenv()
generated_cache = {}

def luhn_checksum(card_number: str) -> int:
    digits = [int(d) for d in card_number]
    checksum = 0
    is_even = True
    for d in reversed(digits):
        if is_even:
            d *= 2
            if d > 9:
                d -= 9
        checksum += d
        is_even = not is_even
    return (10 - checksum % 10) % 10

def detect_brand(bin_code: str) -> str:
    if bin_code.startswith('4'):
        return "Visa"
    if bin_code.startswith(('51','52','53','54','55')):
        return "MasterCard"
    if bin_code.startswith(('34','37')):
        return "American Express"
    if bin_code.startswith('6'):
        return "Discover"
    return "Unknown"

def generate_cc_full(bin_code, exp_month=None, exp_year=None):
    rand_len = 15 - len(bin_code)
    base = bin_code + ''.join(str(random.randint(0,9)) for _ in range(rand_len))
    cc = base + str(luhn_checksum(base))
    month = exp_month or f"{random.randint(1,12):02d}"
    year = exp_year or str(random.randint(2025,2032))
    cvv = f"{random.randint(0,999):03d}"
    return f"{cc}|{month}|{year}|{cvv}"

def generate_txt(data):
    return "\n".join(data).encode('utf-8')

def generate_csv(data):
    header = "CC Number,Expiry Month,Expiry Year,CVV\n"
    rows = [",".join(item.split("|")) for item in data]
    return (header + "\n".join(rows)).encode('utf-8')

async def handle_gen(update: Update, context: ContextTypes.DEFAULT_TYPE, command_mode=False):
    text = " ".join(context.args) if command_mode else update.message.text
    bin_match = re.search(r"(?:\.gen|/gen)\s*(\d{1,15})", text)
    count_match = re.search(r"x(\d{1,3})", text)
    exp_match = re.search(r"exp=(\d{2})\|(\d{4})", text)

    if not bin_match:
        await update.message.reply_text("⚠️ Usage: `/gen <bin> x<qty> exp=MM|YYYY`", parse_mode="Markdown")
        return

    bin_code = bin_match.group(1)
    count = min(int(count_match.group(1)) if count_match else 1, 50)
    exp_month, exp_year = (exp_match.group(1), exp_match.group(2)) if exp_match else (None, None)

    results = [generate_cc_full(bin_code, exp_month, exp_year) for _ in range(count)]
    generated_cache[update.effective_chat.id] = results

    brand = detect_brand(bin_code)
    display = "\n".join(f"{i+1}. {cc}" for i, cc in enumerate(results[:10]))
    if len(results) > 10:
        display += f"\n...and {len(results)-10} more"

    keyboard = [[
        InlineKeyboardButton("⬇️ Export .txt", callback_data='export_txt'),
        InlineKeyboardButton("⬇️ Export .csv", callback_data='export_csv')
    ]]
    await update.message.reply_text(
        f"💳 *{brand} Cards Generated:* \n\n{display}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.lower().startswith(".gen"):
        await handle_gen(update, context)

async def export_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = generated_cache.get(query.message.chat.id)
    if not data:
        await query.edit_message_text("❌ No recent generation found.")
        return

    if query.data == 'export_txt':
        file_data, name = generate_txt(data), "cards.txt"
    else:
        file_data, name = generate_csv(data), "cards.csv"

    await context.bot.send_document(chat_id=query.message.chat.id, document=InputFile(file_data, name))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to the CC Generator Bot!\n\n"
        "Use `/gen <bin> x<qty> exp=MM|YYYY` to generate cards.\n\n"
        "Example:\n"
        "`/gen 457821 x5 exp=07|2028`\n\n"
        "Or simply:\n"
        "`.gen 457821`",
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *Bot Usage Help:*\n\n"
        "`/gen <bin>` - Generate 1 card\n"
        "`/gen <bin> x10` - Generate 10 cards\n"
        "`/gen <bin> x5 exp=08|2030` - Cards with expiry\n\n"
        "_You can also use `.gen 457821 x5` as a message._",
        parse_mode="Markdown"
    )

async def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        print("❌ BOT_TOKEN is missing in environment variables.")
        return

    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("gen", lambda u, c: handle_gen(u, c, command_mode=True)))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(export_callback))
    print("✅ Bot is polling...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if str(e).startswith("This event loop is already running"):
            loop = asyncio.get_event_loop()
            loop.create_task(main())
            loop.run_forever()
        else:
            raise
