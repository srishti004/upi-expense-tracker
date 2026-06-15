from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Literal
import uuid
from pydantic import BaseModel, ConfigDict, Field, EmailStr

CategoryType = Literal[
    "Food", "Groceries", "Travel", "Shopping",
    "Entertainment", "Utilities", "Rent",
    "Health", "Fuel", "Uncategorized"
]


class UserBase(BaseModel):
    email: EmailStr
    fullname: Optional[str] = None  # often optional at signup


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    fullname: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserPrivate(UserPublic):
    model_config = ConfigDict(from_attributes=True)

    email: EmailStr


class UserUpdate(BaseModel):
    fullname: str | None = Field(default=None, min_length=1, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=120)


class Token(BaseModel):
    access_token: str
    token_type: str


class SMSParseRequest(BaseModel):
    raw_sms: str = Field(min_length=1, max_length=300)


class TransactionBase(BaseModel):
    amount: Decimal
    raw_sms: str = Field(min_length=1, max_length=100)


class TransactionCreate(TransactionBase):
    pass


class TransactionResponse(TransactionBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    amount: Decimal
    txn_type: str
    merchant: Optional[str] = None       # can be None (ATM, P2P)
    account_masked: Optional[str] = None
    txn_date: date
    category: str
    is_manually_categorized: bool
    created_at: datetime
    updated_at: datetime


class TransactionCategoryUpdate(BaseModel):
    category: CategoryType


class BudgetCreate(BaseModel):
    category: CategoryType
    monthly_limit: Decimal = Field(gt=0)
    alert_threshold: Decimal = Field(default=Decimal("0.80"), gt=0, le=1)


class BudgetUpdate(BaseModel):
    monthly_limit: Optional[Decimal] = Field(default=None, gt=0)
    alert_threshold: Optional[Decimal] = Field(default=None, gt=0, le=1)
    is_active: Optional[bool] = None


class BudgetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    category: str
    monthly_limit: Decimal
    alert_threshold: Decimal
    is_active: bool


class BudgetSummaryResponse(BaseModel):
    category: str
    monthly_limit: Decimal
    alert_threshold: Decimal
    spent: Decimal