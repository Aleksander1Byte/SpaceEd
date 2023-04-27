import sqlalchemy
import os
from sqlalchemy import orm

from .db_session import SqlAlchemyBase
from .tools.hash import generate_hash


class Task(SqlAlchemyBase):
    __tablename__ = 'tasks'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    question = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    picture_path = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    _hash = None

    def __hash__(self):
        if self._hash is None:
            self._hash = generate_hash()
        return self._hash

    def set_picture_path(self, path):
        from main import app
        if path.filename == '':
            self.picture_path = os.path.join(
                app.config[
                    'UPLOAD_FOLDER']
            ) + 'img/' + 'default_pic.png'
            return
