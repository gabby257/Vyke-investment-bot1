import threading
import asyncio
from bot import main as bot_main
from app import app

def run_flask():
    app.run(host="0.0.0.0", port=10000)

def run_bot():
    asyncio.run(bot_main())

if __name__ == "__main__":
    t1 = threading.Thread(target=run_flask)
    t2 = threading.Thread(target=run_bot)

    t1.start()
    t2.start()
