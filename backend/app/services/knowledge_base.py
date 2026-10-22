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
    "GENERAL_INQUIRY": "General Inquiry",
    "GENERAL": "General Inquiry",
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
            "Royalty Split: BookLeaf operates on an 80/20 net profit split (80% payable to author, 20% retained by BookLeaf).",
            "Net Profit Definition: Net profit is calculated by deducting manufacturing/printing costs, retail platform sales commission (e.g., Amazon, Flipkart, Ingram), and fulfillment/shipping fees from the Maximum Retail Price (MRP).",
            "Payout Schedule: Royalties are calculated quarterly and disbursed to authors within 45 calendar days following the close of each quarter (Q1 ends Mar 31 -> paid by May 15; Q2 ends Jun 30 -> paid by Aug 15; Q3 ends Sep 30 -> paid by Nov 15; Q4 ends Dec 31 -> paid by Feb 15).",
            "Minimum Payout Threshold: The minimum payout threshold is ₹1,000. If accrued quarterly royalties are below ₹1,000, the outstanding balance rolls over into the subsequent quarterly payout cycle without deduction.",
            "Taxes & Records: TDS deductions are applied in compliance with prevailing income tax regulations, and an official digital statement is issued upon remittance.",
        ],
    },
    "ISBN & Metadata Issues": {
        "title": "ISBN Assignment & Metadata Management Policy",
        "rules": [
            "ISBN Assignment: ISBNs are assigned directly by BookLeaf Publishing and registered under BookLeaf's official imprint, unless the author has obtained and registered an independent ISBN under their personal imprint.",
            "Escalation SLA: Any reported ISBN mismatch (such as title, author, barcode, or format discrepancy) is designated as a High/Critical priority issue and escalated immediately to the cataloging and editorial operations desk.",
            "Metadata Propagation: Author-requested metadata modifications (including book description/blurb, pricing adjustments, sub-genre classifications, or author biography) reflect across online retail channels within 3 to 5 business days.",
        ],
    },
    "Printing & Quality": {
        "title": "Printing Turnaround & Manufacturing Quality Policy",
        "rules": [
            "Standard Turnaround: Standard turnaround time for author proof copies and print-on-demand orders is 5 to 7 business days from print-file approval to carrier dispatch.",
            "Defect Warranty & Free Reprints: BookLeaf guarantees professional craftsmanship. Verified printing or physical manufacturing defects (such as binding delamination, cover misregistration, color banding, or missing/inverted pages) qualify for an expedited free replacement reprint under our quality guarantee.",
            "Verification Procedure: Authors are requested to submit clear photographic or video documentation of the defect along with the print delivery slip or batch reference.",
        ],
    },
    "Distribution & Availability": {
        "title": "Retail Distribution & Availability Policy",
        "rules": [
            "Listing Turnaround: Following official publication, digital catalog ingestion and physical retail listings generally require 7 to 10 business days to become live across distribution channels (Amazon, Flipkart, BookLeaf Direct, Ingram).",
            "Stock Availability Resync: If an active listing temporarily displays as 'Currently Unavailable' or 'Out of Stock', this typically reflects an automated inventory feed synchronization between the print facility and the retailer. Stock data resynchronization typically completes within 24 to 48 hours.",
        ],
    },
    "Book Status & Production Updates": {
        "title": "Publishing Production Stages & Milestone Lifecycle",
        "rules": [
            "Production Stages: The BookLeaf publishing pipeline progresses sequentially through: (1) Manuscript Receipt & Formatting, (2) Editorial Review (if enrolled), (3) Cover & Interior Design Proofing, (4) Typesetting & Layout Approval, (5) Author Proofreading Sign-Off, (6) ISBN Assignment & Barcoding, (7) Print Proof Approval, (8) Distribution Setup & Aggregator Ingestion, and (9) Live Publication.",
            "Milestone Status: Production updates reflect the current verified stage in the database. Timelines for each milestone are communicated transparently.",
        ],
    },
    "General Inquiry": {
        "title": "General Inquiries & Account Services Policy",
        "rules": [
            "Account Updates: Contact information updates (email, phone, address, banking details) are processed securely after identity verification.",
            "Communication Standard: BookLeaf's communication style is empathetic, professional, specific, accountable, and transparent regarding next steps.",
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

