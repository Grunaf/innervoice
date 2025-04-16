from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, func
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    generated_username = Column(String(50), unique=True)
    posts_count = Column(Integer, default=0)

    posts = relationship("Post", back_populates="author")


class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)
    message_id_in_channel = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    author_id = Column(Integer, ForeignKey("users.id"))

    author = relationship("User", back_populates="posts")
