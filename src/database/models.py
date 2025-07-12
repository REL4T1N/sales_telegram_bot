from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Boolean, Numeric, ForeignKey,
    UniqueConstraint, TIMESTAMP, BigInteger, DateTime, Text, func
)
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


class Catalog(Base):
    __tablename__ = "catalogs"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    categories = relationship("Category", back_populates="catalog")


class Category(Base):
    __tablename__ = "categories"
    __table_args__ = (UniqueConstraint("catalog_id", "name"),)

    id = Column(Integer, primary_key=True)
    catalog_id = Column(Integer, ForeignKey("catalogs.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)

    catalog = relationship("Catalog", back_populates="categories")
    products = relationship("Product", back_populates="category")


class Unit(Base):
    __tablename__ = "units"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    products = relationship("Product", back_populates="unit")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=False)
    available = Column(Boolean, nullable=False, default=True, server_default="true")
    quantity = Column(Numeric(10, 2), nullable=False, default=0)
    size = Column(Numeric(10, 2), nullable=False, default=1)  # Новое поле с дефолтом
    price = Column(Numeric(10, 2), nullable=False)
    image_id = Column(BigInteger, ForeignKey("images.id", ondelete="SET NULL"), nullable=True)  # Используем BigInteger
    description = Column(Text, nullable=True)  # Поле для описания
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    category = relationship("Category", back_populates="products")
    unit = relationship("Unit", back_populates="products")
