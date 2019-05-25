import mongodb
import quiz
import game_config


def reg(message, bot):
    try:
        to_int = int(message.text)
        if to_int > 100 or to_int < 0:
            bot.send_message(message.chat.id, 'По-моему вы врете, напишите еще раз')
        else:
            bot.send_message(message.chat.id, 'Отлично\nВы окончательно зарегистрировались\nОжидайте игры =)')
            to_update = {mongodb.AvailableFields.AGE: to_int, mongodb.AvailableFields.STATE: mongodb.AvailableStates.AFK}
            mongodb.update_db(message.chat.id, to_update)
    except:
        bot.send_message(message.chat.id, 'Я же просил возраст.\nЕще разок')


def already_in_game(message, bot):
    current_qst_number = mongodb.get_field_value(message.chat.id, mongodb.AvailableFields.QST_COUNT)
    if message.text == '!hint':
        tickets_now = mongodb.get_field_value(message.chat.id, mongodb.AvailableFields.TICKETS)
        if tickets_now <= 5:
            bot.send_message(message.chat.id, 'Недостаточно тикетов')
        else:
            quiz.give_hint(current_qst_number)
            mongodb.update_db(message.chat.id, {mongodb.AvailableFields.TICKETS: tickets_now - 5})
    elif current_qst_number > game_config.qst_amount:
        bot.send_message(message.chat.id, 'Вы ответили на все вопросы\nОжидайте конца игры')
    elif current_qst_number == game_config.qst_amount:
        quiz.check_ans(message.chat.id, current_qst_number, message.text)
        bot.send_message(message.chat.id, 'Вы ответили на все вопросы\nОжидайте конца игры')
        mongodb.update_db(message.chat.id, {mongodb.AvailableFields.QST_COUNT: current_qst_number + 1})
    else:
        quiz.check_ans(message.chat.id, current_qst_number, message.text)
        bot.send_message(message.chat.id, quiz.get_next_question(current_qst_number + 1))
        mongodb.update_db(message.chat.id, {mongodb.AvailableFields.QST_COUNT: current_qst_number + 1})


def not_in_game_yet(message, bot):
    if message.text == '!quiz':
        mongodb.update_db(message.chat.id, {mongodb.AvailableFields.STATE: mongodb.AvailableStates.IN_GAME})
        bot.send_message(message.chat.id, 'Ну что, поехали!')
        bot.send_message(message.chat.id, quiz.get_next_question(1))
    else:
        bot.send_message(message.chat.id,
                         'Идет игра, но похоже вы не учавствуете в ней\nЧто же, вне игры принимаются только команды\nВведите !quiz чтобы начать игру')
