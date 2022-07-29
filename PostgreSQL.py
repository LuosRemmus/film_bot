from requests import get
import psycopg2
from collections import namedtuple

Film = namedtuple("Film", "film_name_ru, film_name_orig, film_img, film_rating, film_url, film_year, film_length, "
                          "film_description, film_countries, film_genres")

host = 'localhost'
user = 'postgres'
password = 'zex.cmd5d68'
db_name = 'film_bot'
port = '3228'

film_ids = {
    'Комедия': [8124, 6039, 426004, 1355139, 555, 21503, 464282, 2868, 455338],
    'Ужасы': [453397, 386, 944708, 577, 468994, 195563, 273302, 64187, 668, 263447],
    'Боевик': [1318972, 41520, 389, 522, 9691, 3442, 257898, 471, 2717, 666],
    'Драма': [435, 329, 326, 448, 535341, 32898, 387556, 530, 4541, 81555]
}


def get_film(film_id: int) -> Film:
    url = f"https://kinopoiskapiunofficial.tech/api/v2.2/films/{film_id}"
    headers = \
        {
            'X-API-KEY': '0a562c7b-9703-4142-8b60-ea1b4dfbc8c2',
            'Content-Type': 'application/json',
        }

    response = get(url=url, headers=headers).json()

    print(response)

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
        film_countries=', '.join([i['country'] for i in response['countries']]) if len(response['countries']) != 0 else "None",
        film_genres=', '.join([i['genre'] for i in response['genres']]) if len(response['genres']) != 0 else "None"
    )

    return film


try:
    connection = psycopg2.connect(
        host=host,
        user=user,
        password=password,
        database=db_name,
        port=port
    )

    connection.autocommit = True

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT version()"
        )
        print(f'Server version {cursor.fetchone()}')

    for counter, genre in enumerate(film_ids):
        for film in film_ids[genre]:
            with connection.cursor() as cursor:
                current_film = get_film(film)
                cursor.execute(
                    f"""INSERT INTO films(name_ru, name_orig, img, rating, url, year, length, description, countries, genres, genre_id) VALUES (\'{current_film.film_name_ru}\',\'{current_film.film_name_orig}\', \'{current_film.film_img}\', {current_film.film_rating}, \'{current_film.film_url}\', {current_film.film_year}, {current_film.film_length}, \'{current_film.film_description}\', \'{current_film.film_countries}\', \'{current_film.film_genres}\', {counter + 1})"""
                )

                print('[INFO] Successfully inserted')

except Exception as _ex:
    print('[INFO] Error while working with PostgreSQL', _ex)
