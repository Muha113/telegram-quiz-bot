import mongodb
import telebot
import config
import game_config


def start_quiz():
    users = mongodb.get_users()
    bot = telebot.TeleBot(config.TOKEN)
    for x in users:
        bot.send_message(x[mongodb.AvailableFields.ID], 'Игра началась!!!')
    mongodb.switch_game_status()


def finish_quiz():
    users = mongodb.get_users()
    bot = telebot.TeleBot(config.TOKEN)
    for x in users:
        bot.send_message(x[mongodb.AvailableFields.ID], 'Игра окончена!!!')
    update_stat(bot)
    mongodb.switch_game_status()


def update_stat(bot):
    users = mongodb.get_users()
    for x in users:
        if x[mongodb.AvailableFields.STATUS_INGAME]:
            right_ans = mongodb.get_field_value(x[mongodb.AvailableFields.ID], mongodb.AvailableFields.RIGHT_ANSWERS)
            total_ans = mongodb.get_field_value(x[mongodb.AvailableFields.ID], mongodb.AvailableFields.TOTAL_RIGHT_ANSWERS)
            total_games = mongodb.get_field_value(x[mongodb.AvailableFields.ID], mongodb.AvailableFields.TOTAL_GAMES)
            average = mongodb.get_field_value(x[mongodb.AvailableFields.ID], mongodb.AvailableFields.AVERAGE)
            new_average = (total_ans + right_ans) // (total_games + 1)
            res_str = "Ваша статистика\nВсего игр - {0}({1})\nПравильных ответов за игру - {2} из 30\nСреднее правильных ответов по играм - {3}({4})".format(total_games + 1, total_games,
                                                                                                                                                             right_ans, new_average, average)
            bot.send_message(x[mongodb.AvailableFields.ID], res_str)
            to_update = {mongodb.AvailableFields.RIGHT_ANSWERS: 0,
                         mongodb.AvailableFields.AVERAGE: new_average,
                         mongodb.AvailableFields.TOTAL_GAMES: total_games + 1,
                         mongodb.AvailableFields.TOTAL_RIGHT_ANSWERS: total_ans + right_ans,
                         mongodb.AvailableFields.QST_COUNT: 1,
                         mongodb.AvailableFields.STATUS_INGAME: False}
            mongodb.update_db(x[mongodb.AvailableFields.ID], to_update)

    users = mongodb.get_users()
    users = sorted(users, key=lambda k: k[mongodb.AvailableFields.AVERAGE])
    for idx, x in enumerate(users):
        mongodb.update_db(x[mongodb.AvailableFields.ID], {mongodb.AvailableFields.GLOBAL_RANK: idx + 1})


def get_next_question(qst_number):
    if qst_number <= game_config.qst_test:
        qst = mongodb.get_question(mongodb.tests, qst_number)
        res_str = 'Вопрос №{0} (Тестовый)\n{1}?\n1 - {2}\n2 - {3}\n3 - {4}\n4 - {5}'.format(qst_number, qst['question'],
                                                                                            qst['answer1'], qst['answer2'],
                                                                                            qst['answer3'], qst['answer4'])
        return res_str
    else:
        print(qst_number - game_config.qst_test)
        qst = mongodb.get_question(mongodb.non_tests, qst_number - game_config.qst_test)
        res_str = 'Вопрос №{0} (Не тестовый)\n{1}?'.format(qst_number, qst['question'])
        return res_str


def check_ans(chat_id, qst_number, answer):
    if qst_number <= game_config.qst_test:
        qst = mongodb.get_question(mongodb.tests, qst_number)
        if int(answer) == qst['right_answer']:
            temp = mongodb.get_field_value(chat_id, mongodb.AvailableFields.RIGHT_ANSWERS)
            mongodb.update_db(chat_id, {mongodb.AvailableFields.RIGHT_ANSWERS: temp + 1})
    else:
        qst = mongodb.get_question(mongodb.non_tests, qst_number - game_config.qst_test)
        if answer.lower() == qst['right_answer'].lower():
            temp = mongodb.get_field_value(chat_id, mongodb.AvailableFields.RIGHT_ANSWERS)
            mongodb.update_db(chat_id, {mongodb.AvailableFields.RIGHT_ANSWERS: temp + 1})




