#source venv/Scripts/activate
#uvicorn app.main:app --reload
from fastapi import  FastAPI

from app.routers import auth_router, sms_router, transactions, budgets,analytics




app = FastAPI()


# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:5173"],  # React dev server
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )




app.include_router(sms_router.router)
app.include_router(auth_router.router)
app.include_router(transactions.router)
app.include_router(budgets.router)
app.include_router(analytics.router)


