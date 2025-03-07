from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from settings import LOGIN
from settings import PASSWORD
from settings import HOST
from settings import PORT
from settings import DATABASE
from models import Base
from models import User
from models import Product
from models import Wishlist
from models import Comment


class Engine:
    def __init__(self):
        self.engine = create_engine(f'postgresql+psycopg2://{LOGIN}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}')
        self.Session = sessionmaker(bind=self.engine)

    def create_tables(self):
        Base.metadata.create_all(self.engine)

    def insert_user(self, user_data):
        with self.Session() as session:
            user = session.query(User).filter(User.email == user_data['email']).first()

            if not user:
                user = User(
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    email=user_data['email'],
                    city=user_data['city'],
                )
                session.add(user)
                session.commit()

            return user.id

    def insert_products(self, products_data):
        products_names = []

        with self.Session() as session:
            for product_data in products_data:
                product = session.query(Product).filter(Product.name == product_data['name']).first()

                if not product:
                    product = Product(
                        name=product_data['name'],
                        retail_price=product_data['retail_price'],
                        wholesale_price=product_data['wholesale_price'],
                        rating=product_data['rating'],
                        comments_count=product_data['comments_count'],
                        in_stores=product_data['in_stores'],
                    )
                    session.add(product)
                    session.commit()
                    products_names.append(product.name)

        return products_names

    def insert_comments(self, products_data, inserted_products):
        with self.Session() as session:
            for product in products_data:
                if product['name'] in inserted_products:
                    product_id = session.query(Product).filter(Product.name == product['name']).first().id

                    for comment_data in product['comments']:
                        comment = Comment(
                            author=comment_data['author'],
                            public_date=comment_data['public_date'],
                            rating=comment_data['rating'],
                            text=comment_data['text'],
                            product_id=product_id,
                        )
                        session.add(comment)
                        session.commit()

    def insert_wishlist(self, user_id, products):
        with self.Session() as session:
            for product in products:
                product_id = session.query(Product).filter(Product.name == product['name']).first().id

                if not session.query(Wishlist).filter(
                        (Wishlist.user_id == user_id) & (Wishlist.product_id == product_id)
                ).first():
                    wishlist = Wishlist(
                        user_id=user_id,
                        product_id=product_id,
                    )
                    session.add(wishlist)
                    session.commit()
