import datetime
from typing import List

from aiogram import types, Bot
from gino import Gino
from gino.schema import GinoSchemaVisitor
from sqlalchemy import (Column, Integer, BigInteger, String,
                        Sequence, TIMESTAMP, Boolean, JSON, DATETIME)
from sqlalchemy import sql, and_, ForeignKey

from config import POSTGRES_URI

db = Gino()


# Документация
# http://gino.fantix.pro/en/latest/tutorials/tutorial.html

class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    user_id = Column(BigInteger)
    full_name = Column(String(100))
    username = Column(String(50))
    data_reg = Column(TIMESTAMP)
    query: sql.Select

    def __repr__(self):
        return "<User(id='{}', fullname='{}', username='{}')>".format(
            self.id, self.full_name, self.username)


class Item(db.Model):
    __tablename__ = 'items'
    query: sql.Select

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    name = Column(String(50))
    # photo = Column(String(250))
    # price = Column(Integer)  # Цена в копейках (потом делим на 100)
    desc = Column(String(10000))
    contactInst = Column(String(250))
    username = Column(String(150))
    review_id = Column(Integer, unique=True)
    payment = Column(Boolean, default=False)

    def __repr__(self):
        return "<Item(id='{}', name='{}', desc='{}', contact='{}',username='{}', review_id='{}'".format(
            self.id, self.name, self.desc, self.contact, self.username, self.review_id)


class Vacancy(db.Model):
    __tablename__ = 'vacanvies'
    query: sql.Select

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    name = Column(String(50))
    # photo = Column(String(250))
    # price = Column(Integer)  # Цена в копейках (потом делим на 100)
    desc = Column(String(10000))
    contactInst = Column(String(250))
    username = Column(String(150))
    # review_id = Column(Integer, unique=True)
    payment = Column(Boolean, default=False)

    def __repr__(self):
        return "<Vacancy(id='{}', name='{}', desc='{}', contactInst='{}',username='{}'".format(
            self.id, self.name, self.desc, self.contactInst, self.username)


class Purchase(db.Model):
    __tablename__ = 'purchases'
    query: sql.Select

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    buyer = Column(BigInteger)
    item_id = Column(Integer)
    # amount = Column(Integer)  # Цена в копейках (потом делим на 100)
    # quantity = Column(Integer)
    purchase_time = Column(TIMESTAMP)
    # shipping_address = Column(JSON)
    # phone_number = Column(String(50))
    # email = Column(String(200))
    # receiver = Column(String(100))
    successful = Column(Boolean, default=False)


class Reviews(db.Model):
    __tablename__ = 'reviews'
    query: sql.Select

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    review_id = Column(Integer, ForeignKey('items.review_id'))
    review_text = Column(String(5000))
    from_us = Column(String(100))

    def __repr__(self):
        return "<Review(id='{}', review_id='{}', review_text='{}', from_us='{}')>".format(
            self.id, self.review_id, self.review_text, self.from_us)


class DBCommands:

    async def get_user(self, user_id):
        user = await User.query.where(User.user_id == user_id).gino.first()
        return user

    async def add_new_user(self):
        user = types.User.get_current()
        old_user = await self.get_user(user.id)
        if old_user:
            return old_user
        new_user = User()
        new_user.user_id = user.id
        new_user.username = user.username
        new_user.full_name = user.full_name
        new_user.data_reg = datetime.datetime.now()
        await new_user.create()
        return new_user

    async def count_users(self) -> int:
        total = await db.func.count(User.id).gino.scalar()
        return total

    async def show_vacancies(self):
        vacancies = await Vacancy.query.gino.all()
        return vacancies

    async def show_producers(self):
        producers = await Item.query.where(Item.name == 'Продюсер').gino.all()
        return producers

    async def show_experts(self):
        experts = await Item.query.where(Item.name == 'Эксперт').gino.all()
        return experts

    async def targ(self):
        targ = await Item.query.where(Item.name == 'Таргетолог').gino.all()
        return targ

    async def storiz(self):
        storiz = await Item.query.where(Item.name == 'Сторизмейкер').gino.all()
        return storiz

    async def smm(self):
        smm = await Item.query.where(Item.name == 'SMM-специалист').gino.all()
        return smm

    async def metod(self):
        metod = await Item.query.where(Item.name == 'Методолог').gino.all()
        return metod

    async def tech(self):
        tech = await Item.query.where(Item.name == 'Технический специалист').gino.all()
        return tech

    async def dis(self):
        dis = await Item.query.where(Item.name == 'Дизайнер').gino.all()
        return dis

    async def copy(self):
        copy = await Item.query.where(Item.name == 'Копирайтер').gino.all()
        return copy

    async def scen(self):
        scen = await Item.query.where(Item.name == 'Сценарист').gino.all()
        return scen

    async def mont(self):
        mont = await Item.query.where(Item.name == 'Монтажер видео').gino.all()
        return mont

    async def ass(self):
        ass = await Item.query.where(Item.name == 'Ассистент').gino.all()
        return ass

    async def vis(self):
        vis = await Item.query.where(Item.name == 'Специалист по визуалу').gino.all()
        return vis

    async def show_reviews(self, review_id):
        reviews = await Reviews.query.where(Reviews.review_id == review_id).gino.all()
        return reviews


async def create_db():
    await db.set_bind(POSTGRES_URI)

    # Create tables
    db.gino: GinoSchemaVisitor
    # await db.gino.drop_all()
    # await db.gino.create_all()
