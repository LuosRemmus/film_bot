import telebot
from telebot import types
from random import choice
from TOKEN import token
import psycopg2

connection = psycopg2.connect(
    host='localhost',
    user='postgres',
    password='zex.cmd5d68',
    database='film_bot',
    port='3228'
)

film_ids = {
    'Комедия': [8124, 6039, 426004, 1355139, 555, 21503, 464282, 2868, 455338],
    'Ужасы': [453397, 386, 944708, 577, 468994, 195563, 273302, 64187, 668, 263447],
    'Боевик': [1318972, 41520, 389, 522, 9691, 3442, 257898, 471, 2717, 666],
    'Драма': [435, 329, 326, 448, 535341, 32898, 387556, 530, 4541, 81555]
}
already_seen = {
    'Комедия': [],
    'Ужасы': [],
    'Боевик': [],
    'Драма': []
}

connection.autocommit = True


def telegram_bot(token):
    bot = telebot.TeleBot(token)

    @bot.message_handler(commands=['start'])
    def start(message):
        bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAEFUmxi2Bohdzk0jYI6F8Jtw4Yvs3DFkQACLxQAAissAAFKQ93cSFVSSYYpBA")
        bot.send_message(message.chat.id,
                         f"Привет <b>{message.from_user.first_name}</b>!\n"
                         f"Я бот, который подскажет тебе что посмотреть.\n"
                         f"Чтобы посмотреть рекомендации фильмов - выбери жанр, нажав /genres", parse_mode='html')

    @bot.message_handler(commands=['genres'])
    def genres(message):
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        btn_1 = types.KeyboardButton('Комедия')
        btn_2 = types.KeyboardButton('Ужасы')
        btn_3 = types.KeyboardButton('Боевик')
        btn_4 = types.KeyboardButton('Драма')
        markup.add(btn_1, btn_2, btn_3, btn_4)

        reply = bot.send_message(message.chat.id, 'Выбери один из жанров', reply_markup=markup)
        bot.register_next_step_handler(reply, genre)

    @bot.message_handler(content_types=['text'])
    def genre(message):
        if message.text in film_ids.keys():
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""SELECT films.* FROM films, genres 
                        WHERE films.genre_id = genres.id AND genres.name = \'{message.text}\'"""
                )

                if len(film_ids[message.text]) != len(already_seen[message.text]):
                    film = choice(cursor.fetchall())
                    print(film)

                    while film in already_seen[message.text]:
                        film = choice(cursor.fetchall())

                    bot.send_photo(message.chat.id, film[2],
                                   f"<b>{film[0]}</b> <i>({film[1]})</i> <b>{film[5]}</b>\n\n"
                                   f"Рейтинг кинопоиска: {film[3]}\n"
                                   f"Длительность фильме: {film[6]} минут\n"
                                   f"Страна: {film[8]}\n"
                                   f"Жанр: {film[9]}\n\n"
                                   f"Описание:\n<i>{film[7]}</i>\n\n"
                                   f"{film[4]}", parse_mode='html')
                    already_seen[message.text].append(film)
                else:
                    bot.send_message(message.chat.id, "Я уже порекомендовал все фильмы из этого жинра")
        else:
            bot.send_message(message.chat.id, "Я тебя не понимаю")

    bot.polling()


if __name__ == '__main__':
    telegram_bot(token)
