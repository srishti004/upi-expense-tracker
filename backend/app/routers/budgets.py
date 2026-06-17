from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func, extract
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import datetime

from app.database import get_db
from app import models
from app.schemas import BudgetCreate, BudgetUpdate, BudgetResponse, BudgetSummaryResponse
from app.auth import get_current_user

router = APIRouter(prefix="/api/budgets", tags=["budgets"])


@router.get("", response_model=list[BudgetResponse])
def list_budgets(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(get_current_user)],
):
    """GET /api/budgets — list all budgets for current user."""
    budgets = db.execute(
        select(models.Budget).where(
            models.Budget.user_id == current_user.id
        )
    ).scalars().all()
    return budgets


@router.post("", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
def create_or_update_budget(
    body: BudgetCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(get_current_user)],
):
    """
    POST /api/budgets — create or update (upsert) a budget.
    UNIQUE(user_id, category) means one budget per category per user.
    If one already exists for this category, update it instead.
    """
    existing = db.execute(
        select(models.Budget).where(
            models.Budget.user_id == current_user.id,
            models.Budget.category == body.category,
        )
    ).scalars().first()

    if existing:
        # update existing
        existing.monthly_limit = body.monthly_limit
        existing.alert_threshold = body.alert_threshold
        existing.is_active = True
        db.commit()
        db.refresh(existing)
        return existing

    # create new
    budget = models.Budget(
        user_id=current_user.id,
        category=body.category,
        monthly_limit=body.monthly_limit,
        alert_threshold=body.alert_threshold,
    )
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return budget


@router.put("/{budget_id}", response_model=BudgetResponse)
def update_budget(
    budget_id: UUID,
    body: BudgetUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(get_current_user)],
):
    """PUT /api/budgets/{id} — update limit, threshold, or active status."""
    budget = db.execute(
        select(models.Budget).where(
            models.Budget.id == budget_id,
            models.Budget.user_id == current_user.id,  # ← own data only
        )
    ).scalars().first()

    if budget is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")

    if body.monthly_limit is not None:
        budget.monthly_limit = body.monthly_limit
    if body.alert_threshold is not None:
        budget.alert_threshold = body.alert_threshold
    if body.is_active is not None:
        budget.is_active = body.is_active

    db.commit()
    db.refresh(budget)
    return budget


@router.get("/summary", response_model=list[BudgetSummaryResponse])
def budget_summary(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(get_current_user)],
    month: Optional[int] = None,
    year: Optional[int] = None,
):
    """
    GET /api/budgets/summary
    Joins budgets + transactions to show spent vs limit per category.
    Defaults to current month/year if not specified.
    """
    now = datetime.now()
    month = month or now.month
    year = year or now.year

    # Sum spending per category for this user/month/year
    spent_subq = (
        select(
            models.Transaction.category,
            func.sum(models.Transaction.amount).label("spent"),
        )
        .where(
            models.Transaction.user_id == current_user.id,
            models.Transaction.txn_type == "debit",
            extract("month", models.Transaction.txn_date) == month,
            extract("year", models.Transaction.txn_date) == year,
        )
        .group_by(models.Transaction.category)
        .subquery()
    )

    # Join budgets with the spending subquery
    rows = db.execute(
        select(
            models.Budget.category,
            models.Budget.monthly_limit,
            models.Budget.alert_threshold,
            func.coalesce(spent_subq.c.spent, Decimal("0")).label("spent"),
        )
        .join(spent_subq, models.Budget.category == spent_subq.c.category, isouter=True)
        .where(
            models.Budget.user_id == current_user.id,
            models.Budget.is_active == True,
        )
    ).all()

    return [
        BudgetSummaryResponse(
            category=row.category,
            monthly_limit=row.monthly_limit,
            alert_threshold=row.alert_threshold,
            spent=row.spent,
        )
        for row in rows
    ]