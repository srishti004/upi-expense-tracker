import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
import re
from dataclasses import dataclass
from typing import Optional
from app.categorizer import get_category


# ═══════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════

# Sentinel value returned as merchant when the transaction is
# between two people (P2P / P2A debit / incoming credit from person)
PERSON_TRANSFER = "P2P Transfer"

# Payment app names that appear in UPI paths as routing metadata,
# NOT as merchant names. e.g. "UPI/P2A/.../PhonePe/YES BANK/..."
# These are ignored during merchant extraction.
PAYMENT_APP_NAMES = {
    'phonepe', 'paytm', 'googlepay', 'amazonpay',
    'bhim', 'mobikwik', 'freecharge'
}


# ═══════════════════════════════════════════════════════════════════
# DATACLASS — structured result returned by parse_upi_sms()
# ═══════════════════════════════════════════════════════════════════

@dataclass
class ParsedSMS:
    amount:    Optional[float]   # transaction amount e.g. 450.0
    txn_type:  Optional[str]     # "debit" or "credit"
    merchant:  Optional[str]     # merchant name, "P2P Transfer", or None
    category:  Optional[str]     # spending category from categorizer
    account:   Optional[str]     # masked account number e.g. "XX1234"
    txn_date:  Optional[str]     # date string as found in SMS
    txn_time:  Optional[str]     # time string HH:MM:SS
    raw_sms:   str               # original unmodified SMS text
    is_upi:    bool              # False if SMS is not a bank/UPI message
    upi_type:  Optional[str]     # "P2M", "P2P", "P2A", "CR", "DR"
    upi_ref:   Optional[str]     # UPI reference number (10+ digits)
    bank:      Optional[str]     # sending bank name e.g. "Axis Bank"
    vpa:       Optional[str]     # raw VPA address e.g. "zomato@okicici"


    txn_status:       Optional[str] = None # "success" / "failed" / None
    parse_confidence: Optional[str] = None # "full" / "partial" / "unknown"
    raw_upi_path:     Optional[str]  = None # full UPI path string for debugging


# ═══════════════════════════════════════════════════════════════════
# LOOKUP MAP — VPA domain → display name
# ═══════════════════════════════════════════════════════════════════
# Keys are VPA domains (part after @ in a UPI address).
# Values are the display merchant name, or None for pure bank handles
# (None means it's a person transfer, not a merchant payment).

VPA_MERCHANT_MAP = {
    # ── Wallet / Payment apps ─────────────────────────
    "paytm":        "Paytm",
    "ptyes":        "Paytm",        # Paytm on Yes Bank rail

    # ── Google Pay bank rails ─────────────────────────
    "okaxis":       "Google Pay",
    "okhdfcbank":   "Google Pay",
    "okicici":      "Google Pay",
    "oksbi":        "Google Pay",

    # ── PhonePe bank rails ────────────────────────────
    "ybl":          "PhonePe",      # Yes Bank Limited
    "ibl":          "PhonePe",      # IDFC Bank Limited
    "axl":          "PhonePe",      # Axis Bank Limited

    # ── Amazon Pay ────────────────────────────────────
    "apl":          "Amazon Pay",
    "yapl":         "Amazon Pay",

    # ── Pure bank handles (person transfer, no merchant)
    # These map to None — any VPA using these is a P2P transfer
    "nyes":         None,           # Yes Bank direct
    "upi":          None,           # generic UPI handle
    "hdfcbank":     None,           # HDFC direct
    "icici":        None,           # ICICI direct
    "axisbank":     None,           # Axis direct
    "sbi":          None,           # SBI direct
    "barodampay":   None,           # Bank of Baroda
}


# ═══════════════════════════════════════════════════════════════════
# REGEX PATTERNS
# ═══════════════════════════════════════════════════════════════════

# ── Amount ────────────────────────────────────────────────────────
# Matches: Rs.450 / Rs 450 / INR450 / INR 1200.50
# Negative lookbehind (?<!AvlBal:) prevents matching the available
# balance shown at end of SMS e.g. "AvlBal:Rs.12000"
AMOUNT_PATTERN = re.compile(
    r'(?<!AvlBal:)(?:Rs\.?|INR)\s*(\d{1,7}(?:\.\d{1,2})?)',
    re.IGNORECASE
)

# ── Transaction type ──────────────────────────────────────────────
# Group 1: standard banks  → "debited" / "credited"
# Group 2: Bank of Baroda  → "Dr." (debit abbreviation)
# Group 3: Bank of Baroda  → "Cr." (credit abbreviation)
# Only one group fires per match — others will be None
TXN_TYPE_PATTERN = re.compile(
    r'\b(debited|credited)\b'
    r'|(\bDr\b\.?)'
    r'|(\bCr\b\.?)',
    re.IGNORECASE
)

