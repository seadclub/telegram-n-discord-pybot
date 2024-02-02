import os
from dotenv import load_dotenv
from telebot.async_telebot import AsyncTeleBot
import asyncio
import aiosqlite

load_dotenv()  # take environment variables from .env.
bot = AsyncTeleBot(os.getenv('TELEGRAM_API_TOKEN'))

# Handle '/start'
@bot.message_handler(commands=['start'])
async def send_welcome(message):
    await bot.reply_to(message, 'Hi, I\'m a TG Bot!')

# Handle '/help'
@bot.message_handler(commands=['help'])
async def send_info(message):
    await bot.reply_to(message, "For assistance or feedback, DM me on Telegram: @lxudrr.")
    
# Handle '/*' all unknown commands
@bot.message_handler(func=lambda message: message.text.startswith('/'))
async def handle_unknown_commands(message):
    try:
        await bot.delete_message(message.chat.id, message.message_id)
    except:
        print('It seems desired message doesn\'t exist.')


# Handle 'appreciation'
@bot.message_handler(func=lambda message: any(word in message.text.lower() for word in ['thanks', 'thx', 'thank']))
async def handle_all_messages(message):
    await bot.reply_to(message, f'{message.from_user.id} + 1')


async def connection_to_db():
    # creating and connecting to the db
    async with aiosqlite.connect('users.sqlite3') as connection:
        # used for handling different tasks with db
        cursor = await connection.cursor()

        # used to prepare table creation
        await cursor.execute('''CREATE TABLE IF NOT EXISTS users
                             (id integer PRIMARY KEY,
                             name varchar(100),
                             gratitudes integer)''')
    
        # used to create a table
        await connection.commit()
        await cursor.close()


if __name__ == '__main__':    
    asyncio.get_event_loop().run_until_complete(connection_to_db())
    asyncio.run(bot.polling())
