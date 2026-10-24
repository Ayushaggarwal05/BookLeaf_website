"""
BookLeaf Knowledge Base & Official Operating Policies.

Contains authoritative business rules, service-level agreements (SLAs),
royalty payout schedules, and editorial communication guidelines.
Indexed by operational domain for contextual retrieval by the Gemini AI Copilot.
"""

from typing import Dict, Any, List

# Official Approved Categories (Prompt 5, Section 2)
APPROVED_CATEGORIES = [
    "Royalty & Payments",
    "ISBN & Metadata Issues",
    "Printing & Quality",
    "Distribution & Availability",
    "Book Status & Production Updates",
    "General Inquiry",
]

# Official Approved Priorities (Prompt 5, Section 3)
APPROVED_PRIORITIES = [
    "Critical",
    "High",
    "Medium",
    "Low",
]

# Mapping between standard codes and approved categories
CATEGORY_CODE_MAP = {
    "ROYALTY": "Royalty & Payments",
    "ROYALTY_AND_PAYMENTS": "Royalty & Payments",
    "ISBN": "ISBN & Metadata Issues",
    "METADATA_UPDATE": "ISBN & Metadata Issues",
    "ISBN_AND_METADATA": "ISBN & Metadata Issues",
    "PRINT_QUALITY": "Printing & Quality",
    "PRINTING_AND_QUALITY": "Printing & Quality",
    "DISTRIBUTION": "Distribution & Availability",
    "DISTRIBUTION_AND_AVAILABILITY": "Distribution & Availability",
    "PRODUCTION": "Book Status & Production Updates",
    "COVER_DESIGN": "Book Status & Production Updates",
    "BOOK_STATUS_AND_PRODUCTION": "Book Status & Production Updates",
    "GENERAL": "General Inquiry",
}

# Reverse mapping from AI/department display strings to standard codes
REVERSE_CATEGORY_MAP = {
    "Royalty & Payments": "ROYALTY",
    "ISBN & Metadata Issues": "METADATA_UPDATE",
    "Printing & Quality": "PRINT_QUALITY",
    "Distribution & Availability": "DISTRIBUTION",
    "Book Status & Production Updates": "COVER_DESIGN",
    "General Inquiry": "GENERAL_INQUIRY",
}

# Mapping between AI priority strings and database priority codes
PRIORITY_CODE_MAP = {
    "Critical": "URGENT",
    "High": "HIGH",
    "Medium": "MEDIUM",
    "Low": "LOW",
}

BOOKLEAF_POLICIES: Dict[str, Dict[str, Any]] = {
    "Royalty & Payments": {
        "title": "Royalty Calculation & Payout Policy",
        "rules": [
            "Royalty Split: BookLeaf operates on an 80/20 royalty split (80% of net profit goes to author, 20% retained by BookLeaf).",
            "Net Profit Calculation: Net profit = Maximum Retail Price (MRP) minus printing cost, platform sales commission (Amazon/Flipkart), and shipping charges.",
            "Payout Schedule: Royalties are calculated quarterly and disbursed to authors within 45 calendar days following the close of each quarter (Q1 ends Mar 31 -> paid by May 15; Q2 ends Jun 30 -> paid by Aug 15; Q3 ends Sep 30 -> paid by Nov 15; Q4 ends Dec 31 -> paid by Feb 15).",
            "Minimum Payout Threshold: Minimum payout threshold is ₹1,000. If accumulated quarterly royalties are below ₹1,000, the balance rolls over to the next quarter without deduction.",
            "Disbursement Method & Transparency: Payouts are made via direct bank transfer to the account linked in the author's dashboard. Authors can view a detailed royalty breakdown in their dashboard showing sales figures per platform.",
        ],
    },
    "ISBN & Metadata Issues": {
        "title": "ISBN Assignment & Metadata Management Policy",
        "rules": [
            "ISBN Assignment: Every book published through BookLeaf receives a unique ISBN assigned by BookLeaf and registered under BookLeaf's publisher imprint. If an author wants an ISBN under their own imprint, they need to obtain it independently.",
            "Escalation SLA: If an author reports an ISBN error (duplicate, wrong book linked, or barcode/metadata mismatch), it is treated as a high-priority issue and escalated immediately to the production team.",
            "Metadata Propagation: Author-requested metadata modifications (including book description/blurb, pricing adjustments, sub-genre classifications, or author biography) reflect across online retail channels within 3 to 5 business days.",
        ],
    },
    "Printing & Quality": {
        "title": "Printing Facilities, Turnaround & Quality Policy",
        "rules": [
            "Printing Facilities & Turnaround: In-house printing facility and warehouse are located in Delhi (handling most orders), with print partners including Repro India and Epitome Books for overflow or specific formats. Standard print turnaround is 5–7 business days from order confirmation to dispatch.",
            "Defect Warranty & Free Reprints: If an author reports a quality issue (misprints, binding defects, or color inconsistency), BookLeaf guarantees professional craftsmanship and arranges an expedited free reprint after verification.",
            "Verification Procedure: Authors may be requested to share clear photographic or video documentation of the defective copy along with the print delivery slip or batch reference.",
        ],
    },
    "Distribution & Availability": {
        "title": "Retail Distribution & Availability Policy",
        "rules": [
            "Distribution Channels: Books are listed on Amazon India, Flipkart, Amazon US, Amazon UK, and the BookLeaf Store.",
            "Listing Timeline: Following completion of publication, new listings typically go live across retail channels within 7–10 business days.",
            "Stock Out & Resync: If an active book listing is showing as unavailable on a platform, it usually indicates a stock synchronization issue. BookLeaf's operations team can trigger a manual re-sync within 24–48 hours.",
        ],
    },
    "Book Status & Production Updates": {
        "title": "Publishing Production Stages & Milestone Lifecycle",
        "rules": [
            "Production Pipeline: A book progresses sequentially through: (1) Manuscript Receipt & Formatting → (2) Editing (if opted) → (3) Cover Design → (4) Typesetting → (5) Proofreading → (6) ISBN Assignment → (7) Printing → (8) Distribution Setup → (9) Published & Live Publication.",
            "Author Updates & Bottlenecks: Authors are updated at each milestone via email. Production delays typically occur at Cover Design (waiting for author approval) and Proofreading (revision rounds).",
        ],
    },
    "General Inquiry": {
        "title": "Company Overview & Publishing Packages Policy",
        "rules": [
            "Company Overview: BookLeaf Publishing is a self-publishing company operating in India and the US, providing end-to-end cover design, typesetting, ISBN assignment, printing, distribution, and royalty management.",
            "Publishing Packages: BookLeaf offers two packages: Standard Free (no upfront cost) and Bestseller Breakthrough (premium, paid package with marketing and distribution add-ons).",
            "Account Services: Author contact information, email, phone, city, or linked banking details are updated securely in the dashboard.",
        ],
    },
}

