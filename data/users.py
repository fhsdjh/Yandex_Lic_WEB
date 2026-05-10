import datetime
import sqlalchemy as sa
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = "users"
    serialize_only = ("id", "name", "email", "created")

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, nullable=False)
    email = sa.Column(sa.String, index=True, unique=True, nullable=False)
    pwd_hash = sa.Column(sa.String, nullable=False)
    created = sa.Column(sa.DateTime, default=datetime.datetime.now)

    posts = orm.relationship("Post", back_populates="author")

    def set_pwd(self, pwd):
        self.pwd_hash = generate_password_hash(pwd, method="pbkdf2:sha256")

    def check_pwd(self, pwd):
        return check_password_hash(self.pwd_hash, pwd)
