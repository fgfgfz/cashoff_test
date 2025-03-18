from os import getenv

from dotenv import load_dotenv


load_dotenv()


# Parser settings
URL = 'https://siriust.ru/'

PROFILE_URL = f'{URL}profiles-update/'

WISHLIST_URL = f'{URL}wishlist/'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
}


# DataBase settings
LOGIN = getenv('LOGIN')

PASSWORD = getenv('PASSWORD')

HOST = getenv('HOST')

PORT = getenv('PORT')

DATABASE = getenv('DATABASE')

SCHEMA = getenv('SCHEMA')
