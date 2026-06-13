from fastapi import APIRouter, FastAPI
from typing import Annotated
from app.routers import auth_router, sms_router, transactions, budgets




app = FastAPI()





app.include_router(sms_router.router)
app.include_router(auth_router.router)

