import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class UserStats(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'userstats'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    weight = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    height = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    birthday = sqlalchemy.Column(sqlalchemy.Date)

    user = orm.relation('User')
