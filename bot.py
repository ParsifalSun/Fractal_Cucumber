# %6703063072:AAEmI99ZiR2bdRId4s0mz3DinqyXD0SX0k8%

''''
import telebot

bot = telebot.TeleBot('6703063072:AAEmI99ZiR2bdRId4s0mz3DinqyXD0SX0k8')

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "Привет":
        bot.send_message(message.from_user.id, "Привет, чем я могу тебе помочь?")
    elif message.text == "/help":
        bot.send_message(message.from_user.id, "Напиши привет")
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /help.")

bot.polling(none_stop=True, interval=0)
'''


import telebot
import random
import time
import subprocess

# Токен вашего бота
TOKEN = '6703063072:AAEmI99ZiR2bdRId4s0mz3DinqyXD0SX0k8'
bot = telebot.TeleBot(TOKEN)

# Словарь с комнатами и их параметрами
rooms = {}


# Обработчик команды /start

@bot.message_handler(commands=['start'], content_types=['text', 'document', 'audio'])
def handle_start(message):
    room_id = random.randint(1000, 9999)

    # Создаем новую комнату и связываем ее с ID пользователя и его ником
    rooms[room_id] = {
        'creator_id': message.chat.id,
        'creator_username': message.chat.username,
        'players': {},
        'game_started': False,
        'target': None
    }

    # Отправляем пользователю ссылку на комнату
    bot.send_message(message.chat.id, f'Создана комната с ID {room_id}. Перейдите по ссылке для регистрации:\n' +
                     f'https://t.me/{bot.get_me().username}?start={room_id}')
""" 
@bot.message_handler(commands=['join'])
def run_join(message):
    subprocess.run(['python', 'join.py'], shell=True, check=True)
"""


# Обработчик регистрационного сообщения
@bot.message_handler(commands=['join'], content_types=['text', 'document', 'audio'])
def handle_registration(message):
    #bot.reply_to(message, 'Введите ID комнаты: ')
    room_id = input('Введите ID комнаты: ')
    #room_id = bot.reply_to(message, 'Введите ID комнаты: ')
    if room_id.isdigit() and int(room_id) in rooms:
        room = rooms[int(room_id)]

        # Добавляем пользователя в комнату
        room['players'][message.chat.id] = {
           # 'fio': None,
            #'class': None,
            #'photo': None,
            'alive': True
        }

        bot.reply_to(message, 'Отправьте свое полное ФИО:')

        @bot.message_handler(func=lambda message: message.text is not None)
        def handle_registration(message):
            room_id = get_room_id(message.chat.id)
            if room_id:
                room = rooms[room_id]
                player = room['players'][message.chat.id]

                if 'fio' not in player:
                    # Сохраняем ФИО пользователя
                    player['fio'] = message.text
                    bot.reply_to(message, 'Отправьте свой класс:')
                elif 'class' not in player:
                    # Сохраняем класс пользователя
                    player['class'] = message.text
                    bot.reply_to(message, 'Отправьте фото:')
                else:

                    # Сохраняем ссылку на фото 1
                    #player['photo'] = message.photo[-1].file_id

                    # Отправляем фото пользователю для подтверждения 1
                    #bot.send_photo(message.chat.id, player['photo'], 'Фото принято')

                    player['photo'] = message.photo

                    bot.reply_to(message, 'Регистрация завершена!')
                    bot.send_message(message.chat.id, 'Для начала игры создатель комнаты должен нажать /start_game')
            else:
                bot.reply_to(message, 'Вы не зарегистрированы в комнате')
    else:
        bot.reply_to(message, 'Комната не существует')




# Обработчик команды /start_game-------------------------------------------------------------------------------------
@bot.message_handler(commands=['start_game'])
def handle_start_game(message):
    room_id = get_room_id(message.chat.id)
    if room_id:
        room = rooms[room_id]
        if room['creator_id'] == message.chat.id:
            room['game_started'] = True

            # Раздаем цели пользователям
            players = list(room['players'].keys())
            random.shuffle(players)
            for i in range(len(players)):
                player = room['players'][players[i]]
                player['target'] = players[(i + 1) % len(players)]
                bot.send_message(players[i], f'Ваша цель: {player["target"]}')

                player_info = "Имя игрока: {}\nКласс игрока: {}\nСсылка на фото: {}".format(player['fio'], player['class'], player['photo'])

                bot.send_message(players[i], player_info)
        else:
            bot.send_message(message.chat.id, 'Вы не являетесь создателем комнаты')
    else:
        bot.send_message(message.chat.id, 'Вы не зарегистрированы в комнате')




# Обработчик команды /kill
@bot.message_handler(commands=['kill'])
def handle_kill(message):
    room_id = get_room_id(message.chat.id)
    if room_id:
        room = rooms[room_id]

        # Проверяем, что игра уже началась
        if room['game_started']:
            player = room['players'][message.chat.id]

            # Проверяем, что игрок еще жив
            if player['alive']:
                target_id = player['target']
                target = room['players'][target_id]

                # Убиваем цель и меняем цель на ее цель
                target['alive'] = False
                player['target'] = target['target']

                bot.send_message(message.chat.id, f'Вы успешно убили игрока {target_id}!')

                # Проверка на победу
                if not any(player['alive'] for player in room['players'].values()):
                    bot.send_message(room['creator_id'], 'Игра окончена. Вы проиграли')
                    for player_id in room['players']:
                        if player_id != room['creator_id']:
                            bot.send_message(player_id, 'Игра окончена. Вы победили!')

            else:
                bot.send_message(message.chat.id, 'Вы уже мертвы')
        else:
            bot.send_message(message.chat.id, 'Игра еще не началась')
    else:
        bot.send_message(message.chat.id, 'Вы не зарегистрированы в комнате')


# Функция для получения ID комнаты, в которой зарегистрирован пользователь
def get_room_id(user_id):
    for room_id, room in rooms.items():
        if user_id in room['players']:
            return room_id
    return None

@bot.message_handler(commands=['players'])

def players_check(message):
    room_id = get_room_id(message.chat.id)
    if room_id:
        room = rooms[room_id]
        #players = list(room['players'].keys())
        #bot.send_message(message.chat.id, f"Игроки: {players}")
        players = list(room['players'].keys())
        for player in players:
            user_info = room['players'][player]
            bot.send_message(message.chat.id,f"{player}: ФИО: {user_info['fio']}, класс: {user_info['class']}, фото: {user_info['photo']}")

    else:
        bot.send_message(message.chat.id, 'Вы не зарегистрированы в комнате')



# Обработчик команды /kick
@bot.message_handler(commands=['kick'])
def kick_players(message):
    room_id = get_room_id(message.chat.id)
    if room_id:
        room = rooms[room_id]
        if room['creator_id'] == message.chat.id:
            players = list(room['players'].keys())
            bot.send_message(message.chat.id, 'Номер игрока, которого нужно удалить: ')
            player_to_remove = message.text.split()[1]  # Получаем номер игрока, которого нужно удалить
            if player_to_remove in players:
                players.remove(player_to_remove)
                bot.send_message(message.chat.id, f'Игрок {player_to_remove} был удален')
            else:
                bot.send_message(message.chat.id, 'Игрок с таким номером не найден')
        else:
            bot.send_message(message.chat.id, 'Вы не являетесь создателем комнаты')
    else:
        bot.send_message(message.chat.id, 'Вы не зарегистрированы в комнате')


# Запуск бота
bot.polling()



