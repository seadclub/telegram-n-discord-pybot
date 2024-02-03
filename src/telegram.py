import os
from dotenv import load_dotenv
from telebot.async_telebot import AsyncTeleBot
import asyncio
import aiosqlite

load_dotenv()  # take environment variables from .env.
bot = AsyncTeleBot(os.getenv('TELEGRAM_API_TOKEN'))


# admin wrapper
def admin_only(func):
    async def wrapper(message):
        user_info = await bot.get_chat_member(message.chat.id, message.from_user.id)

        if user_info.status in ['creator', 'administrator']:
            await func(message)
        else:
            try:
                await bot.delete_message(message.chat.id, message.message_id)
            except:
                print('Can\'t delete message')
    return wrapper        


# Handle '/start'
@bot.message_handler(commands=['start'], func=lambda message: message.chat.type in ['group', 'supergroup'])
async def send_welcome(message):
    await bot.reply_to(message, 'Hi, I\'m a TG Bot!')

# Handle '/help'
@bot.message_handler(commands=['help'], func=lambda message: message.chat.type in ['group', 'supergroup'])
async def send_info(message):
    await bot.reply_to(message, "For assistance or feedback, DM me on Telegram: @lxudrr.")
    
# Handle '/*' all unknown commands
@bot.message_handler(func=lambda message: message.text.startswith('/') and message.chat.type in ['group', 'supergroup'])
async def handle_unknown_commands(message):
    try:
        await bot.delete_message(message.chat.id, message.message_id)
    except:
        print('It seems desired message doesn\'t exist.')


# Handle 'appreciation'
@bot.message_handler(func=lambda message: any(word in message.text.lower() for word in ['thanks', 'thx', 'thank', 'дякую']) and message.chat.type in ['group', 'supergroup'])
async def handle_all_messages(message):
    try:
        message_sender = message.from_user
        message_receiver = message.reply_to_message.from_user

        # check whether message_sender doesn't reply to himself
        if message_sender.id != message_receiver.id:
            
            # update db
            async with aiosqlite.connect('users.sqlite3') as connection:
                cursor = await connection.cursor()

                # Fetch all user IDs from the database
                await cursor.execute('SELECT * FROM users')
                fetchall = await cursor.fetchall()


                if message_sender.id in [user_id[1] for user_id in fetchall]:
                    pass
                else:
                    # create message_sender's info
                    await cursor.execute(f'INSERT INTO users (user_id, gratitudes) VALUES ("{message_sender.id}", 0)')

                if message_receiver.id in [user_id[1] for user_id in fetchall]:
                    # add gratitude points
                    await cursor.execute(f'UPDATE users SET gratitudes = gratitudes + 1 WHERE user_id = {message_receiver.id}')
                else:
                    # create message_receiver's info
                    await cursor.execute(f'INSERT INTO users (user_id, gratitudes) VALUES ("{message_receiver.id}", 1)')
                
                await connection.commit()
                await cursor.close()


            # show output 
            async with aiosqlite.connect('users.sqlite3') as connection:
                cursor = await connection.cursor()

                await cursor.execute(f'SELECT gratitudes FROM users WHERE user_id = {message_sender.id}')
                message_sender_gratitudes = (await cursor.fetchone())[0]

                await cursor.execute(f'SELECT gratitudes FROM users WHERE user_id = {message_receiver.id}')
                message_receiver_gratitudes = (await cursor.fetchone())[0]
                
                await bot.reply_to(message, f'<b>{message_sender.first_name}</b> ({message_sender_gratitudes}) respected to <b>{message_receiver.first_name}</b> ({message_receiver_gratitudes})', parse_mode='HTML')

                await connection.commit()
                await cursor.close()
    except:
        print('Unable to make a gratitude.')


async def connection_to_db():
    # creating and connecting to the db
    async with aiosqlite.connect('users.sqlite3') as connection:
        # used for handling different tasks with db
        cursor = await connection.cursor()

        # used to prepare table creation
        await cursor.execute('''CREATE TABLE IF NOT EXISTS users
                             (id integer PRIMARY KEY,
                             user_id integer,
                             gratitudes integer)''')
    
        # used to create a table
        await connection.commit()
        await cursor.close()


if __name__ == '__main__':    
    asyncio.get_event_loop().run_until_complete(connection_to_db())
    asyncio.run(bot.polling())
