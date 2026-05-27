import os
import sqlite3
from telegram import ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise Exception("TOKEN missing")

# DB
conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY)")
cursor.execute("CREATE TABLE IF NOT EXISTS balances(user_id INTEGER PRIMARY KEY, amount REAL DEFAULT 0)")
conn.commit()

# HELPERS
def get_balance(uid):
    row = cursor.execute("SELECT amount FROM balances WHERE user_id=?", (uid,)).fetchone()
    return row[0] if row else 0

# MENU
def menu():
    return ReplyKeyboardMarkup(
        [["💰 Deposit", "🏧 Withdraw"], ["💳 Balance"]],
        resize_keyboard=True
    )

# START
async def start(update, context):
    uid = update.effective_user.id

    cursor.execute("INSERT OR IGNORE INTO users VALUES(?)", (uid,))
    cursor.execute("INSERT OR IGNORE INTO balances VALUES(?,0)", (uid,))
    conn.commit()

    await update.message.reply_text("Bot is working 🚀", reply_markup=menu())

# HANDLER
async def handle(update, context):
    text = update.message.text
    uid = update.effective_user.id

    bal = get_balance(uid)

    if text == "💳 Balance":
        await update.message.reply_text(f"Balance: ₦{bal}")

    elif text == "💰 Deposit":
        await update.message.reply_text("Send payment to admin")

    elif text == "🏧 Withdraw":
        if bal < 200:
            await update.message.reply_text("❌ Minimum withdrawal is ₦200")
        else:
            await update.message.reply_text("📩 Withdrawal sent")

# MAIN (IMPORTANT FIX)
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
