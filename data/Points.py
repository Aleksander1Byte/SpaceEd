import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Points(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'points'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    task_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("tasks.id"))
    amount = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, default=0)

    user = orm.relation('User')
    tsk = orm.relation('Task')
