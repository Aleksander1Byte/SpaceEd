import os

import sqlalchemy
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase
from .tools.hash import generate_hash


class Theory(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'theories'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    video_path = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    picture_path = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    allowed_groups = sqlalchemy.Column(sqlalchemy.String, default='', nullable=False)
    _hash = None

    def set_allowed_groups(self, groups):
        for g in groups:
            self.allowed_groups += f'{g};'

    def __hash__(self):
        if self._hash is None:
            self._hash = generate_hash()
        return self._hash

    def set_video_path(self, path):
        from main import app

        if path.filename == '':
            self.video_path = None
            return
        self.video_path = (
            os.path.join(app.config['UPLOAD_FOLDER'])
            + 'vid/'
            + self.__hash__()
            + path.filename[-4:]
        )
        path.save(self.video_path)

    def set_picture_path(self, path):
        from main import app

        if path.filename == '':
            return

        self.picture_path = (
            os.path.join(app.config['UPLOAD_FOLDER'])
            + 'img/'
            + self.__hash__()
            + path.filename[-4:]
        )
        path.save(self.picture_path)

    def set_paths(self, video_path, picture_path):
        self.set_video_path(video_path)
        self.set_picture_path(picture_path)
