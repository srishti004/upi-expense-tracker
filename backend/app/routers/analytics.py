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

    # ── Recent 5 transactions ──
    recent_rows = db.execute(
        select(models.Transaction)
        .where(models.Transaction.user_id == current_user.id)
        .order_by(models.Transaction.txn_date.desc(), models.Transaction.created_at.desc())
        .limit(5)
    ).scalars().all()
 
    recent_transactions = [
        RecentTransaction(
            id=t.id,
            merchant=t.merchant,
            amount=t.amount,
            category=t.category,
            txn_type=t.txn_type,
            txn_date=t.txn_date,
        )
        for t in recent_rows
    ]


    

    # ── Budget alerts ──
    budget_rows = db.execute(
        select(models.Budget)
        .where(
            models.Budget.user_id == current_user.id,
            models.Budget.is_active == True,
        )
    ).scalars().all()


    alerts = []
    for budget in budget_rows:
        spent = next(
            (c.spent for c in spending_by_category if c.category == budget.category),
            Decimal("0")
        )
        usage = float(spent / budget.monthly_limit) if budget.monthly_limit > 0 else 0
        if usage >= float(budget.alert_threshold):
            alerts.append(BudgetAlert(
                category=budget.category,
                spent=spent,
                monthly_limit=budget.monthly_limit,
                usage_percent=round(usage * 100, 1),
                alert_threshold=float(budget.alert_threshold) * 100,
            ))
 
    return DashboardResponse(
        total_spent_this_month=this_month_total,
        total_spent_last_month=last_month_total,
        month_over_month_change=round(change, 1),
        spending_by_category=spending_by_category,
        recent_transactions=recent_transactions,
        budget_alerts=alerts,
    )

# ─── Spending by date range ─────────────────────────────────────────
 
@router.get("/spending", response_model=SpendingByDateRange)
def spending_by_date_range(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(get_current_user)],
    from_date: date = Query(..., description="Start date e.g. 2026-04-01"),
    to_date:   date = Query(..., description="End date e.g. 2026-04-30"),
):
    base_filter = and_(
        models.Transaction.user_id == current_user.id,
        models.Transaction.txn_date >= from_date,
        models.Transaction.txn_date <= to_date,
    )
 
    totals = db.execute(
        select(
            func.coalesce(
                func.sum(case((models.Transaction.txn_type == "debit", models.Transaction.amount), else_=Decimal("0"))),
                Decimal("0")
            ).label("total_spent"),
            func.coalesce(
                func.sum(case((models.Transaction.txn_type == "credit", models.Transaction.amount), else_=Decimal("0"))),
                Decimal("0")
            ).label("total_credited"),
        )
        .where(base_filter)
    ).first()
 
    category_rows = db.execute(
        select(
            models.Transaction.category,
            func.sum(models.Transaction.amount).label("spent"),
            func.count(models.Transaction.id).label("count"),
        )
        .where(base_filter, models.Transaction.txn_type == "debit")
        .group_by(models.Transaction.category)
        .order_by(func.sum(models.Transaction.amount).desc())
    ).all()
 
    merchant_rows = db.execute(
        select(
            models.Transaction.merchant,
            func.sum(models.Transaction.amount).label("spent"),
            func.count(models.Transaction.id).label("count"),
        )
        .where(
            base_filter,
            models.Transaction.txn_type == "debit",
            models.Transaction.merchant.isnot(None),
        )
        .group_by(models.Transaction.merchant)
        .order_by(func.sum(models.Transaction.amount).desc())
        .limit(10)
    ).all()
 
    return SpendingByDateRange(
        from_date=from_date,
        to_date=to_date,
        total_spent=totals.total_spent,
        total_credited=totals.total_credited,
        by_category=[
            CategorySpend(
                category=r.category,
                spent=r.spent,
                count=r.count,
                percentage=0.0,  # not needed for date range view
            )
            for r in category_rows
        ],
        by_merchant=[
            {"merchant": r.merchant, "spent": r.spent, "count": r.count}
            for r in merchant_rows
        ],
    )
 
 
# ─── Monthly trend ──────────────────────────────────────────────────
 
@router.get("/monthly-trend", response_model=list[MonthlyTrend])
def monthly_trend(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(get_current_user)],
    months: int = Query(default=6, ge=1, le=12),
):
    rows = db.execute(
        select(
            extract("year",  models.Transaction.txn_date).label("year"),
            extract("month", models.Transaction.txn_date).label("month"),
            func.coalesce(
                func.sum(case((models.Transaction.txn_type == "debit",  models.Transaction.amount), else_=Decimal("0"))),
                Decimal("0")
            ).label("spent"),
            func.coalesce(
                func.sum(case((models.Transaction.txn_type == "credit", models.Transaction.amount), else_=Decimal("0"))),
                Decimal("0")
            ).label("credited"),
        )
        .where(models.Transaction.user_id == current_user.id)
        .group_by(
            extract("year",  models.Transaction.txn_date),
            extract("month", models.Transaction.txn_date),
        )
        .order_by(
            extract("year",  models.Transaction.txn_date).desc(),
            extract("month", models.Transaction.txn_date).desc(),
        )
        .limit(months)
    ).all()
 
    return [
        MonthlyTrend(
            month=f"{int(row.year)}-{int(row.month):02d}",
            spent=row.spent,
            credited=row.credited,
        )
        for row in reversed(rows)
    ]


# ─── Category drill-down ────────────────────────────────────────────
 
@router.get("/category/{category_name}", response_model=CategoryDrilldown)
def category_drilldown(
    category_name: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(get_current_user)],
    month: Optional[int] = Query(default=None, ge=1, le=12),
    year:  Optional[int] = Query(default=None),
):
    now = datetime.now()
    month = month or now.month
    year  = year  or now.year
 
    txns = db.execute(
        select(models.Transaction)
        .where(
            models.Transaction.user_id  == current_user.id,
            models.Transaction.category == category_name,
            models.Transaction.txn_type == "debit",
            extract("month", models.Transaction.txn_date) == month,
            extract("year",  models.Transaction.txn_date) == year,
        )
        .order_by(models.Transaction.txn_date.desc())
    ).scalars().all()
 
    return CategoryDrilldown(
        category=category_name,
        month=f"{year}-{month:02d}",
        total_spent=sum(t.amount for t in txns),
        count=len(txns),
        transactions=[
            RecentTransaction(
                id=t.id,
                merchant=t.merchant,
                amount=t.amount,
                category=t.category,
                txn_type=t.txn_type,
                txn_date=t.txn_date,
            )
            for t in txns
        ],
    )


        
    