# ── Merchant name ─────────────────────────────────────────────────
# Three alternative patterns tried in order:
#
# Group 1 — UPI path label (most reliable)
#   Captures name after ref number in UPI path
#   e.g. "UPI/P2M/402819371234/Zomato" → "Zomato"
#   Stops at: newline, slash, "Not you", or end of string
#
# Group 2 — Natural language "to/at" (fallback for older bank formats)
#   e.g. "debited to Zomato on 04-Apr" → "Zomato"
#   Stops at: "on", "via", ".", or end of string
#
# Group 3 + 4 — VPA address (last resort)
#   e.g. "zomato@okicici" → g3="zomato", g4="okicici"
#   g4 is looked up in VPA_MERCHANT_MAP for display name
MERCHANT_PATTERN = re.compile(
    r'UPI/(?:P2M|P2P|P2A|CR|DR)?/\d+/'
    r'([A-Za-z0-9][A-Za-z0-9&\-]*(?:\s[A-Za-z0-9&\-]+){0,5})'
    r'(?=\s*[\n\r/]|\s+Not\s+you|\s*$)'
    r'|(?:to|at)\s+([A-Za-z][A-Za-z0-9\s&\-]{1,30}?)(?=\s+on|\s+via|\.|$)'
    r'|([A-Za-z0-9]+)@(\w+)',
    re.IGNORECASE
)

# ── Account number ────────────────────────────────────────────────
# Matches masked account numbers in formats:
# "A/c XX1234" / "Ac XX5678" / "account no. XX9012"
ACCOUNT_PATTERN = re.compile(
    r'(?:A/c|Ac|account)(?:\s+no\.?)?\s+([A-Z0-9]{2,6}\d{4})',
    re.IGNORECASE
)

# ── UPI signal (gate check) ───────────────────────────────────────
# Quick check before doing any real parsing work.
# If none of these signals appear, it's not a bank SMS.
# Covers: UPI keywords, BOB abbreviations, VPA @address, ref numbers
UPI_SIGNAL_PATTERN = re.compile(
    r'\b(UPI|NEFT|IMPS|debited|credited|txn|transaction)\b'
    r'|Dr\.|Cr\.'
    r'|@[a-z]+'
    r'|\bRef[:\s]\d{6,}\b',
    re.IGNORECASE
)

# ── Date ──────────────────────────────────────────────────────────
# Matches three common date formats found in Indian bank SMS:
# DD-MM-YY or DD-MM-YYYY  e.g. "04-04-26" or "04-04-2026"
# D-Mon-YY                e.g. "4-Apr-26"
# YYYY-MM-DD              e.g. "2026-04-04"
DATE_PATTERN = re.compile(
    r'(\d{2}-\d{2}-\d{2,4})'
    r'|(\d{1,2}[-/](?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[-/]?\d{0,4})'
    r'|(\d{4}-\d{2}-\d{2})',
    re.IGNORECASE | re.MULTILINE
)

# ── Time ──────────────────────────────────────────────────────────
# Matches HH:MM:SS format e.g. "14:32:01"
TIME_PATTERN = re.compile(
    r'\b(\d{2}:\d{2}:\d{2})\b'
)

# ── UPI reference number ──────────────────────────────────────────
# Captures the 10+ digit ref number from the UPI path
# e.g. "UPI/P2M/402819371234/Zomato" → "402819371234"
UPI_REF_PATTERN = re.compile(
    r'UPI/(?:P2M|P2P|P2A|CR|DR)?/(\d{10,})',
    re.IGNORECASE
)

# ── UPI transfer type ─────────────────────────────────────────────
# Captures transfer type code from UPI path
# P2M = Person to Merchant  (you paid a business)
# P2P = Person to Person    (you sent/received money from a person)
# P2A = Person to Account   (bank transfer, or refund)
# CR  = Credit              (incoming)
# DR  = Debit               (outgoing)
UPI_TYPE_PATTERN = re.compile(
    r'UPI/(P2M|P2P|P2A|CR|DR)/',
    re.IGNORECASE
)

# ── Bank name ─────────────────────────────────────────────────────
# Detects which bank sent the SMS from the message body
BANK_PATTERN = re.compile(
    r'\b(HDFC Bank|SBI|ICICI Bank|Axis Bank|Kotak|Punjab National Bank|PNB)\b',
    re.IGNORECASE
)

