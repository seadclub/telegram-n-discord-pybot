import os
from dotenv import load_dotenv
from telebot.async_telebot import AsyncTeleBot
import asyncio
import aiosqlite
from time import time

load_dotenv()  # take environment variables from .env.
bot = AsyncTeleBot(os.getenv('TELEGRAM_API_TOKEN'))


# admin wrapper
def admin_only(func):
    async def wrapper(message):
        try:
            user_info = await bot.get_chat_member(message.chat.id, message.from_user.id)

            if user_info.status in ['creator', 'administrator']:
                await func(message)
            else:
                await bot.delete_message(message.chat.id, message.message_id)
        except Exception as e:
            print(f'Error in the admin_only wrapper func: {e}')
    return wrapper        

# group only wrapper
def group_only(func):
    async def wrapper(message):
        try:
            if message.chat.type in ['group', 'supergroup']:
                await func(message)
        except Exception as e:
            print(f'Error in the group_only wrapper func: {e}')
    return wrapper

# ban a user
@bot.message_handler(commands=['ban', 'kick'])
@group_only
@admin_only
async def ban(message):
    try:
        if message.reply_to_message:
            if not message.reply_to_message.from_user.is_bot and not (await bot.get_chat_member(message.chat.id, message.reply_to_message.from_user.id)).status in ['creator', 'administrator']:
                await bot.ban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
                await bot.delete_message(message.chat.id, message.message_id)
            else:
                await bot.delete_message(message.chat.id, message.message_id)
        else:
            await bot.delete_message(message.chat.id, message.message_id)
    except Exception as e:
        print(f'Error in the ban func: {e}')

# mute a user
@bot.message_handler(commands=['mute'])
@group_only
@admin_only
async def mute(message):
    try:
        if message.reply_to_message:
            if not message.reply_to_message.from_user.is_bot and not (await bot.get_chat_member(message.chat.id, message.reply_to_message.from_user.id)).status in ['creator', 'administrator']:
                mute_time = int(time()) + int(message.text.split(' ')[1])*60
                await bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, mute_time)
                await bot.delete_message(message.chat.id, message.message_id)
            else:
                await bot.delete_message(message.chat.id, message.message_id)
        else:
            await bot.delete_message(message.chat.id, message.message_id)
    except Exception as e:
        print(f'Error in the mute func: {e}')

# Delete info messages
@bot.message_handler(func=lambda message: True, content_types=['new_chat_members', 'left_chat_member'])
async def delete_info_message(message):
    try:
        await bot.delete_message(message.chat.id, message.message_id)
    except Exception as e:
        print(f'Error in the delete_invite_message func: {e}')

# Handle '/start'
@bot.message_handler(commands=['start'])
@group_only
async def send_welcome(message):
    await bot.reply_to(message, 'Hi, I\'m a TG Bot!')

# Handle '/help'
@bot.message_handler(commands=['help'])
@group_only
async def send_info(message):
    await bot.reply_to(message, "For assistance or feedback, DM me on Telegram: @lxudrr.")
    
# Handle '/*' all unknown commands
@bot.message_handler(func=lambda message: message.text.startswith('/'))
@group_only
async def handle_unknown_commands(message):
    await bot.delete_message(message.chat.id, message.message_id)

# Handle 'appreciation'
@bot.message_handler(func=lambda message: any(word in message.text.lower() for word in ['thanks', 'thx', 'thank', 'дякую']))
@group_only
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
    except Exception as e:
        print(f'Error in the handle_all_messages func: {e}')


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

        await cursor.execute('''CREATE TABLE IF NOT EXISTS topics
                             (id integer PRIMARY KEY,
                             topic_id integer,
                             name char(100))''')

        await connection.commit()
        await cursor.close()


if __name__ == '__main__':    
    asyncio.get_event_loop().run_until_complete(connection_to_db())
    asyncio.run(bot.polling())
