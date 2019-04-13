# Telegram Quiz-bot
# Started 13 april 12:20:20

import requests
import telebot
from telebot.types import Message

BASE_URL = 'https://api.telegram.org/bot872301715:AAHRbYsReiIIPHNENXvCnSmuIJoINuLEQBA/'
TOKEN = '872301715:AAHRbYsReiIIPHNENXvCnSmuIJoINuLEQBA'

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start', 'help'])
def commands_handler(message: Message):
    if message.text == '/help':
        bot.send_message(message.chat.id, "/start - starts the bot\n/help - show list of commands\n")


@bot.message_handler(func=lambda m: True)
def echo_all(message):
    bot.reply_to(message, message.text)


bot.polling()
