If you don't read the [setup instruction](./setup.md), please do so first.

=== "Pyrogram"
    ```python
    from pyrogram import Client, filters
    from pyrogram.types import Message
    from doti18n import LocaleData

    i18n = LocaleData("locales")
    app = Client("bot", api_id=..., api_hash="...", bot_token="...")
    
    @app.on_message(filters.command("start"))
    async def main(_, message: Message):
        t = i18n[message.from_user.language_code].main
        await message.reply(t.hello)

    app.run()
    ```

=== "Aiogram"
    ```python
    import asyncio
    from aiogram import Bot, Dispatcher
    from aiogram.types import Message
    from aiogram.filters import CommandStart
    from doti18n import LocaleData
    
    i18n = LocaleData("locales")
    dp = Dispatcher()
    
    @dp.message(CommandStart())
    async def main(message: Message):
        t = i18n[message.from_user.language_code].main
        await message.reply(t.hello)
    
    async def main():
        bot = Bot(token="...")
        await dp.start_polling(bot)
    
    if __name__ == "__main__":
        asyncio.run(main())
    ```

=== "Python-Telegram-Bot"
    ```python
    from telegram import Update
    from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
    from doti18n import LocaleData
    
    i18n = LocaleData("locales")
    
    async def main(update: Update, _):
        t = i18n[update.effective_user.language_code].main
        await update.message.reply_text(t.hello)
    
    app = ApplicationBuilder().token("...").build()
    app.add_handler(CommandHandler("start", hello))
    app.run_polling()
    ```

=== "Telethon"
    ```python
    from telethon import TelegramClient, events
    from doti18n import LocaleData
    
    i18n = LocaleData("locales")
    client = TelegramClient("bot", api_id=..., api_hash="...").start(bot_token="...")
    
    @client.on(events.NewMessage(pattern='/start'))
    async def main(event: events.NewMessage.Event):
        user = await event.get_sender()
        t = i18n[user.lang_code].main
        await event.reply(t.hello)
    
    client.run_until_disconnected()
    ```