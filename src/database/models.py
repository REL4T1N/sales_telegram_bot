from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, String, Boolean, ForeignKey, Numeric, Text, DateTime
from sqlalchemy.orm import relationship
from database.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, unique=True, nullable=False)  # Изменили на BigInteger для Telegram ID
    username = Column(String(100))
    first_name = Column(String(100))
    last_name = Column(String(100))
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"
