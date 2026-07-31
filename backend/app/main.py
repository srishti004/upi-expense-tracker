from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth_router, sms_router, transactions, budgets, analytics

app = FastAPI()

origins = [
    "http://localhost:5173",
    "https://upi-expense-tracker-zeta.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sms_router.router)
app.include_router(auth_router.router)
app.include_router(transactions.router)
app.include_router(budgets.router)
app.include_router(analytics.router)