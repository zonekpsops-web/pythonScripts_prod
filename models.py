# Create proper indexing, ENUM constraints, and foreign key relationships.

import uuid
from datetime import datetime, date
from typing import Any, Dict
from sqlalchemy import String, Numeric, Boolean, Date, DateTime, ForeignKey, Index, Enum as SQLEnum, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base
import enum

class ItemCondition(str, enum.Enum):
    NEW = "new"
    RESALE = "resale"

class ItemCategory(str, enum.Enum):
    BOOK = "book"
    TOY = "toy"
    PHONE = "phone"
    COSMETIC = "cosmetic"

class PaymentMode(str, enum.Enum):
    CREDIT = "credit"
    CASH = "cash"
    CHEQUE = "cheque"
    LOAN = "loan"

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    contact_no: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    company_name: Mapped[str] = mapped_column(String(100), nullable=True)
    department: Mapped[str] = mapped_column(String(100), nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    pincode: Mapped[str] = mapped_column(String(10), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    payments = relationship("Payment", back_populates="user", cascade="all, delete-orphan")

class Item(Base):
    __tablename__ = "items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    item_name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[ItemCategory] = mapped_column(SQLEnum(ItemCategory), nullable=False, index=True)
    price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    loan_available: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    condition: Mapped[ItemCondition] = mapped_column(SQLEnum(ItemCondition), nullable=False, default=ItemCondition.NEW)
    
    # JSON field storing dynamic category-specific features (e.g. RAM, author, age_group)
    specifications: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    payments = relationship("Payment", back_populates="item", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_items_category_price", "category", "price"),
    )

class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    item_id: Mapped[str] = mapped_column(String(36), ForeignKey("items.id"), nullable=False)
    mode_of_payment: Mapped[PaymentMode] = mapped_column(SQLEnum(PaymentMode), nullable=False)
    down_payment: Mapped[float] = mapped_column(Numeric(12, 2), default=0.00)
    loan_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0.00)
    total_paid: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="payments")
    item = relationship("Item", back_populates="payments")

    __table_args__ = (
        Index("ix_payments_user_created", "user_id", "created_at"),
    )