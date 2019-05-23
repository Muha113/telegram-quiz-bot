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
from multiprocessing import Process
from telebot.types import Message

bot = telebot.TeleBot(config.TOKEN)


def schedule_polling():
    while True:
        schedule.run_pending()
        time.sleep(1)


schedule.every().day.at(game_config.game_starts).do(quiz.start_quiz)
schedule.every().day.at(game_config.game_finish).do(quiz.finish_quiz)
schedule.every().day.at(game_config.game_alarm).do(commands.on_time_to)
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


@bot.message_handler(commands=['start'])
def commands_handler_start(message):
    mongodb.add_user_info(message)
    bot.send_message(message.chat.id, commands.on_start())
    if mongodb.is_still_reg(message.chat.id):
        bot.send_message(message.chat.id, 'Сколько вам лет?')


@bot.message_handler(func=lambda m: True)
def messages(message: Message):
    if mongodb.is_still_reg(message.chat.id):
        try:
            to_int = int(message.text)
            if to_int > 100 or to_int < 0:
                bot.send_message(message.chat.id, 'По-моему вы врете, напишите еще раз')
            else:
                bot.send_message(message.chat.id, 'Отлично\nВы окончательно зарегистрировались\nОжидайте игры =)')
                mongodb.update_db(message.chat.id, mongodb.AvailableFields.AGE, to_int)
                mongodb.update_db(message.chat.id, mongodb.AvailableFields.STATUS_REG, False)
        except:
            bot.send_message(message.chat.id, 'Я же просил возраст.\nЕще разок')
    elif mongodb.game_status():
        if mongodb.get_field_value(message.chat.id, mongodb.AvailableFields.STATUS_INGAME):
            current_qst_number = mongodb.get_field_value(message.chat.id, mongodb.AvailableFields.QST_COUNT)
            if current_qst_number == game_config.qst_amount:
                quiz.check_ans(message.chat.id, current_qst_number, message.text)
                bot.send_message(message.chat.id, 'Вы ответили на все вопросы\nОжидайте конца игры')
            else:
                quiz.check_ans(message.chat.id, current_qst_number, message.text)
                bot.send_message(message.chat.id, quiz.get_next_question(current_qst_number + 1))
                mongodb.update_db(message.chat.id, mongodb.AvailableFields.QST_COUNT, current_qst_number + 1)
        else:
            if message.text == '!quiz':
                mongodb.update_db(message.chat.id, mongodb.AvailableFields.STATUS_INGAME, True)
                bot.send_message(message.chat.id, 'Ну что, поехали!')
                bot.send_message(message.chat.id, quiz.get_next_question(1))
            else:
                bot.send_message(message.chat.id, 'Идет игра, но похоже вы не учавствуете в ней\n' + \
                                 'Что же, вне игры принимаются только команды\n' + \
                                 'Введите !quiz чтобы начать игру')
    else:
        bot.send_message(message.chat.id, 'Вне игры принимаются только команды')


bot.polling()
