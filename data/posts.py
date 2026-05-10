import datetime
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Post(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "posts"
    serialize_rules = ("-author.posts", "-author.pwd_hash")

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    title = sa.Column(sa.String, nullable=False)
    text = sa.Column(sa.String, nullable=False)
    image = sa.Column(sa.String, nullable=True)
    created = sa.Column(sa.DateTime, default=datetime.datetime.now)

    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"))
    author = orm.relationship("User", back_populates="posts")
