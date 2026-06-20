from typing import Annotated, Optional
from datetime import datetime, date
from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, extract, and_, case
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.auth import get_current_user
from app.schemas import (
    CategorySpend,
    RecentTransaction,
    BudgetAlert,
    DashboardResponse,
    SpendingByDateRange,
    MonthlyTrend,
    CategoryDrilldown,
)

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

# ─── Dashboard ─────────────────────────────────────────────────────

@router.get("/dashboard",response_model="")
def get_dashboard(
    db:  Annotated[Session, Depends(get_db)],
    current_user :  Annotated[models.User, Depends(get_current_user)],
):
    now = datetime.now()
    now = datetime.now()
    this_month = now.month
    this_year  = now.year
    last_month = 12 if this_month == 1 else this_month - 1
    last_year  = this_year - 1 if this_month == 1 else this_year

    # # ── Total spent this month ──
    this_month_total=db.execute(
        select(func.coalesce(func.sum(models.Transaction.amount), Decimal("0")))
        .where(
            models.Transaction.user_id == current_user.id,
            models.Transaction.txn_type  == "debit",
            extract("month", models.Transaction.txn_date) == this_month,
            extract("year",  models.Transaction.txn_date) == this_year,
    )
    ).scalar()

     # ── Total spent last month ──
    last_month_total = db.execute(
        select(func.coalesce(func.sum(models.Transaction.amount), Decimal("0")))
        .where(
            models.Transaction.user_id == current_user.id,
            models.Transaction.txn_type == "debit",
            extract("month", models.Transaction.txn_date) == last_month,
            extract("year",  models.Transaction.txn_date) == last_year,
        )
    ).scalar()

        # ── Month-over-month change % ──
    if last_month_total and last_month_total > 0:      # safety net: not None, not 0 # numeric guard: can safely divide
        change = float(
            ((this_month_total - last_month_total) / last_month_total) * 100
        )
    else:
        change = 0.0

        # ── Spending by category this month ──
    category_rows = db.execute(
        select(
            models.Transaction.category,
            func.sum(models.Transaction.amount).label("spent"),
            func.count(models.Transaction.id).label("count"),
        )
        .where(
            models.Transaction.user_id == current_user.id,
            models.Transaction.txn_type == "debit",
            extract("month", models.Transaction.txn_date) == this_month,
            extract("year",  models.Transaction.txn_date) == this_year,
        )
        .group_by(models.Transaction.category)
        .order_by(func.sum(models.Transaction.amount).desc())
    ).all()

    spending_by_category = [
        CategorySpend(
            category=row.category,
            spent=row.spent,
            count=row.count,
            percentage=round(
                float(row.spent / this_month_total * 100) if this_month_total > 0 else 0,
                1
            ),
        )
        for row in category_rows
    ]
    recent_rows = db.execute(
        select(models.Transaction)
        .where(models.Transaction.user_id == current_user.id)
        .order_by(models.Transaction.txn_date.desc(), models.Transaction.created_at.desc())
        .limit(5)
    ).scalars().all()



        
    

