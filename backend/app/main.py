#source venv/Scripts/activate
from fastapi import  FastAPI

from app.routers import auth_router, sms_router, transactions, budgets




app = FastAPI()





app.include_router(sms_router.router)
app.include_router(auth_router.router)
app.include_router(transactions.router)
app.include_router(budgets.router)

