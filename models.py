from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Numeric
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import MetaData
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base

from settings import SCHEMA


Base = declarative_base(metadata=MetaData(schema=SCHEMA))


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer(), primary_key=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(100), unique=True, nullable=False)
    city = Column(String(100))
    wishlist = relationship('Wishlist', back_populates='user', cascade='all, delete-orphan')


class Product(Base):
    __tablename__ = 'product'

    id = Column(Integer(), primary_key=True)
    name = Column(String(500), unique=True, nullable=False)
    retail_price = Column(Numeric(10, 2), nullable=False)
    wholesale_price = Column(Numeric(10, 2), nullable=False)
    rating = Column(Numeric(2, 1), nullable=False)
    comments_count = Column(Integer(), nullable=False)
    in_stores = Column(Integer(), nullable=False)
    comments = relationship('Comment', back_populates='product', cascade='all, delete-orphan')
    wishlist = relationship('Wishlist', back_populates='product', cascade='all, delete-orphan')


class Wishlist(Base):
    __tablename__ = 'wishlist'

    id = Column(Integer(), primary_key=True)
    user_id = Column(Integer(), ForeignKey('user.id', ondelete='CASCADE'))
    product_id = Column(Integer(), ForeignKey('product.id', ondelete='CASCADE'))
    user = relationship('User', back_populates='wishlist')
    product = relationship('Product', back_populates='wishlist')


class Comment(Base):
    __tablename__ = 'comment'

    id = Column(Integer(), primary_key=True)
    author = Column(String(200), nullable=False)
    public_date = Column(DateTime(), nullable=False)
    rating = Column(Integer(), nullable=False)
    text = Column(Text())
    product_id = Column(Integer(), ForeignKey('product.id', ondelete='CASCADE'))
    product = relationship('Product', back_populates='comments')
