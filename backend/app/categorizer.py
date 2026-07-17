from typing import Optional
 
 
# ─── Merchant → Category map ──────────────────────────────────────
# Add more merchants here as you discover them in real SMS messages.
# Keys are lowercase. Values are the display category name.



#if transaction type is person to person
PERSON_TRANSFER = "P2P Transfer"

MERCHANT_CATEGORIES: dict[str, str] = {
    # Food & dining
    "zomato":              "Food",
    "swiggy":              "Food",
    "dominos":             "Food",
    "mcdonalds":           "Food",
    "starbucks":           "Food",
    "blinkit":             "Food",
    "zepto":               "Food",
    "Haldiram V Square M": "Food",
    "bigbasket":           "Groceries",
 
    # Travel & transport
    "uber":         "Travel",
    "ola":          "Travel",
    "rapido":       "Travel",
    "irctc":        "Travel",
    "makemytrip":   "Travel",
    "redbus":       "Travel",
 
    # Shopping
    "amazon":       "Shopping",
    "flipkart":     "Shopping",
    "myntra":       "Shopping",
    "meesho":       "Shopping",
    "nykaa":        "Shopping",
    "ajio":         "Shopping",
 
    # Utilities & bills
    "bescom":       "Bills",
    "airtel":       "Bills",
    "jio":          "Bills",
    "bsnl":         "Bills",
    "tatapower":    "Bills",
    "phonepe":      "Bills",
 
    # Health
    "apollo":       "Health",
    "1mg":          "Health",
    "netmeds":      "Health",
    "practo":       "Health",
 
    # Entertainment
    "netflix":              "Entertainment" ,
    "spotify":              "Subscriptions",
    "hotstar":              "Subscriptions",
    "youtube":              "Subscriptions",
    "bookmyshow":           "Subscriptions",
    "googleindiadigital":   "Subscriptions",   # ← "Google India Digital"
    "googleplay":           "Subscriptions",   # ← "Google Play"
    "primevideo":           "Subscriptions",   # ← "Prime Video"
    "appleitunes":          "Subscriptions",

    # Transfers
    "p2ptransfer":   "Transfers",

    "bigbasket": "Groceries"
}
 
 
def get_category(merchant: Optional[str]) -> str:
    """
    Return a spending category for a given merchant name.
    Falls back to "Other" if not found in the map.
 
    Usage:
        get_category("Zomato")   # → "Food"
        get_category("Uber")     # → "Travel"
        get_category("UnknownX") # → "Other"
    """
    if not merchant:
        return "Uncategorized"
    
    # P2P transfers — catch before dict lookup
    if merchant == PERSON_TRANSFER:        # "P2P Transfer"
        return "Transfers"
 
    # Normalize: lowercase, strip spaces, remove common suffixes
    key = merchant.lower().strip()
    key = key.replace(" ", "").replace(".", "")  # "Tata Power" → "tatapower"
 
    return MERCHANT_CATEGORIES.get(key, "Uncategorized")