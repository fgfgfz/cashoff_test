from datetime import datetime as dt
from json import dumps
from sys import exit
from os.path import isdir
from os import mkdir

from requests import Session
from requests.exceptions import HTTPError
from lxml import html
from loguru import logger

from settings import URL
from settings import PROFILE_URL
from settings import WISHLIST_URL
from settings import HEADERS
from logging_config import setup_logging
from decorators import retry_request
from db import Engine


class Parser:
    def __init__(self):
        logger.info('Entering user data')

        self.user = {}
        self.wishlist = []
        self.user_login = input('login: ')
        self.password = input('password: ')
        self.url = URL
        self.profile_url = PROFILE_URL
        self.wishlist_url = WISHLIST_URL
        self.session = Session()
        self.session.headers.update(HEADERS)

    @staticmethod
    def check_status_code(status_code):
        if status_code != 200:
            raise HTTPError('Status code is not 200')

    @retry_request()
    def authorization(self):
        logger.info('Authorization')

        data = {
            'return_url': 'index.php?dispatch=auth.login_form',
            'redirect_url': 'index.php?dispatch=auth.login_form',
            'user_login': self.user_login,
            'password': self.password,
            'dispatch[auth.login]': '',
        }
        response = self.session.post(self.url, data=data)
        self.check_status_code(response.status_code)
        root = html.fromstring(response.text)
        account = root.cssselect('li.ty-account-info__item.ty-account-info__name.ty-dropdown-box__item')

        if not account:
            logger.warning('Incorrect login or password')
            exit(1)

    @retry_request()
    def get_user_data(self):
        logger.info('Getting user data')

        response = self.session.get(self.profile_url)
        self.check_status_code(response.status_code)
        root = html.fromstring(response.text)

        try:
            email = root.cssselect('#email')[0].value
            first_name = root.cssselect('#elm_15')[0].value
            last_name = root.cssselect('#elm_17')[0].value
            city = root.cssselect('#elm_23')[0].value

            # Т.к. при отсутствии значения возвращается пустая строка (обязательное поле только email),
            # а данные сохраняются в БД, лучше присвоить им значения NUll
            self.user['first_name'] = first_name if first_name else None
            self.user['last_name'] = last_name if last_name else None
            self.user['email'] = email
            self.user['city'] = city if city else None

        except (IndexError, AttributeError) as exception:
            logger.exception(f'{exception.__class__.__name__}: {exception}')
            exit(1)

    @retry_request()
    def get_wishlist_data(self):
        logger.info('Getting wishlist data')

        response = self.session.get(self.wishlist_url)
        self.check_status_code(response.status_code)
        root = html.fromstring(response.text)

        try:
            product_cards = root.cssselect('div.col-tile')

            for product in product_cards:
                url = product.cssselect('a.product-title')[0].get('href')
                response_2 = self.session.get(url)
                self.check_status_code(response_2.status_code)
                root = html.fromstring(response_2.text)
                id = root.cssselect('label.ty-control-group__label')[0].get('id').strip('sku_')

                product_data = {
                    'name': self.get_name(root),
                    'retail_price': self.get_retail_price(root, id),
                    'wholesale_price': self.get_wholesale_price(root, id),
                    'rating': self.get_rating(root),
                    'comments_count': self.get_comments_count(root),
                    'in_stores': self.get_in_stores(root),
                    'comments': self.get_comments(root),
                }

                self.wishlist.append(product_data)

        except (IndexError, AttributeError, TypeError) as exception:
            logger.exception(f'{exception.__class__.__name__}: {exception}')
            exit(1)

    @staticmethod
    def get_name(root):
        return str(root.cssselect('h1.ty-product-block-title')[0].text_content())

    # Цен с копейками не нашёл, однако для валидации на всякий случай перевёл во float, а не в int
    @staticmethod
    def get_retail_price(root, id):
        retail_price = root.cssselect(f'#sec_discounted_price_{id}')[0].text
        retail_price = retail_price.replace('\xa0', '').replace(',', '.')
        return float(retail_price)

    # Цен с копейками не нашёл, однако для валидации на всякий случай перевёл во float, а не в int
    @staticmethod
    def get_wholesale_price(root, id):
        wholesale_price = root.cssselect(f'#sec_second_price_{id}')[0].text
        wholesale_price = wholesale_price.replace('\xa0', '').replace(',', '.')
        return float(wholesale_price)

    @staticmethod
    def get_rating(root):
        rating_wrapper = root.cssselect('div.ty-discussion__rating-wrapper')[0]
        stars = rating_wrapper.cssselect('i.ty-stars__icon.ty-icon-star')
        half_stars = rating_wrapper.cssselect('i.ty-stars__icon.ty-icon-star-half')
        return float(len(stars) + len(half_stars) * 0.5)

    @staticmethod
    def get_comments_count(root):
        comments = root.cssselect('div.ty-discussion-post__content.ty-mb-l')
        return len(comments)

    @staticmethod
    def get_in_stores(root):
        stores = root.cssselect('div.ty-product-feature__value')[1:]
        stores = [store for store in stores if 'отсутствует' not in store.text_content()]
        return len(stores)

    @staticmethod
    def get_comments(root):
        comments = []
        comments_data = root.cssselect('div.ty-discussion-post__content.ty-mb-l')

        for comment in comments_data:
            author = comment.cssselect('span.ty-discussion-post__author')[0].text
            public_date = comment.cssselect('span.ty-discussion-post__date')[0].text
            public_date = dt.strptime(public_date, '%d.%m.%Y, %H:%M')
            rating = len(comment.cssselect('i.ty-stars__icon.ty-icon-star'))
            text = comment.cssselect('div.ty-discussion-post__message')[0].text

            comments.append({
                'author': author,
                'public_date': public_date,
                'rating': rating,
                'text': text,
            })

        return comments

    def close_session(self):
        self.session.close()

    @staticmethod
    def format_date(date):
        try:
            return date.isoformat()

        except TypeError as exception:
            logger.exception(f'{exception.__class__.__name__}: {exception}')
            exit(1)

    def save_data(self):
        logger.info('Saving data')

        directory = 'users_data'

        if not isdir(directory):
            mkdir(directory)

        name = self.user['email']
        date = dt.now().strftime('%Y-%m-%d_%H-%M-%S')
        file_name = f'{directory}/{name}_{date}.txt'

        with open(file_name, 'w', encoding='utf-8') as file:
            data = {
                'user': self.user,
                'wishlist': self.wishlist
            }
            file.write(dumps(data, indent=4, ensure_ascii=False, default=self.format_date))

    def load_data_in_database(self):
        logger.info('Loading data')

        db = Engine()
        db.create_tables()
        user_id = db.insert_user(self.user)
        products_names = db.insert_products(self.wishlist)
        db.insert_comments(self.wishlist, products_names)
        db.insert_wishlist(user_id, self.wishlist)


def main():
    setup_logging()
    logger.info('Start program')
    parser = Parser()
    parser.authorization()
    parser.get_user_data()
    parser.get_wishlist_data()
    parser.close_session()
    parser.save_data()
    parser.load_data_in_database()
    logger.info('End program')


if __name__ == '__main__':
    main()
