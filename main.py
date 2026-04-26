import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

class MyBot(commands.Bot):
        def __init__(self):
            intents = discord.Intents.default()
            intents.message_content = True
            super().__init__(command_prefix="!", intents=intents)

        async def setup_hook(self):
            # 1. thread_cogからViewを読み込んで登録（これだけでOK）
            from thread_cog import SetupView, ThreadManageView
            self.add_view(SetupView())
            self.add_view(ThreadManageView())

            # 2. Cogを読み込む
            await self.load_extension("thread_cog")
            await self.tree.sync()

bot = MyBot()

def main():
    token = os.getenv("DISCORD_TOKEN")
    if token is None:
        print("DISCORD_TOKENが設定されていません。")
        print("環境変数にDISCORD_TOKENを設定してください。")
        return
    keep_alive()

    try:
        bot.run(token)
    except Exception as e:
        print(f"エラーが発生しました: {e}")

# 起動

if __name__ == "__main__":
    main()