# ── UPI name from path ────────────────────────────────────────────
# Extracts name segment right after ref number in UPI path.
# Used separately from MERCHANT_PATTERN to inspect P2A paths
# before deciding if they are person transfers or refunds.
# e.g. "UPI/P2A/704499170776/Amazon Pa/UTIB/Refu" → "Amazon Pa"
UPI_NAME_PATTERN = re.compile(
    r'UPI/(?:P2M|P2P|P2A|CR|DR)?/\d+/'
    r'([A-Za-z0-9][A-Za-z0-9&\-]*(?:\s[A-Za-z0-9&\-]+){0,5})'
    r'(?=\s*[\n\r/]|\s+Not\s+you|\s*$)',
    re.IGNORECASE
)


# ═══════════════════════════════════════════════════════════════════
# MAIN PARSER FUNCTION
# ═══════════════════════════════════════════════════════════════════

def parse_upi_sms(sms: str) -> ParsedSMS:
    """
    Parse a raw UPI/bank SMS and return structured fields.

    Returns a ParsedSMS dataclass with all extracted fields.
    If the SMS is not a bank message, is_upi=False and all
    fields are None.

    Usage:
        result = parse_upi_sms("INR 450 debited A/c XX1234 UPI/P2M/123/Zomato")
        result.amount    # 450.0
        result.merchant  # "Zomato"
        result.category  # "Food"
    """

    # ── Step 1: Gate check ────────────────────────────────────────
    # Run a quick scan for any bank/UPI signal before doing real work.
    # Filters out OTPs, promotional SMS, delivery alerts etc.
    if not UPI_SIGNAL_PATTERN.search(sms):
        return ParsedSMS(
            amount=None,    txn_type=None,  merchant=None,
            category=None,  account=None,   txn_date=None,
            txn_time=None,  raw_sms=sms,    is_upi=False,
            upi_type=None,  upi_ref=None,   bank=None,
             vpa=None,
        )

    # ── Step 2: Run all regex patterns ───────────────────────────
    # Run every pattern upfront. Each returns a match object or None.
    amount_match   = AMOUNT_PATTERN.search(sms)
    type_match     = TXN_TYPE_PATTERN.search(sms)
    account_match  = ACCOUNT_PATTERN.search(sms)
    upi_type_match = UPI_TYPE_PATTERN.search(sms)
    upi_ref_match  = UPI_REF_PATTERN.search(sms)
    upi_name_match = UPI_NAME_PATTERN.search(sms)
    date_match     = DATE_PATTERN.search(sms)
    time_match     = TIME_PATTERN.search(sms)
    bank_match     = BANK_PATTERN.search(sms)
    vpa_match      = re.search(r'[A-Za-z0-9.\-]+@[A-Za-z0-9]+', sms)

    # ── Step 3: Extract amount ────────────────────────────────────
    # Convert matched string "450.00" → float 450.0
    # Returns None if no amount found
    amount = float(amount_match.group(1)) if amount_match else None

    # ── Step 4: Extract transaction type ─────────────────────────
    # Normalise all variants to "debit" or "credit":
    #   "debited" → "debit"
    #   "Dr."     → "debit"   (Bank of Baroda format)
    #   "credited"→ "credit"
    #   "Cr."     → "credit"  (Bank of Baroda format)
    if type_match:
        # Only one group fires — pick the non-None one
        raw = (type_match.group(1) or type_match.group(2) or type_match.group(3))
        raw = raw.lower().rstrip('.')       # "Dr." → "dr"
        if raw in ('debited', 'dr'):
            txn_type = 'debit'
        elif raw in ('credited', 'cr'):
            txn_type = 'credit'
        else:
            txn_type = None
    else:
        txn_type = None

    # ── Step 5: Extract UPI transfer type ────────────────────────
    # Pulled from the UPI path e.g. "UPI/P2M/..." → "P2M"
    # This drives the entire merchant resolution logic in Step 6
    upi_type = upi_type_match.group(1).upper() if upi_type_match else None

    # ── Step 6: Extract name from UPI path ───────────────────────
    # Captured separately before merchant logic to inspect P2A paths.
    # e.g. "UPI/P2A/704499170776/Amazon Pa/UTIB/Refu" → "Amazon Pa"
    # Used to distinguish refunds from person transfers in P2A credit.
    upi_name = upi_name_match.group(1).strip() if upi_name_match else None

    # ── Step 7: Merchant resolution ──────────────────────────────
    # Decision tree based on upi_type and txn_type.
    # upi_type is the primary authority — it tells us the transfer
    # category before we even look at the merchant name.
    #
    # Full decision tree:
    #
    #   P2P (any direction)
    #       → always "P2P Transfer" (person to person, no merchant)
    #
    #   P2A + debit (you sent money to a bank account)
    #       → always "P2P Transfer" (no merchant involved)
    #
    #   P2A + credit (money came into your account)
    #       → 3 sub-cases based on UPI path content:
    #           a) "/Refu" in path + name present → merchant (refund)
    #              e.g. "Amazon Pa/UTIB/Refu" → "Amazon Pa"
    #           b) name is a payment app (PhonePe, Paytm etc) → None
    #              e.g. "PhonePe/YES BANK/..." → routing noise, not merchant
    #           c) name is a person name → "P2P Transfer"
    #              e.g. "MADHU LA/UTIB/..." → person sent you money
    #
    #   credit + upi_type unknown (no UPI path in SMS)
    #       → "P2P Transfer" (safe fallback for incoming transfers)
    #
    #   P2M or unknown debit (merchant payment)
    #       → run MERCHANT_PATTERN to extract name:
    #           g1 → name from UPI path  e.g. "Zomato"
    #           g2 → name from "to/at"   e.g. "to Zomato"
    #           g4 → VPA domain lookup   e.g. "okicici" → "Google Pay"

    if upi_type == 'P2P':
        # Person to person transfer — no merchant ever
        merchant = PERSON_TRANSFER

    elif upi_type == 'P2A' and txn_type == 'debit':
        # You sent money to someone's bank account — no merchant
        merchant = PERSON_TRANSFER

    elif upi_type == 'P2A' and txn_type == 'credit':
        # Incoming P2A — could be refund, person transfer, or noise
        is_refund = bool(re.search(r'/Refu\b', sms, re.IGNORECASE))

        if is_refund and upi_name:
            # Refund from a merchant e.g. Amazon Pa/UTIB/Refu
            merchant = upi_name

        elif upi_name and upi_name.lower().replace(' ', '') in PAYMENT_APP_NAMES:
            # Payment app name in path = routing metadata, not a merchant
            # e.g. PhonePe/YES BANK/skill-creator
            merchant = None

        else:
            # Person name in path = someone sent you money
            # e.g. MADHU LA/UTIB/UPI
            merchant = PERSON_TRANSFER

    elif txn_type == 'credit' and upi_type != 'P2M':
        # Incoming credit with no UPI path — safe fallback
        merchant = PERSON_TRANSFER

    else:
        # P2M or unknown — run full MERCHANT_PATTERN to find merchant name
        merchant_match = MERCHANT_PATTERN.search(sms)

        if merchant_match:
            g1 = merchant_match.group(1)    # UPI path label  e.g. "Zomato"
            g2 = merchant_match.group(2)    # "to/at" name    e.g. "Zomato"
            g3 = merchant_match.group(3)    # VPA prefix      e.g. "zomato"
            g4 = merchant_match.group(4)    # VPA domain      e.g. "okicici"

            if g1 or g2:
                # Direct name found — use it as-is
                merchant = (g1 or g2).strip()

            elif g4:
                # VPA domain found — look up display name in map
                # If domain maps to None → bank handle → person transfer
                # If domain not in map → use capitalized domain as fallback
                raw_domain = g4.lower()
                mapped = VPA_MERCHANT_MAP.get(raw_domain, raw_domain.capitalize())
                merchant = mapped if mapped is not None else PERSON_TRANSFER

            else:
                # Regex matched but no useful group captured
                merchant = None
        else:
            # No pattern matched — genuine parse failure
            merchant = None

    # ── Step 8: Category resolution ──────────────────────────────
    # upi_type is the authority for P2P/P2A — always "Transfers"
    # regardless of what merchant name was found.
    # For everything else, look up merchant in categorizer.
    if upi_type in ('P2P', 'P2A'):
        category = "Transfers"
    else:
        category = get_category(merchant)

    # ── Step 9: Extract remaining simple fields ───────────────────
    # Each follows the same safe pattern:
    # if match found → extract group → else None
    account  = account_match.group(1).upper() if account_match else None
    txn_date = date_match.group(0)            if date_match    else None
    txn_time = time_match.group(1)            if time_match    else None
    upi_ref  = upi_ref_match.group(1)         if upi_ref_match else None
    bank     = bank_match.group(1)            if bank_match    else None

    # Raw VPA address extracted separately — stored for dispute resolution
    # or contact lookup even when merchant = "P2P Transfer"
    # e.g. "reetudevi0067@nyes" preserved even though merchant is sentinel
    vpa = vpa_match.group(0).lower() if vpa_match else None

    # ── Step 10: Return structured result ────────────────────────
    return ParsedSMS(
        amount=amount,
        txn_type=txn_type,
        merchant=merchant,
        category=category,
        account=account,
        txn_date=txn_date,
        txn_time=txn_time,
        raw_sms=sms,
        is_upi=True,
        upi_type=upi_type,
        upi_ref=upi_ref,
        bank=bank,
        vpa=vpa,
    )




if __name__ == "__main__":
    print(parse_upi_sms("Rs.450 debited from A/c XX1234 for UPI txn to Zomato on 04-Apr."))