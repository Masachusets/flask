import pydantic
from typing import Optional, Type
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, create_engine, func
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

from flask import Flask
from flask_bcrypt import Bcrypt

app = Flask('app')  # create app
DSN = 'postgresql://app:1111@127.0.0.1:5433/flask_db'
engine = create_engine(DSN)
Base = declarative_base()
Session = sessionmaker(bind=engine)
bcrypt = Bcrypt(app)
Base.metadata.create_all(engine)  # makemigrations


class UserModel(Base):

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False, unique=True)
    password_hash = Column(String, nullable=False)
    email = Column(String, nullable=False)


class AdModel(Base):

    __tablename__ = 'ads'

    id = Column(Integer, primary_key=True)
    title = Column(String(32), nullable=False, unique=True)
    text = Column(String)
    creation_time = Column(DateTime, server_default=func.now())
    owner = relationship(UserModel, lazy="owner")


class CreateUserSchema(pydantic.BaseModel):
    name: str
    password: str

    @pydantic.validator('name')
    def check_name(cls, value: str):
        if len(value) > 32:
            raise ValueError('Name must be less then 32 chars')

        return value

    @pydantic.validator('password')
    def check_password(cls, value: str):
        value = value.encode()
        value = bcrypt.generate_password_hash(value)
        value = value.decode()
        return value


class PatchUserSchema(pydantic.BaseModel):
    name: Optional[str]
    password: Optional[str]

    @pydantic.validator('name')
    def check_name(cls, value: str):
        if len(value) > 32:
            raise ValueError('Name must be less then 32 chars')

        return value

    @pydantic.validator('password')
    def check_password(cls, value: str):
        # if not re.search(password_regex, value):
        #     raise ValueError('the wrong password')
        value = value.encode()
        value = bcrypt.generate_password_hash(value)
        value = value.decode()
        return value


class CreateAdSchema(pydantic.BaseModel):
    title: str
    text: str
    owner: Type[UserModel]

    @pydantic.validator('title')
    def check_title(cls, value: str):
        if len(value) > 32:
            raise ValueError('Title must be less then 32 chars')

        return value

    @pydantic.validator('owner')
    def check_owner(cls, value: Type[UserModel]):
        value = value.encode()
        value = bcrypt.generate_password_hash(value)
        value = value.decode()
        return value


class PatcAdSchema(pydantic.BaseModel):
    title: Optional[str]
    owner: Type[UserModel]

    @pydantic.validator('name')
    def check_title(cls, value: str):
        if len(value) > 32:
            raise ValueError('Name must be less then 32 chars')

        return value

    @pydantic.validator('password')
    def check_owner(cls, value: str):
        value = value.encode()
        value = bcrypt.generate_password_hash(value)
        value = value.decode()
        return value