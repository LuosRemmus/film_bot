from requests import get
import telebot
from telebot import types
from random import choice
from TOKEN import token

film_ids = {
    'Комедия': [8124, 6039, 426004, 1355139, 555, 21503, 464282, 2868, 455338],
    'Ужасы': [453397, 386, 944708, 577, 468994, 195563, 273302, 64187, 668, 263447],
    'Боевик': [1318972, 41520, 389, 522, 9691, 3442, 257898, 471, 2717, 666],
    'Драма': [435, 329, 326, 448, 535341, 32898, 387556, 530, 4541, 81555]
}


def get_film(film_id: int) -> dict:
    url = f"https://kinopoiskapiunofficial.tech/api/v2.2/films/{film_id}"
    headers = \
        {
            'X-API-KEY': '0a562c7b-9703-4142-8b60-ea1b4dfbc8c2',
            'Content-Type': 'application/json',
        }

    response = get(url=url, headers=headers).json()

    film_name_ru = response['nameRu']
    film_name_orig = response['nameOriginal']
    film_img = response['posterUrl']
    film_rating = response['ratingKinopoisk']
    film_url = response['webUrl']
    film_year = response['year']
    film_length = f"{int(response['filmLength'] // 60)}ч. {int(response['filmLength'] % 60)}м. " \
                  f"({response['filmLength']} минут)"
    film_description = response['description']
    film_countries = ', '.join([i['country'] for i in response['countries']])
    film_genres = ', '.join([i['genre'] for i in response['genres']])

    film = {
        "film_name_ru": film_name_ru,
        "film_name_orig": film_name_orig,
        "film_img": film_img,
        "film_rating": film_rating,
        "film_url": film_url,
        "film_year": film_year,
        "film_length": film_length,
        "film_description": film_description,
        "film_countries": film_countries,
        "film_genres": film_genres
    }

    return film


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
        print(message.text)
        if message.text in film_ids.keys():
            film = get_film(choice(film_ids[message.text]))
            bot.send_photo(message.chat.id, film['film_img'],
                           f"<b>{film['film_name_ru']}</b> <i>({film['film_name_orig']})</i> <b>{film['film_year']}</b>\n\n"
                           f"Рейтинг кинопоиска: {film['film_rating']}\n"
                           f"Длительность фильме: {film['film_length']}\n"
                           f"Страна: {film['film_countries']}\n"
                           f"Жанр: {film['film_genres']}\n\n"
                           f"Описание:\n<i>{film['film_description']}</i>\n\n"
                           f"{film['film_url']}", parse_mode='html')
        else:
            bot.send_message(message.chat.id, "Я тебя не понимаю")

    bot.polling()


if __name__ == '__main__':
    telegram_bot(token)
