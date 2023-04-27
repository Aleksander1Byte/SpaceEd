import sqlalchemy
import os
from sqlalchemy import orm
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase
from .tools.hash import generate_hash


class Task(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'tasks'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    question = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    answer = sqlalchemy.Column(sqlalchemy.String, nullable=True, default=None)
    given_points = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, default=0)
    picture_path = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    users = orm.relation('Points', back_populates='tsk')
    _hash = None

    def __hash__(self):
        if self._hash is None:
            self._hash = generate_hash()
        return self._hash

    def set_picture_path(self, path):
        from main import app
        if path.filename == '':
            return
        self.picture_path = os.path.join(
            app.config[
                'UPLOAD_FOLDER']
        ) + 'img/' + self.__hash__() + path.filename[-4:]
        path.save(self.picture_path)
