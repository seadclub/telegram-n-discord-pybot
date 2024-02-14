import aiosqlite

async def connection_to_db():
    # creating and connecting to the db
    async with aiosqlite.connect('db.sqlite3') as connection:
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


async def forward_message(message):
    try:
        async with aiosqlite.connect('db.sqlite3') as connection:
            cursor = await connection.cursor()
            await cursor.execute('SELECT * FROM topics')
            topic_names = await cursor.fetchall()
            await cursor.close()
        for value in topic_names:
            if message.text[1:] == value[2]:
                await bot.forward_message(message.chat.id, message.chat.id, message.reply_to_message.id, message_thread_id=value[1])
                await bot.delete_messages(message.chat.id, [message.message_id, message.reply_to_message.id])
                return
        await bot.delete_message(message.chat.id, message.message_id)
    except Exception as e:
        await bot.delete_message(message.chat.id, message.message_id)
        print(f'Error in the forward_message func: {e}')

