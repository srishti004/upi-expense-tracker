# backend/verify_db.py
# Run with: python verify_db.py
# Delete after it works.

from datetime import date
from decimal import Decimal
from sqlalchemy import func, extract, text
from app.database import SessionLocal
from app.models import User, Transaction, Budget
import uuid

db = SessionLocal()

try:
    print("\n── Step 1: clean slate ──────────────────────────")
    # wipe any previous test data so you can re-run safely
    db.query(Transaction).delete()
    db.query(Budget).delete()
    db.query(User).delete()
    db.commit()
    print("✓ old test data cleared")

    # ─── insert a user ───────────────────────────────────
    print("\n── Step 2: insert user ──────────────────────────")
    user = User(
        email           = "test@upitracker.com",
        hashed_password = "bcrypt_goes_here",   # plaintext ok for testing only
        fullname       = "Test User",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"✓ user created  → id: {user.id}")

    # ─── insert transactions ──────────────────────────────
    print("\n── Step 3: insert transactions ──────────────────")
    txns = [
        Transaction(
            user_id  = user.id,
            amount   = Decimal("450.00"),
            txn_type = "debit",
            merchant = "Zomato",
            category = "Food",
            txn_date = date(2024, 4, 10),
            raw_sms  = "Rs.450 debited from A/c XX1234 to Zomato on 10-Apr",
        ),
        Transaction(
            user_id  = user.id,
            amount   = Decimal("320.00"),
            txn_type = "debit",
            merchant = "Swiggy",
            category = "Food",
            txn_date = date(2024, 4, 15),
            raw_sms  = "Rs.320 debited from A/c XX1234 to Swiggy on 15-Apr",
        ),
        Transaction(
            user_id  = user.id,
            amount   = Decimal("200.00"),
            txn_type = "debit",
            merchant = "Uber",
            category = "Travel",
            txn_date = date(2024, 4, 18),
            raw_sms  = "Rs.200 debited from A/c XX1234 to Uber on 18-Apr",
        ),
        Transaction(
            user_id  = user.id,
            amount   = Decimal("5000.00"),
            txn_type = "credit",            # credit — should NOT appear in summary
            merchant = "SALARY",
            category = "Uncategorized",
            txn_date = date(2024, 4, 1),
            raw_sms  = "Rs.5000 credited to A/c XX1234 on 01-Apr",
        ),
    ]
    db.add_all(txns)
    db.commit()
    print(f"✓ {len(txns)} transactions inserted")

    # ─── insert budgets ───────────────────────────────────
    print("\n── Step 4: insert budgets ───────────────────────")
    budgets = [
        Budget(
            user_id         = user.id,
            category        = "Food",
            monthly_limit   = Decimal("5000.00"),
            alert_threshold = Decimal("0.80"),
        ),
        Budget(
            user_id         = user.id,
            category        = "Travel",
            monthly_limit   = Decimal("2000.00"),
            alert_threshold = Decimal("0.80"),
        ),
    ]
    db.add_all(budgets)
    db.commit()
    print(f"✓ {len(budgets)} budgets inserted")

    # ─── query 1: list transactions ───────────────────────
    print("\n── Step 5: query transactions (April 2024) ──────")
    results = (
        db.query(Transaction)
        .filter(
            Transaction.user_id  == user.id,
            Transaction.txn_type == "debit",
            extract("month", Transaction.txn_date) == 4,
            extract("year",  Transaction.txn_date) == 2024,
        )
        .order_by(Transaction.txn_date.desc())
        .all()
    )
    print(f"✓ found {len(results)} debit transactions")
    for t in results:
        print(f"  {t.txn_date}  {t.merchant:<12} ₹{t.amount}  [{t.category}]")

    expected_count = 3   # 3 debits, salary credit excluded
    assert len(results) == expected_count, \
        f"✗ expected {expected_count} transactions, got {len(results)}"
    print(f"✓ count check passed")

    # ─── query 2: budget summary ──────────────────────────
    print("\n── Step 6: budget summary (April 2024) ──────────")
    summary = (
        db.query(
            Budget.category,
            Budget.monthly_limit,
            Budget.alert_threshold,
            func.coalesce(
                func.sum(Transaction.amount), 0
            ).label("spent"),
        )
        .outerjoin(
            Transaction,
            (Transaction.user_id  == Budget.user_id)  &
            (Transaction.category == Budget.category)  &
            (Transaction.txn_type == "debit")          &
            (extract("month", Transaction.txn_date) == 4) &
            (extract("year",  Transaction.txn_date) == 2024),
        )
        .filter(Budget.user_id == user.id, Budget.is_active == True)
        .group_by(
            Budget.category,
            Budget.monthly_limit,
            Budget.alert_threshold,
        )
        .all()
    )

    print(f"✓ summary rows returned: {len(summary)}")
    print(f"\n  {'Category':<14} {'Spent':>8} {'Limit':>8}  {'%':>6}  Alert?")
    print(f"  {'─'*14} {'─'*8} {'─'*8}  {'─'*6}  {'─'*6}")
    for row in summary:
        pct      = float(row.spent) / float(row.monthly_limit)
        alert    = "⚠ YES" if pct >= float(row.alert_threshold) else "no"
        print(f"  {row.category:<14} ₹{row.spent:>7} ₹{row.monthly_limit:>7}"
              f"  {pct:>5.0%}  {alert}")

    # ─── assertions ───────────────────────────────────────
    print("\n── Step 7: assertions ───────────────────────────")

    food_row   = next(r for r in summary if r.category == "Food")
    travel_row = next(r for r in summary if r.category == "Travel")

    assert float(food_row.spent)   == 770.0,  \
        f"✗ food spent wrong: {food_row.spent}"
    assert float(travel_row.spent) == 200.0,  \
        f"✗ travel spent wrong: {travel_row.spent}"

    food_pct   = float(food_row.spent)   / float(food_row.monthly_limit)
    travel_pct = float(travel_row.spent) / float(travel_row.monthly_limit)

    assert food_pct   < float(food_row.alert_threshold),   \
        "✗ food alert should NOT fire at 15.4%"
    assert travel_pct < float(travel_row.alert_threshold), \
        "✗ travel alert should NOT fire at 10%"

    print("✓ food spent   = ₹770   (₹450 Zomato + ₹320 Swiggy)")
    print("✓ travel spent = ₹200   (₹200 Uber)")
    print("✓ credit txn excluded from both summaries")
    print("✓ no alerts firing  (food 15.4%, travel 10%)")

    print("\n✓✓ ALL CHECKS PASSED — database layer is working correctly\n")

except AssertionError as e:
    db.rollback()
    print(f"\n{e}\n")

except Exception as e:
    db.rollback()
    print(f"\n✗ unexpected error: {e}\n")
    raise

finally:
    db.close()