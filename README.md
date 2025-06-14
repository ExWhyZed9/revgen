# 💳 RevGenBot - Telegram CC Generator

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template/0WqzRl?referralCode=ExWhyZed9)

**RevGenBot** is a Telegram bot that generates valid credit card numbers based on the Luhn algorithm. It supports BIN input, custom expiry dates, and exports in `.txt` or `.csv`. Ideal for testing and educational purposes only.

> 🔗 [Use the bot on Telegram »](https://t.me/revgenbot)

---

## ✨ Features

- ✅ Luhn-based CC generation
- 💼 BIN detection with brand info (Visa, MasterCard, etc.)
- 📅 Optional expiry date input
- 📦 Export results in `.txt` or `.csv`
- 🔘 Inline buttons for easy download
- ⚙️ Command & message-based control
- 👥 Works in group chats too
- 🆕 Update notifications via channel

---

## 🧪 Usage

Send the following formats:

```
.gen 457821
.gen 457821 x10
.gen 457821 x5 exp=08|2030
```

Or use commands:

```
/gen 457821
/gen 457821 x10
/gen 457821 x5 exp=12|2028
```

You’ll get:

- Brand + BIN info
- Generated CC numbers
- Inline buttons to download as `.txt` or `.csv`

---

## 💻 Self-Hosting

### 1. Clone this repo

```bash
git clone https://github.com/ExWhyZed9/revgen.git
cd revgen
```

### 2. Install requirements

```bash
pip install -r requirements.txt
```

### 3. Setup environment

Create a `.env` file or use Railway/GitHub secrets:

```
BOT_TOKEN=your_bot_token_here
```

### 4. Run the bot

```bash
python bot.py
```

---

## 🚀 One-Click Deploy

You can deploy easily using [Railway](https://railway.app):

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template/0WqzRl?referralCode=ExWhyZed9)

---

## 🛡 Disclaimer

This bot is made **for educational and testing purposes only**. It does not generate real credit card information. Do not use it for illegal purposes. We are not responsible for any misuse.

---

## 🤖 Bot Author

- Telegram: [@ExWhyZed9](https://t.me/ExWhyZed9)
- Bot: [@revgenbot](https://t.me/revgenbot)