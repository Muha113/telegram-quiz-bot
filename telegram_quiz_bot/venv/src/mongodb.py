from pymongo import MongoClient
# from telebot.types import Message
import config

client = MongoClient(config.db_localhost, config.db_port)

db = client[config.db_basename]
users = db[config.db_collection_name[0]]
tests = db[config.db_collection_name[1]]
non_tests = db[config.db_collection_name[2]]
game_switch = db[config.db_collection_name[3]]


class AvailableFields:
    ID = 'id'
    FIRST_NAME = 'first_name'
    LAST_NAME = 'last_name'
    QST_COUNT = 'qst_count'
    RIGHT_ANSWERS = 'right_answers'
    TOTAL_RIGHT_ANSWERS = 'total_right_answers'
    GLOBAL_RANK = 'global_rank'
    AVERAGE = 'average'
    TOTAL_GAMES = 'total_games'
    STATE = 'state'
    AGE = 'age'
    TICKETS = 'tickets'


class AvailableStates:
    IN_GAME = 'in_game'
    IN_REG = 'in_reg'
    AFK = 'afk'


def game_status():
    game = game_switch.find()
    return True if game[0]['is_now_game'] else False


def switch_game_status():
    game = game_switch.find()
    new_status = not game[0]['is_now_game']
    game_switch.update_one({'id': 1}, {'$set': {'is_now_game': new_status}}, upsert=False)


def is_registered(chat_id):
    return False if users.find_one({AvailableFields.ID: chat_id}) is not None else True


def get_state(chat_id):
    return get_field_value(chat_id, AvailableFields.STATE)


def add_user_info(message):
    if is_registered(message.chat.id):
        data = {AvailableFields.ID: message.chat.id,
                AvailableFields.FIRST_NAME: message.chat.first_name,
                AvailableFields.LAST_NAME: message.chat.last_name,
                AvailableFields.QST_COUNT: 1,
                AvailableFields.RIGHT_ANSWERS: 0,
                AvailableFields.TOTAL_RIGHT_ANSWERS: 0,
                AvailableFields.GLOBAL_RANK: 0,
                AvailableFields.AVERAGE: 0,
                AvailableFields.TOTAL_GAMES: 0,
                AvailableFields.STATE: AvailableStates.IN_REG,
                AvailableFields.AGE: -1,
                AvailableFields.TICKETS: 0}
        users.insert_one(data).inserted_id


def update_db(chat_id, diction):
    users.update_one({AvailableFields.ID: chat_id}, {'$set': diction}, upsert=False)


def get_field_value(chat_id, field):
    res = users.find_one({AvailableFields.ID: chat_id})
    return res[field]


def get_question(db, number):
    res = db.find_one({AvailableFields.ID: number})
    return res


def get_users():
    return users.find()


def get_user(chat_id):
    return users.find_one({AvailableFields.ID: chat_id})