COMMUNICATION_STYLE_GUIDELINES = """
COMMUNICATION STYLE GUIDELINES:
1. Tone: Empathetic, professional, specific, accountable, and encouraging. Address the author respectfully by name.
2. Facts Only: Do not invent payout dates, account status, completed actions, or production facts not present in the database.
3. Missing Information: If key details are missing (such as order ID, photos of print defects, or payout month), politely request them.
4. Next Steps & Timelines: Provide a clear next step and realistic timeline supported by BookLeaf operating policies.
5. Sign-off: Professional sign-off as 'BookLeaf Author Support Team'.
"""


def get_relevant_knowledge(category: str, query_text: str = "") -> str:
    """
    Retrieve formatted knowledge base rules for a given category.
    Includes general communication style guidelines and relevant policy rules.
    """
    matched_cat = normalize_category(category)
    cat_policy = BOOKLEAF_POLICIES.get(matched_cat, BOOKLEAF_POLICIES["General Inquiry"])

    rules_formatted = "\n".join(f"- {rule}" for rule in cat_policy["rules"])
    
    # If query mentions royalties or money, also include royalty policy as supplement
    supplements = []
    if matched_cat != "Royalty & Payments" and any(k in query_text.lower() for k in ["royalty", "payment", "payout", "profit", "inr", "rupee"]):
        royalty_rules = "\n".join(f"- {r}" for r in BOOKLEAF_POLICIES["Royalty & Payments"]["rules"][:3])
        supplements.append(f"\n[SUPPLEMENTAL ROYALTY RULES]\n{royalty_rules}")

    return f"""=== OFFICIAL BOOKLEAF POLICIES: {cat_policy['title']} ===
{rules_formatted}
{''.join(supplements)}

{COMMUNICATION_STYLE_GUIDELINES}
"""


def normalize_category(category: str) -> str:
    """Normalize any category input to one of the 6 approved categories."""
    if not category:
        return "General Inquiry"
    cleaned = category.strip()
    if cleaned in APPROVED_CATEGORIES:
        return cleaned
    code_match = CATEGORY_CODE_MAP.get(cleaned.upper())
    if code_match:
        return code_match
    # Substring search
    c_lower = cleaned.lower()
    if "royalty" in c_lower or "payment" in c_lower or "payout" in c_lower:
        return "Royalty & Payments"
    if "isbn" in c_lower or "metadata" in c_lower:
        return "ISBN & Metadata Issues"
    if "print" in c_lower or "quality" in c_lower or "defect" in c_lower:
        return "Printing & Quality"
    if "distribut" in c_lower or "availab" in c_lower or "amazon" in c_lower or "stock" in c_lower:
        return "Distribution & Availability"
    if "status" in c_lower or "production" in c_lower or "stage" in c_lower or "cover" in c_lower or "typeset" in c_lower:
        return "Book Status & Production Updates"
    return "General Inquiry"


def normalize_priority(priority: str) -> str:
    """Normalize priority to one of the 4 approved priorities."""
    if not priority:
        return "Medium"
    p = priority.strip().capitalize()
    if p in APPROVED_PRIORITIES:
        return p
    p_upper = priority.strip().upper()
    if p_upper in ("URGENT", "CRITICAL", "EMERGENCY"):
        return "Critical"
    if p_upper in ("HIGH", "P1"):
        return "High"
    if p_upper in ("MEDIUM", "NORMAL", "P2"):
        return "Medium"
    if p_upper in ("LOW", "MINOR", "P3"):
        return "Low"
    return "Medium"


# Helper aliases for external modules and testing
def get_knowledge_base() -> Dict[str, Dict[str, Any]]:
    """Return the complete BookLeaf policy catalog."""
    return BOOKLEAF_POLICIES


def find_relevant_policies(category: str) -> List[str]:
    """Return the list of policy rules applicable to a specific category."""
    cat = normalize_category(category)
    return BOOKLEAF_POLICIES.get(cat, {}).get("rules", [])


def format_knowledge_base_for_prompt(category: str, query_text: str = "") -> str:
    """Format policies and communication guidelines for injection into LLM prompts."""
    return get_relevant_knowledge(category, query_text)


COMMUNICATION_GUIDELINES = COMMUNICATION_STYLE_GUIDELINES

