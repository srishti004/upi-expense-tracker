"""
Run these tests with:  pytest backend/tests/test_parser.py::test_bob_paytm -v

"""
import re
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.parser import parse_upi_sms
from app.categorizer import get_category


# ─── Parser tests ─────────────────────────────────────────────────
def test_hdfc_blinkit():
    sms = "INR 329.00 debited A/c no. XX7586 17-04-26, 13:44:23 UPI/P2M/610768938985/Blinkit Not you? SMS BLOCKUPI Cust ID to 919951860002 HDFC Bank"
    r = parse_upi_sms(sms)
    assert r.is_upi    == True
    assert r.amount    == 329.00
    assert r.txn_type  == "debit"
    assert r.account   == "XX7586"
    assert r.merchant  == "Blinkit"
    assert r.upi_ref   == "610768938985"
    assert r.bank      == "HDFC Bank"
    print(r.category)

def test_axis_p2a():
    sms = """INR 137.00 debited
    A/c no. XX7457
    24-04-26, 14:58:13
    UPI/P2A/611473038694/ANANDEETA
    Not you? SMS BLOCKUPI Cust ID to 919951860002
    Axis Bank"""
    r = parse_upi_sms(sms)
    assert r.is_upi   == True
    assert r.amount   == 137.00
    assert r.txn_type == "debit"
    assert r.account  == "XX7457"
    assert r.upi_ref  == "611473038694"
    assert r.merchant == "P2P Transfer"    # P2A = person transfer
    assert r.bank     == "Axis Bank"
    print(r.category)

def test_axis_p2a_credit():
    sms = """INR 48.00 credited
A/c no. XX7457
07-07-25, 12:26:07 IST
UPI/P2A/518857354146/PhonePe/YES BANK/skill-creator - Axis Bank"""
    r = parse_upi_sms(sms)
    assert r.is_upi   == True
    assert r.amount   == 48.00
    assert r.txn_type == "credit"
    assert r.account  == "XX7457"
    assert r.upi_ref  == "518857354146"
    assert r.merchant == None        # P2A — person transfer
    assert r.bank     == "Axis Bank"
    print(r.category)
def test1():
    sms = """ INR 80.00 debited
A/c no. XX7457
05-05-26, 14:11:27
UPI/P2M/649138467938/SHRI SHYAM ENTERPRI
Not you? SMS BLOCKUPI Cust ID to 919951860002
Axis Bank"""
    r = parse_upi_sms(sms)
    assert r.is_upi   == True
    assert r.amount   == 80.00
    assert r.txn_type == "debit"
    assert r.account  == "XX7457"
    assert r.merchant == "SHRI SHYAM ENTERPRI"       
    assert r.bank     == "Axis Bank"
    print(r.category)

def test2():
    sms = """INR 6500.00 credited
A/c no. XX7457
09-05-26, 09:33:42 IST
UPI/P2A/649541217267/MADHU  LA/UTIB/UPI - Axis Bank"""
    r = parse_upi_sms(sms)
    assert r.is_upi   == True
    assert r.amount   == 6500.00
    assert r.txn_type == "credit"
    assert r.account  == "XX7457"
    assert r.merchant == "P2P Transfer"       
    assert r.bank     == "Axis Bank"
    print(r.category)

def test3():
    sms = """INR 2005.00 debited
A/c no. XX7457
03-05-26, 10:27:10
UPI/P2M/648912992303/10 Haryana Jagriti
Not you? SMS BLOCKUPI Cust ID to 919951860002
Axis Bank """
    r = parse_upi_sms(sms)
    assert r.is_upi   == True
    assert r.amount   == 2005.00
    assert r.txn_type == "debit"
    assert r.account  == "XX7457"
    assert r.merchant == "10 Haryana Jagriti"       
    assert r.bank     == "Axis Bank"
    print(r.category)

def test4():
    sms =  """INR 12865.00 debited
A/c no. XX7457
25-07-25, 15:14:18
UPI/P2M/557292264361/Bajaj Finance Limit
Not you? SMS BLOCKUPI Cust ID to 919951860002
Axis Bank""" 
    r = parse_upi_sms(sms)
    assert r.is_upi   == True
    assert r.amount   == 12865.00
    assert r.txn_type == "debit"
    assert r.account  == "XX7457"
    assert r.merchant == "Bajaj Finance Limit"       
    assert r.bank     == "Axis Bank"
    print(r.category)

def test5():
    sms = """INR 437.00 credited
A/c no. XX7457
18-03-26, 18:57:14 IST
UPI/P2A/704499170776/Amazon Pa/UTIB/Refu - Axis Bank """
    r = parse_upi_sms(sms)
    assert r.is_upi   == True
    assert r.amount   == 437.00
    assert r.txn_type == "credit"
    assert r.account  == "XX7457"
    assert r.merchant == "Amazon Pa"       
    assert r.bank     == "Axis Bank"
    print(r.category)

def test6():
    sms = """INR 963.77 debited
A/c no. XX7457
28-09-25, 18:08:26
UPI/P2M/527154584467/Haldiram V Square M
Not you? SMS BLOCKUPI Cust ID to 919951860002
Axis Bank"""
    r = parse_upi_sms(sms)
    assert r.is_upi   == True
    assert r.amount   == 963.77
    assert r.txn_type == "debit"
    assert r.account  == "XX7457"
    assert r.merchant == "Haldiram V Square M"       
    assert r.bank     == "Axis Bank"
    print(r.category)
    
# def test_non_upi_sms():
#     sms = "Your OTP is 847291. Do not share with anyone."
#     r = parse_upi_sms(sms)
#     assert r.is_upi == False
#     assert r.amount  == None

# def test_empty_sms():
#     r = parse_upi_sms("")
#     assert r.is_upi == False

def test_bob_paytm():
    sms = "Rs.290.00 Dr. from A/C XXXXXX4997 and Cr. to paytmqr95bi1we7ef@paytm. Ref:702129793040. AvlBal:Rs32812.02(2026:04:20 01:35:43). Not you? Call 18005700/5000-BOB"
    r = parse_upi_sms(sms)
    assert r.is_upi   == True
    assert r.amount   == 290.00
    assert r.txn_type == "debit"        # once you fix Dr. → "debit"
    assert r.account  == "XXXXXX4997"
    assert r.merchant == "Paytm"        # once you fix VPA extraction         # once you add BOB to BANK_PATTERN
    print(r.category)

def test_p2p_stores_vpa():
    sms = "Rs.77.00 Dr. from A/C XXXXXX4997 and Cr. to reetudevi0067@nyes. Ref:202412786229. AvlBal:Rs33102.02(2026:04:19 07:37:18). Not you? Call 18005700/5000-BOB"
    r = parse_upi_sms(sms)
    assert r.merchant == "P2P Transfer"
    assert r.vpa      == "reetudevi0067@nyes"   # raw VPA stored for later lookup
    print(r.category)


# ─── Categorizer tests ────────────────────────────────────────────

def test_known_merchant():
    assert get_category("Zomato")  == "Food"
    assert get_category("Uber")    == "Travel"
    assert get_category("Netflix") == "Subscriptions"

def test_unknown_merchant():
    assert get_category("SomeRandomShop") == "Other"

def test_none_merchant():
    assert get_category(None) == "Other"











