import telebot
from telebot import types
from random import choice
from TOKEN import token
import sqlalchemy as db
from requests import get
from collections import namedtuple
from sqlalchemy import Column, Integer, UnicodeText, Float

Film = namedtuple("Film", "film_name_ru, film_name_orig, film_img, film_rating, film_url, film_year, film_length, "
                          "film_description, film_countries, film_genres, genre_id")

engine = db.create_engine('sqlite:///Kinopoisk.db', connect_args={'check_same_thread': False})
connection = engine.connect()
metadata = db.MetaData()

films_table = db.Table('films', metadata,
                       Column('id', Integer, primary_key=True, nullable=False),
                       Column('film_name_ru', UnicodeText),
                       Column('film_name_orig', UnicodeText),
                       Column('film_img', UnicodeText),
                       Column('film_rating', Float),
                       Column('film_url', UnicodeText),
                       Column('film_year', Integer),
                       Column('film_length', Integer),
                       Column('film_description', UnicodeText),
                       Column('film_countries', UnicodeText),
                       Column('film_genres', UnicodeText),
                       Column('genre_id', UnicodeText),
                       )

metadata.create_all(engine)

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


def push(film_name_ru, film_name_orig, film_img, film_rating, film_url, film_year, film_length,
         film_description, film_countries, film_genres, genre_id):
    try:
        insert_query = films_table.insert().values({
            'film_name_ru': film_name_ru,
            'film_name_orig': film_name_orig,
            'film_img': film_img,
            'film_rating': film_rating,
            'film_url': film_url,
            'film_year': film_year,
            'film_length': film_length,
            'film_description': film_description,
            'film_countries': film_countries,
            'film_genres': film_genres,
            'genre_id': genre_id
        })

        connection.execute(insert_query)
        return "[INFO] Data pushed successfully!"
    except:
        return "[INFO] Error while pushing"


def get_film(film_id: int, genre_id: str) -> Film:
    url = f"https://kinopoiskapiunofficial.tech/api/v2.2/films/{film_id}"
    headers = \
        {
            'X-API-KEY': '0a562c7b-9703-4142-8b60-ea1b4dfbc8c2',
            'Content-Type': 'application/json',
        }

    response = get(url=url, headers=headers).json()

    get_attribute = lambda attr_name: response[attr_name] if response[attr_name] is not None else "None"

    film = Film(
        film_name_ru=get_attribute("nameRu").replace("'", "`"),
        film_name_orig=get_attribute('nameOriginal').replace("'", "`"),
        film_img=get_attribute('posterUrl'),
        film_rating=get_attribute('ratingKinopoisk'),
        film_url=get_attribute('webUrl'),
        film_year=get_attribute('year'),
        film_length=get_attribute('filmLength'),
        film_description=get_attribute('description').replace("'", "`"),
        film_countries=', '.join([i['country'] for i in response['countries']]) if len(
            response['countries']) != 0 else "None",
        film_genres=', '.join([i['genre'] for i in response['genres']]) if len(response['genres']) != 0 else "None",
        genre_id=genre_id
    )

    return film


def return_film(genre_id):
    select_query = db.select([films_table]).where(films_table.columns.genre_id == genre_id)
    film = choice(connection.execute(select_query).fetchall())
    print(film)
    return film


def telegram_bot(token):
    bot = telebot.TeleBot(token)

    @bot.message_handler(commands=['start'])
    def start(message):
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
            if len(film_ids[message.text]) != len(already_seen[message.text]):
                film = return_film(message.text)

                while film in already_seen[message.text]:
                    film = return_film(message.text)

                bot.send_photo(message.chat.id, film[3],
                               f"<b>{film[1]}</b> <i>({film[2]})</i> <b>{film[6]}</b>\n\n"
                               f"Рейтинг кинопоиска: {film[4]}\n"
                               f"Длительность фильме: {film[7]} минут\n"
                               f"Страна: {film[9]}\n"
                               f"Жанр: {film[10]}\n\n"
                               f"Описание:\n<i>{film[8]}</i>\n\n"
                               f"{film[5]}", parse_mode='html')
                already_seen[message.text].append(film)
            else:
                bot.send_message(message.chat.id, "Я уже порекомендовал все фильмы из этого жанра")
        else:
            bot.send_message(message.chat.id, "Я тебя не понимаю")

    bot.polling()


if __name__ == '__main__':
    for genre in film_ids:
        for id in film_ids[genre]:
            data = get_film(id, genre)
            print("Film's data get successfully!")
            push(data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9], data[10])
            print("Film's data pushed successfully!")
    telegram_bot(token)
