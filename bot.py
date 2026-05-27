import os
import sqlite3
from telegram import ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# TOKEN from Render environment
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise Exception("TOKEN is missing in environment variables")

# DB
conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY)")
cursor.execute("CREATE TABLE IF NOT EXISTS balances(user_id INTEGER PRIMARY KEY, amount REAL DEFAULT 0)")
cursor.execute("""
CREATE TABLE IF NOT EXISTS withdrawals(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    amount REAL,
    status TEXT
)
""")
conn.commit()

# HELPERS
def get_balance(uid):
    row = cursor.execute("SELECT amount FROM balances WHERE user_id=?", (uid,)).fetchone()
    return row[0] if row else 0

def set_balance(uid, amount):
    cursor.execute("INSERT OR IGNORE INTO balances VALUES(?,0)", (uid,))
    cursor.execute("UPDATE balances SET amount=? WHERE user_id=?", (amount, uid))
    conn.commit()

# MENU
def menu():
    return ReplyKeyboardMarkup([
        ["💰 Deposit", "🏧 Withdraw"],
        ["💳 Balance"]
    ], resize_keyboard=True)

# START COMMAND
async def start(update, context):
    uid = update.effective_user.id

    cursor.execute("INSERT OR IGNORE INTO users VALUES(?)", (uid,))
    cursor.execute("INSERT OR IGNORE INTO balances VALUES(?,0)", (uid,))
    conn.commit()

    await update.message.reply_text("Welcome 🚀", reply_markup=menu())

# MESSAGE HANDLER
async def handle(update, context):
    text = update.message.text
    uid = update.effective_user.id

    balance = get_balance(uid)

    if text == "💰 Deposit":
        await update.message.reply_text("Send payment and contact admin.")

    elif text == "💳 Balance":
        await update.message.reply_text(f"Balance: ₦{balance}")

    elif text == "🏧 Withdraw":
        if balance < 200:
            await update.message.reply_text("❌ Minimum withdrawal is ₦200")
        else:
            cursor.execute(
                "INSERT INTO withdrawals(user_id, amount, status) VALUES(?,?,?)",
                (uid, balance, "pending")
            )
            conn.commit()

            await update.message.reply_text("📩 Withdrawal request sent to admin")

# MAIN FUNCTION (IMPORTANT FIX)
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
