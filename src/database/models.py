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

class Catalog(Base):
    __tablename__ = "catalogs"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    categories = relationship("ProductCategory", back_populates="catalog", cascade="all, delete-orphan")

    is_available = Column(Boolean, default=False, server_default='false', 
                         nullable=False, index=True)
    
    def update_availability(self):
        self.is_available = any(c.is_available for c in self.categories)
    
    def __repr__(self):
        return f"<Catalog(id={self.id}, name='{self.name}')>"


class ProductCategory(Base):
    __tablename__ = "product_categories"

    id = Column(Integer, primary_key=True)
    catalog_id = Column(Integer, ForeignKey("catalogs.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    image_url = Column(String(512))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    catalog = relationship("Catalog", back_populates="categories")
    products = relationship("Product", back_populates="category", cascade="all, delete-orphan")

    is_available = Column(Boolean, default=False, server_default='false', 
                          nullable=False, index=True)
    
    def update_availability(self):
        new_status = any(p.is_available for p in self.products)
        if self.is_available != new_status: 
            self.is_available = new_status
            if self.catalog:
                self.catalog.update_availability()

    def __repr__(self):
        return f"<ProductCategory(id={self.id}, name='{self.name}')>"


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey("product_categories.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Numeric(10, 3), nullable=False)
    unit = Column(String(50), nullable=False)  # 'шт', 'кг', 'л', 'м', 'упак', 'мл', 'г'
    price = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    category = relationship("ProductCategory", back_populates="products")

    is_available = Column(Boolean, default=True, server_default='true', 
                         nullable=False, index=True)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update_availability()

    def update_availability(self):
        new_status = self.quantity > 0
        if self.is_available != new_status:
            self.is_available = new_status
            if self.category:
                self.category.update_availability()

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', price={self.price})>"