import uuid
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class UserModel(Base):

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False, unique=True)
    password = Column(String, nullable=False)
    email = Column(String, nullable=True)
    ads = relationship("AdModel", backref="owner", lazy="joined")


class AdModel(Base):

    __tablename__ = 'ads'

    id = Column(Integer, primary_key=True)
    title = Column(String(32), nullable=False, unique=True)
    text = Column(String)
    creation_time = Column(DateTime, server_default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)


class Token(Base):
    __tablename__ = "tokens"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    creation_time = Column(DateTime, server_default=func.now())
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    user = relationship(UserModel, lazy="joined")
