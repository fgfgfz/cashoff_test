from datetime import datetime as dt

from requests import Session
from lxml import html

from settings import URL
from settings import PROFILE_URL
from settings import WISHLIST_URL
from settings import HEADERS
from db import Engine


class Parser:
    def __init__(self):
        self.user_data = {}
        self.products_data = []
        self.user_login = input('login: ')
        self.password = input('password: ')
        self.url = URL
        self.profile_url = PROFILE_URL
        self.wishlist_url = WISHLIST_URL
        self.session = Session()
        self.session.headers.update(HEADERS)

    def authorization(self):
        data = {
            'return_url': 'index.php?dispatch=auth.login_form',
            'redirect_url': 'index.php?dispatch=auth.login_form',
            'user_login': self.user_login,
            'password': self.password,
            'dispatch[auth.login]': '',
        }
        self.session.post(self.url, data=data)

    def get_user_data(self):
        response = self.session.get(self.profile_url)
        root = html.fromstring(response.text)

        email = root.cssselect('#email')[0].value
        first_name = root.cssselect('#elm_15')[0].value
        last_name = root.cssselect('#elm_17')[0].value
        city = root.cssselect('#elm_23')[0].value

        # Т.к. при отсутствии значения возвращается пустая строка (обязательное поле только email),
        # а данные сохраняются в БД, лучше присвоить им значения NUll
        self.user_data['first_name'] = first_name if first_name else None
        self.user_data['last_name'] = last_name if last_name else None
        self.user_data['email'] = email
        self.user_data['city'] = city if city else None

    def get_wishlist_data(self):
        response = self.session.get(self.wishlist_url)
        root = html.fromstring(response.text)
        product_cards = root.cssselect('div.col-tile')

        for product in product_cards:
            url = product.cssselect('a.product-title')[0].get('href')
            response_2 = self.session.get(url)
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

            self.products_data.append(product_data)

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
        comments_data = []
        comments = root.cssselect('div.ty-discussion-post__content.ty-mb-l')

        for comment in comments:
            author = comment.cssselect('span.ty-discussion-post__author')[0].text
            public_date = comment.cssselect('span.ty-discussion-post__date')[0].text
            public_date = dt.strptime(public_date, '%d.%m.%Y, %H:%M')
            rating = len(comment.cssselect('i.ty-stars__icon.ty-icon-star'))
            text = comment.cssselect('div.ty-discussion-post__message')[0].text

            comments_data.append({
                'author': author,
                'public_date': public_date,
                'rating': rating,
                'text': text,
            })

        return comments_data

    def close_session(self):
        self.session.close()

    def load_data(self):
        db = Engine()
        db.create_tables()
        user_id = db.insert_user(self.user_data)
        products_names = db.insert_products(self.products_data)
        db.insert_comments(self.products_data, products_names)
        db.insert_wishlist(user_id, self.products_data)


def main():
    parser = Parser()
    parser.authorization()
    parser.get_user_data()
    parser.get_wishlist_data()
    parser.close_session()
    parser.load_data()


if __name__ == '__main__':
    main()
