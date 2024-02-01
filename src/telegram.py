from telebot.async_telebot import AsyncTeleBot
import asyncio

bot = AsyncTeleBot('')

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
    await bot.reply_to(message, "Unrecognized command. Type /help")

# Handle 'appreciation'
@bot.message_handler(func=lambda message: any(word in message.text.lower() for word in ['thanks', 'thx', 'thank']))
async def handle_all_messages(message):
    await bot.reply_to(message, f'{message.from_user.id} + 1')

if __name__ == '__main__':    
    asyncio.run(bot.polling())
