from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String

Base = declarative_base()


class Account(Base):

    __tablename__ = 'account'

    id = Column(Integer, primary_key=True, autoincrement=True)
    auth_id = Column(String(40))
    username = Column(String(30))


class PhoneNumber(Base):

    __tablename__ = 'phone_number'

    id = Column(Integer, primary_key=True, autoincrement=True)
    number = Column(String(40))
    account_id = Column(Integer, ForeignKey("account.id"))
