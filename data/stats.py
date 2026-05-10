import sqlalchemy as sa

from .db_session import SqlAlchemyBase


class Stat(SqlAlchemyBase):
    __tablename__ = "stats"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    alice_uid = sa.Column(sa.String, index=True, unique=True, nullable=False)
    name = sa.Column(sa.String, nullable=True)
    score = sa.Column(sa.Integer, default=0)
    rounds = sa.Column(sa.Integer, default=0)
