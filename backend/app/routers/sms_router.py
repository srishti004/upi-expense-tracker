from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from app.database import get_db
from app.schemas import SMSParseRequest, TransactionResponse
import app.models
from app.parser import parse_upi_sms
from app.categorizer import get_category
from  typing import  Annotated
from  sqlalchemy.orm  import Session
from app.auth import get_current_user


router = APIRouter(prefix="/api/sms", tags=["sms"])

@router.post("/parse", response_model=TransactionResponse)
def parse_sms(
    body: SMSParseRequest,
    db:   Annotated[Session, Depends(get_db)],
    current_user: Annotated[app.models.User, Depends(get_current_user)],
):

    result = parse_upi_sms(body.raw_sms)

    
       
    if not result.is_upi:
        raise HTTPException(
            status_code=400,
            detail="This doesn't look like a UPI transaction SMS"
        )

    if result.amount is None:
        raise HTTPException(
            status_code=422,
            detail="Could not extract amount from this SMS"
        )

    

    category = get_category(result.merchant)

    txn = app.models.Transaction(
        user_id        = current_user.id,
        amount         = result.amount,
        txn_type       = result.txn_type,
        merchant       = result.merchant,
        account_masked = result.account,
        txn_date       = result.txn_date,
        category       = category,
        raw_sms        = body.raw_sms,
    )

    db.add(txn)
    db.commit()
    db.refresh(txn)
    return txn

# db.add(txn)    →  tells SQLAlchemy "I want to insert this row"
#                   nothing written to DB yet — it's staged in memory

# db.commit()    →  executes INSERT INTO transactions (...) VALUES (...)
#                   row now exists in PostgreSQL permanently

# db.refresh(txn)→  re-reads the row from DB back into the txn object
#                   this is how you get the auto-generated UUID back
#                   (PostgreSQL generated it, Python didn't know it yet)
