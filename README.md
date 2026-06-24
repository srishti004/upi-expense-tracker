# UPI Expense Tracker

Track your spending automatically — paste a UPI SMS, get a categorized 
transaction, budget alert, and monthly analytics. No manual entry.

Built for Indian users who receive 5-10 UPI transaction SMS daily but 
have no way to turn them into structured financial data without uploading 
to a third-party server. This app parses them locally — your SMS stays 
on your machine.

**What you get**: spending by category, budget vs actual comparison, 
6-month trends, and date-range analysis — all from raw SMS text.

## Input → output

Paste this SMS:

Rs.450 debited from A/c XX1234 for UPI txn to Zomato on 04-Jun.

Get this back:
```json
{
  "amount": 450.00,
  "txn_type": "debit",
  "merchant": "Zomato",
  "category": "Food",
  "txn_date": "2026-06-04"
}
```

## Tech stack

| Layer      | Technology                          |
|------------|-------------------------------------|
| Backend    | Python 3.11, FastAPI, SQLAlchemy    |
| Database   | PostgreSQL, Alembic migrations      |
| Auth       | pwdlib (argon2+bcrypt), PyJWT       |
| Parser     | Python regex, custom categorizer    |
| Frontend   | React, Vite, Recharts, Tailwind v4  |

## Features

- SMS parsing engine — extracts amount, merchant, date, type from raw SMS
- Auto-categorization — 50+ Indian merchants mapped (Zomato, Swiggy, CRED...)
- JWT authentication — argon2 password hashing, protected routes
- Budget tracking — set limits per category, alerts at threshold
- Analytics — monthly trends, date range analysis, category drill-down
- Bulk import — paste multiple SMS at once
- Manual correction — re-label wrong categories, protected from auto-overwrite
- Re-categorization — retroactively fix old transactions when categorizer improves

## Setup

### Prerequisites
- Python 3.11+
- PostgreSQL 14+
- Node.js 18+ (for frontend)

### Backend

```bash
git clone https://github.com/srishti004/upi-expense-tracker.git
cd upi-expense-tracker/backend

python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt

cp .env.example .env
# Edit .env — add SECRET_KEY and DATABASE_URL

alembic upgrade head
uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs

### Environment variables

| Variable                    | Description                        |
|-----------------------------|------------------------------------|
| `SECRET_KEY`                | Random 32-byte hex string          |
| `DATABASE_URL`              | postgresql://user:pass@host/dbname |
| `ALGORITHM`                 | HS256 (default)                    |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 1440 (24h, default)             |


## API endpoints

### Auth
| Method | Endpoint        | Description              |
|--------|-----------------|--------------------------|
| POST   | /auth/signup    | Create account           |
| POST   | /auth/login     | Get JWT token            |
| GET    | /auth/me        | Current user info        |

### Transactions
| Method | Endpoint                          | Description              |
|--------|-----------------------------------|--------------------------|
| POST   | /api/sms/parse                    | Parse single SMS         |
| POST   | /api/sms/parse/bulk               | Parse multiple SMS       |
| POST   | /api/sms/recategorize             | Re-run categorizer       |
| GET    | /api/transactions                 | List with filters        |
| PUT    | /api/transactions/{id}/category   | Manual re-label          |

### Budgets
| Method | Endpoint              | Description              |
|--------|-----------------------|--------------------------|
| POST   | /api/budgets          | Create or update budget  |
| GET    | /api/budgets          | List budgets             |
| PUT    | /api/budgets/{id}     | Edit budget              |
| GET    | /api/budgets/summary  | Spent vs limit per cat.  |

### Analytics
| Method | Endpoint                            | Description              |
|--------|-------------------------------------|--------------------------|
| GET    | /api/analytics/dashboard            | Full dashboard data      |
| GET    | /api/analytics/spending             | Date range analysis      |
| GET    | /api/analytics/monthly-trend        | 6-month chart data       |
| GET    | /api/analytics/category/{name}      | Category drill-down      |

## Project structure
backend/

├── app/

│   ├── main.py           FastAPI app + CORS + router registration

│   ├── config.py         pydantic-settings configuration

│   ├── models.py         SQLAlchemy: User, Transaction, Budget

│   ├── schemas.py        Pydantic request/response schemas

│   ├── auth.py           JWT + password hashing + get_current_user

│   ├── database.py       DB engine + session + get_db dependency

│   └── routers/

│       ├── auth_router.py

│       ├── sms_router.py

│       ├── transactions.py

│       ├── budgets.py

│       └── analytics.py

│   └── parser/

│       ├── parser.py     SMS parsing, ParsedSMS dataclass

│       └── categorizer.py MERCHANT_CATEGORIES dict

├── alembic/              DB migrations

└── requirements.txt
