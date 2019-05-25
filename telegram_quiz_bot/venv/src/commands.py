import game_config
import mongodb
import telebot
import config
from datetime import datetime, timedelta


def on_help():
    res_str = 'Доступные команды:\n' + \
              '/start - вывод приветствия и основной информации о викторинах\n' + \
              '/help - вывод всех доступных команд с их описанием\n' + \
              '/stat - вывод статистики о ваших играх\n' + \
              '/top - топ 10 игроков\n' + \
              '/time_to - время до следующей игры'
    return res_str


def on_start():
    res_str = 'Привет! Я бот Патрик и люблю викторины\n' + \
              'Поэтому каждый день в 18:00 я стартую викторину\n' + \
              'Длится 30 мин\n' + \
              '30 вопросов, 20 тестовые и 10 нет\n' + \
              'Приходи, Будет весело'
    res_str = res_str + '\n\n' + on_help()
    return res_str


def on_game_alarm():
    bot = telebot.TeleBot(config.TOKEN)
    users = mongodb.get_users()
    for x in users:
        bot.send_message(x[mongodb.AvailableFields.ID], on_time_to())


def on_time_to():
    temp = str(datetime.now().time())
    temp = temp.split('.')
    s1 = temp[0]
    s2 = game_config.game_starts + ':00'
    fmt = '%H:%M:%S'
    delta = datetime.strptime(s2, fmt) - datetime.strptime(s1, fmt)
    if delta.days < 0:
        delta = timedelta(days=0, seconds=delta.seconds, microseconds=delta.microseconds)
    return 'До следующей игры осталось\n' + str(delta)


def reset_stat(chat_id):
    tickets_now = mongodb.get_field_value(chat_id, mongodb.AvailableFields.TICKETS)
    if tickets_now < 100:
        return False
    else:
        to_update = {mongodb.AvailableFields.GLOBAL_RANK: 0,
                     mongodb.AvailableFields.TOTAL_GAMES: 0,
                     mongodb.AvailableFields.AVERAGE: 0,
                     mongodb.AvailableFields.TOTAL_RIGHT_ANSWERS: 0,
                     mongodb.AvailableFields.TICKETS: tickets_now - 10}
        mongodb.update_db(chat_id, to_update)
        return True


def tickets(chat_id):
    return mongodb.get_field_value(chat_id, mongodb.AvailableFields.TICKETS)


def on_stat(chat_id):
    user = mongodb.get_user(chat_id)
    res_str = 'Статистика:\nВсего игр - {0}\n' \
              'Всего правильных ответов - {1}\n' \
              'Средний показатель ответов к игре - {2}\n' \
              'Глобальный ранг - {3}'.format(user[mongodb.AvailableFields.TOTAL_GAMES],
                                             user[mongodb.AvailableFields.TOTAL_RIGHT_ANSWERS],
                                             user[mongodb.AvailableFields.AVERAGE],
                                             user[mongodb.AvailableFields.GLOBAL_RANK])
    return res_str


def on_top():
    res_str = ''
    users = mongodb.get_users()
    users = sorted(users, key=lambda k: k[mongodb.AvailableFields.GLOBAL_RANK], reverse=True)
    skip = 0
    for idx, x in enumerate(users):
        if x[mongodb.AvailableFields.GLOBAL_RANK] == 0:
            skip += 1
            continue
        if idx == 10 + skip:
            break
        res_str += '{0}. {1} {2}, возраст: {3}\n' \
                   'Всего игр - {4}\n' \
                   'Всего правильных ответов - {5}\n' \
                   'Средний показатель ответов к игре - {6}\n\n'.format(x[mongodb.AvailableFields.GLOBAL_RANK],
                                                                        x[mongodb.AvailableFields.FIRST_NAME],
                                                                        x[mongodb.AvailableFields.LAST_NAME],
                                                                        x[mongodb.AvailableFields.AGE],
                                                                        x[mongodb.AvailableFields.TOTAL_GAMES],
                                                                        x[mongodb.AvailableFields.TOTAL_RIGHT_ANSWERS],
                                                                        x[mongodb.AvailableFields.AVERAGE])
    return res_str if res_str else 'Увы никого в топе нет('
