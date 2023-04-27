import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class ManualAnswer(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'manual_answer'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    task_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("tasks.id"))
    answer = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    user = orm.relation('User')
    tsk = orm.relation('Task')
