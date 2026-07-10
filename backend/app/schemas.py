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
    raw_sms: str 


class TransactionBase(BaseModel):
    amount: Decimal
    raw_sms: str 


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

# ─── Analytics schemas ────────────────────────────────────────────
 
class CategorySpend(BaseModel):
    category:   str
    spent:      Decimal
    count:      int
    percentage: float   # e.g. 24.8 means 24.8% of total spending
 
 
class RecentTransaction(BaseModel):
    id:       uuid.UUID
    merchant: Optional[str] = None
    amount:   Decimal
    category: str
    txn_type: str
    txn_date: date
 
 
class BudgetAlert(BaseModel):
    category:        str
    spent:           Decimal
    monthly_limit:   Decimal
    usage_percent:   float   # e.g. 84.0 means 84% used
    alert_threshold: float   # e.g. 80.0 means alert fires at 80%


class DashboardResponse(BaseModel):
    total_spent_this_month:  Decimal
    total_spent_last_month:  Decimal
    month_over_month_change: float
    spending_by_category:    list[CategorySpend]
    recent_transactions:     list[RecentTransaction]
    budget_alerts:           list[BudgetAlert]
 
 
class SpendingByDateRange(BaseModel):
    from_date:      date
    to_date:        date
    total_spent:    Decimal
    total_credited: Decimal
    by_category:    list[CategorySpend]
    by_merchant:    list[dict]   # merchant name not typed — varies too much
 
 
class MonthlyTrend(BaseModel):
    month:    str       # "2026-04"
    spent:    Decimal
    credited: Decimal
 
 
class CategoryDrilldown(BaseModel):
    category:     str
    month:        str
    total_spent:  Decimal
    count:        int
    transactions: list[RecentTransaction]   # reuse — same shape needed here


class BulkSMSRequest(BaseModel):
    messages: list[str] = Field(min_length=1, max_length=50)
    # list of raw SMS strings, max 50 at once

class BulkSMSResult(BaseModel):
    raw_sms:  str
    success:  bool
    transaction: Optional[TransactionResponse] = None
    error:    Optional[str] = None   # why it failed if success=False

class BulkSMSResponse(BaseModel):
    total:    int
    saved:    int
    skipped:  int
    results:  list[BulkSMSResult]
 