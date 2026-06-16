from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import uuid
from datetime import date, datetime, UTC
from sqlalchemy.dialects.postgresql import UUID
from typing import List, Optional
from sqlalchemy import String, ForeignKey, Boolean, Numeric, Date, Text, UniqueConstraint, DateTime
from decimal import Decimal

def utcnow():
    return datetime.now(UTC)

class Base(DeclarativeBase):
    pass

# ─── users table ──────────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    email: Mapped[Optional[str]] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
        index=True
    )

    fullname: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=True
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
        nullable=False
    )

    transactions = relationship("Transaction", back_populates="user", cascade="all,delete-orphan")
    budgets = relationship("Budget", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email}>"
    

# ─── transactions table ───────────────────────────────────────────
class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    txn_type: Mapped[str] = mapped_column(
        String(10),
        nullable=False
    )

    merchant: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )

    account_masked: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True
    )

    txn_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True
    )

    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="Uncategorised",
        index=True
    )

    is_manually_categorized: Mapped[bool] = mapped_column(
    Boolean,
    nullable=False,
    default=False
)
    
    raw_sms: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        nullable=False
    )

    user = relationship("User", back_populates="transactions")

    def __repr__(self):
        return f"<Transaction {self.merchant} ₹{self.amount}>"
    

# ─── budgets table ────────────────────────────────────────────────
class Budget(Base):
    __tablename__ = "budgets"

    __table_args__ = (
        UniqueConstraint("user_id", "category", name="uq_budget_user_category"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )

    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )

    monthly_limit: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    alert_threshold: Mapped[Decimal] = mapped_column(
        Numeric(4, 2),
        nullable=False,
        default=Decimal("0.80")
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        nullable=False
    )

    user = relationship("User", back_populates="budgets")

    def __repr__(self):
        return f"<Budget {self.category} ₹{self.monthly_limit}/mo>"
