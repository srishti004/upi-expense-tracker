from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, extract, func
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.schemas import TransactionResponse, TransactionCategoryUpdate
from app.auth import get_current_user

router = APIRouter(prefix="/api/transactions", tags=["transactions"])


@router.get("", response_model=dict)
def list_transactions(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(get_current_user)],
    month: Optional[int] = Query(default=None, ge=1, le=12),
    year: Optional[int] = Query(default=None, ge=2000),
    category: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    base_query = select(models.Transaction).where(
        models.Transaction.user_id == current_user.id
    )

    if month:
        base_query = base_query.where(extract("month", models.Transaction.txn_date) == month)
    if year:
        base_query = base_query.where(extract("year", models.Transaction.txn_date) == year)
    if category:
        base_query = base_query.where(models.Transaction.category == category)

    # get total count before pagination
    total = db.execute(select(func.count()).select_from(base_query.subquery())).scalar()

    # apply pagination
    transactions = db.execute(
        base_query.order_by(models.Transaction.txn_date.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).scalars().all()

    return {
        "transactions": [TransactionResponse.model_validate(t) for t in transactions],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.put("/{transaction_id}/category", response_model=TransactionResponse)
def update_category(
    transaction_id: UUID,
    body: TransactionCategoryUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(get_current_user)],
):
    """
    PUT /api/transactions/{id}/category
    Manually re-label a transaction's category.
    Only the owner can update their own transaction.
    """
    txn = db.execute(
        select(models.Transaction).where(
            models.Transaction.id == transaction_id,
            models.Transaction.user_id == current_user.id,  # ← security: own data only
        )
    ).scalars().first()

    if txn is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )

    txn.category = body.category
    txn.is_manually_categorized = True  # mark as human-overridden
    db.commit()
    db.refresh(txn)
    return txn


#*********************BUG********************************#
# What PUT /api/transactions/{id}/category actually does
# Transaction row in DB:
# {
#   id:                    "69b26414...",
#   merchant:              "PETROL PUMP",
#   category:              "Uncategorized",   ← wrong
#   is_manually_categorized: False
# }

# User sends:
# PUT /api/transactions/69b26414.../category
# Body: {"category": "Fuel"}

# Transaction row after:
# {
#   id:                    "69b26414...",
#   merchant:              "PETROL PUMP",
#   category:              "Fuel",            ← fixed, only this row
#   is_manually_categorized: True             ← flagged as human-corrected
# }
# That's it. One row changed. categorizer.py is untouched.

# The real problem this creates
# Next time the user pastes another "PETROL PUMP" SMS:
# New SMS: "Rs.300 debited for UPI txn to PETROL PUMP on 10-Jun"
# → categorizer.py still doesn't know PETROL PUMP
# → new transaction saved as "Uncategorized" again
# → user has to manually fix it again
# → and again next month
# → and again...
# This is genuinely bad UX. The user fixed it once — they shouldn't have to fix it every time.