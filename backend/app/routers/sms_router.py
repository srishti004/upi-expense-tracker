from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from app.database import get_db
from app.schemas import SMSParseRequest, TransactionResponse,BulkSMSRequest,BulkSMSResult,BulkSMSResponse
import app.models
from app.parser import parse_upi_sms
from app.categorizer import get_category
from  typing import  Annotated
from  sqlalchemy.orm  import Session
from app.auth import get_current_user


router = APIRouter(prefix="/api/sms", tags=["sms"])


def parse_txn_date(raw_date: str | None) -> date:
    """Convert '04-Jun' or '04-Jun-24' from SMS into a date object."""
    if not raw_date:
        return datetime.today().date()
    try:
        # with year: "04-Jun-24"
        return datetime.strptime(raw_date, "%d-%b-%y").date()
    except ValueError:
        try:
            # no year: "04-Jun" — assume current year
            parsed = datetime.strptime(raw_date, "%d-%b")
            return parsed.replace(year=datetime.today().year).date()
        except ValueError:
            return datetime.today().date()  # fallback

@router.post("/parse", response_model=TransactionResponse)
def parse_sms(
    body: SMSParseRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[app.models.User, Depends(get_current_user)],
):
    # duplicate check — same user, same raw SMS
    existing = db.execute(
        select(app.models.Transaction).where(
            app.models.Transaction.user_id == current_user.id,
            app.models.Transaction.raw_sms == body.raw_sms,
        )
    ).scalars().first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="This SMS has already been parsed and saved",
        )

    result = parse_upi_sms(body.raw_sms)

    if not result.is_upi:
        raise HTTPException(
            status_code=400,
            detail="This doesn't look like a UPI transaction SMS",
        )

    if result.amount is None:
        raise HTTPException(
            status_code=422,
            detail="Could not extract amount from this SMS",
        )

    category = get_category(result.merchant)

    txn = app.models.Transaction(
        user_id=current_user.id,
        amount=result.amount,
        txn_type=result.txn_type,
        merchant=result.merchant,
        account_masked=result.account,
        txn_date=parse_txn_date(result.txn_date),
        category=category,
        raw_sms=body.raw_sms,
    )

    db.add(txn)
    db.commit()
    db.refresh(txn)
    return txn

@router.post("/parse/bulk", response_model=BulkSMSResponse)
def parse_bulk_sms(
    body: BulkSMSRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[app.models.User, Depends(get_current_user)],
):
    results = []
    saved = 0
    skipped = 0

    for raw_sms in body.messages:
        try:
            existing = db.execute(
                select(app.models.Transaction).where(
                    app.models.Transaction.user_id == current_user.id,
                    app.models.Transaction.raw_sms == raw_sms,
                )
            ).scalars().first()

            if existing:
                skipped += 1
                results.append(BulkSMSResult(
                    raw_sms=raw_sms,
                    success=False,
                    error="Already saved",
                ))
                continue

            result = parse_upi_sms(raw_sms)

            if not result.is_upi or result.amount is None:
                skipped += 1
                results.append(BulkSMSResult(
                    raw_sms=raw_sms,
                    success=False,
                    error="Not a valid UPI transaction SMS",
                ))
                continue

            category = get_category(result.merchant)
            
            txn = app.models.Transaction(
                user_id=current_user.id,
                amount=result.amount,
                txn_type=result.txn_type,
                merchant=result.merchant,
                account_masked=result.account,
                txn_date=parse_txn_date(result.txn_date),
                category=category,
                raw_sms=raw_sms,
            )
            db.add(txn)
            db.flush()   # assigns UUID without committing yet
            db.refresh(txn)

            saved += 1
            results.append(BulkSMSResult(
                raw_sms=raw_sms,
                success=True,
                transaction=TransactionResponse.model_validate(txn),
            ))

        except Exception as e:
            skipped += 1
            results.append(BulkSMSResult(
                raw_sms=raw_sms,
                success=False,
                error=str(e),
            ))

    db.commit()   # one commit for all successful inserts

    return BulkSMSResponse(
        total=len(body.messages),
        saved=saved,
        skipped=skipped,
        results=results,
    )

# db.add(txn)    →  tells SQLAlchemy "I want to insert this row"
#                   nothing written to DB yet — it's staged in memory

# db.commit()    →  executes INSERT INTO transactions (...) VALUES (...)
#                   row now exists in PostgreSQL permanently

# db.refresh(txn)→  re-reads the row from DB back into the txn object
#                   this is how you get the auto-generated UUID back
#                   (PostgreSQL generated it, Python didn't know it yet)
