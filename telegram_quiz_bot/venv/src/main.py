# Telegram Quiz-bot
# Started 13 april 12:20:20

import mongodb
import config
import telebot
import schedule
import quiz
import game_config
import time
import commands
import mess_controller
from multiprocessing import Process
from telebot.types import Message

bot = telebot.TeleBot(config.TOKEN)


def schedule_polling():
    while True:
        schedule.run_pending()
        time.sleep(1)


schedule.every().day.at(game_config.game_starts).do(quiz.start_quiz)
schedule.every().day.at(game_config.game_finish).do(quiz.finish_quiz)
schedule.every().day.at(game_config.game_alarm).do(commands.on_game_alarm)
p = Process(target=schedule_polling)
p.start()


@bot.message_handler(commands=['help'])
def commands_handler_help(message):
    bot.send_message(message.chat.id, commands.on_help())


@bot.message_handler(commands=['time_to'])
def commands_handler_help(message):
    bot.send_message(message.chat.id, commands.on_time_to())


@bot.message_handler(commands=['stat'])
def commands_handler_help(message):
    bot.send_message(message.chat.id, commands.on_stat(message.chat.id))


@bot.message_handler(commands=['top'])
def commands_handler_help(message):
    bot.send_message(message.chat.id, commands.on_top())


@bot.message_handler(commands=['tickets'])
def commands_handler_help(message):
    bot.send_message(message.chat.id, 'Ваши тикеты: ' + str(commands.tickets(message.chat.id)))


@bot.message_handler(commands=['reset_stat'])
def commands_handler_help(message):
    if commands.reset_stat(message.chat.id):
        bot.send_message(message.chat.id, 'Статистика успешно обнулена')
    else:
        bot.send_message(message.chat.id, 'Недостаточно тикетов')


@bot.message_handler(commands=['start'])
def commands_handler_start(message):
    mongodb.add_user_info(message)
    bot.send_message(message.chat.id, commands.on_start())
    if mongodb.get_state(message.chat.id) == mongodb.AvailableStates.IN_REG:
        bot.send_message(message.chat.id, 'Сколько вам лет?')


@bot.message_handler(func=lambda m: True)
def messages(message: Message):
    state = mongodb.get_state(message.chat.id)
    if state == mongodb.AvailableStates.IN_REG:
        mess_controller.reg(message, bot)
    elif mongodb.game_status():
        if state == mongodb.AvailableStates.IN_GAME:
            mess_controller.already_in_game(message, bot)
        else:
            mess_controller.not_in_game_yet(message, bot)
    else:
        bot.send_message(message.chat.id, 'Вне игры принимаются только команды')


bot.polling()
