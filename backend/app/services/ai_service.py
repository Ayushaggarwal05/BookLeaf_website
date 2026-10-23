"""
Google Gemini AI Service for BookLeaf Support Portal.

Provides structured ticket triage (classification and priority scoring)
and context-aware response drafting using the BookLeaf knowledge base.
Implements bounded retries, graceful fallbacks, and strict secret hygiene.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ValidationError

from backend.app.core.config import settings
from backend.app.services.knowledge_base import (
    APPROVED_CATEGORIES,
    APPROVED_PRIORITIES,
    PRIORITY_CODE_MAP,
    get_relevant_knowledge,
    find_relevant_policies,
    normalize_category,
    normalize_priority,
)

logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Structured Output Schemas (Validated by Pydantic)
# -----------------------------------------------------------------------------

class AiTriageOutput(BaseModel):
    """Structured output expected from Gemini for ticket triage."""
    category: str = Field(
        ...,
        description=f"Exactly one category from: {', '.join(APPROVED_CATEGORIES)}",
    )
    priority: str = Field(
        ...,
        description=f"Exactly one priority from: {', '.join(APPROVED_PRIORITIES)}",
    )
    confidence: float = Field(
        default=0.85,
        ge=0.0,
        le=1.0,
        description="Confidence score between 0.0 and 1.0",
    )
    reasoning: str = Field(
        ...,
        description="Concise rationale explaining the category classification and priority assessment.",
    )
    applicable_policies: List[str] = Field(
        default_factory=list,
        description="List of relevant BookLeaf operating policies cited.",
    )


class AiDraftOutput(BaseModel):
    """Structured output expected from Gemini for author response drafting."""
    draft_response: str = Field(
        ...,
        description="Empathetic, professional draft response adhering strictly to BookLeaf knowledge base policies.",
    )
    suggested_category: str = Field(
        ...,
        description=f"Category from: {', '.join(APPROVED_CATEGORIES)}",
    )
    suggested_priority: str = Field(
        ...,
        description=f"Priority from: {', '.join(APPROVED_PRIORITIES)}",
    )
    confidence: float = Field(default=0.85, ge=0.0, le=1.0)
    reasoning: str = Field(
        ...,
        description="Brief explanation of policy rationale and next steps provided to author.",
    )
    relevant_policies: List[str] = Field(
        default_factory=list,
        description="List of specific knowledge base policy points cited.",
    )


class AiTriageResult(BaseModel):
    """Standardized service result returned to application handlers."""
    category: str
    priority: str
    priority_code: str
    confidence: float
    reasoning: str
    status: str  # "success", "fallback", "unavailable"
    model: str
    created_at: str
    applicable_policies: List[str] = Field(default_factory=list)
    provider: Optional[str] = None
    error_message: Optional[str] = None

    def model_post_init(self, __context: Any) -> None:
        if not self.provider:
            self.provider = self.model


class AiDraftResult(BaseModel):
    """Standardized draft result returned to admin ticket detail view."""
    draft_response: str
    suggested_category: str
    suggested_priority: str
    priority_code: str
    confidence: float
    reasoning: str
    relevant_policies: List[str]
    status: str  # "success", "unavailable", "error"
    model: str
    error_message: Optional[str] = None
    created_at: str


# -----------------------------------------------------------------------------
# Gemini AI Service Class
# -----------------------------------------------------------------------------

class GeminiService:
    """
    Dedicated AI Service wrapping Google's official Gemini SDK.
    Handles authentication, client lifecycle, prompt generation,
    structured JSON validation, and non-blocking failure recovery.
    """

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self._explicit_key = api_key
        self.model_name = model_name or settings.GEMINI_MODEL
        self.timeout = settings.GEMINI_TIMEOUT_SECONDS
        self._client = None
        self._initialized = False

    @property
    def api_key(self) -> str:
        if self._explicit_key is not None:
            return self._explicit_key
        return settings.GEMINI_API_KEY or ""

    def get_client(self):
        """Retrieve the configured genai.Client or None."""
        if self._client is not None:
            return self._client
        key = self.api_key.strip()
        if key:
            try:
                from google import genai
                self._client = genai.Client(api_key=key)
                self._initialized = True
                return self._client
            except Exception as e:
                logger.warning(f"Failed to create Google GenAI client: {type(e).__name__}")
                return None
        return None

    @property
    def is_available(self) -> bool:
        """Indicates whether Gemini API client is actively configured."""
        return self.get_client() is not None

    def triage_ticket(
        self,
        subject: str,
        description: str,
        author_name: Optional[str] = None,
        book_title: Optional[str] = None,
        book_isbn: Optional[str] = None,
    ) -> AiTriageResult:
        """
        Classifies ticket into exactly one approved category and priority score.
        If Gemini is unconfigured or fails, applies safe deterministic fallback.
        """
        now_iso = datetime.now(timezone.utc).isoformat()
        client = self.get_client()

        if client is None:
            return self._heuristic_triage(
                subject=subject,
                description=description,
                status="unavailable",
                reason="Gemini API key not configured. Deterministic fallback applied.",
            )

        prompt = self._build_triage_prompt(
            subject=subject,
            description=description,
            author_name=author_name,
            book_title=book_title,
            book_isbn=book_isbn,
        )

        try:
            from google.genai import types

            config = types.GenerateContentConfig(
                temperature=0.1,
                response_mime_type="application/json",
                response_schema=AiTriageOutput,
            )

            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config,
            )

            if hasattr(response, "parsed") and response.parsed is not None:
                parsed_output = response.parsed
                if isinstance(parsed_output, dict):
                    parsed_output = AiTriageOutput.model_validate(parsed_output)
            else:
                raw_text = response.text if hasattr(response, "text") else str(response)
                parsed_output = self._parse_json_safely(raw_text, AiTriageOutput)

            norm_cat = normalize_category(parsed_output.category)
            norm_pri = normalize_priority(parsed_output.priority)
            pri_code = PRIORITY_CODE_MAP.get(norm_pri, "MEDIUM")

            policies = parsed_output.applicable_policies or find_relevant_policies(norm_cat)

            return AiTriageResult(
                category=norm_cat,
                priority=norm_pri,
                priority_code=pri_code,
                confidence=round(parsed_output.confidence, 2),
                reasoning=parsed_output.reasoning.strip(),
                status="success",
                model=self.model_name,
                provider=self.model_name,
                applicable_policies=policies,
                created_at=now_iso,
            )

        except Exception as e:
            logger.warning(f"Gemini triage call failed ({type(e).__name__}): {e}. Applying safe fallback.")
            err_str = str(e)
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "quota" in err_str.lower():
                user_friendly_error = "Gemini Free Tier Quota Exceeded (20 requests/day limit reached). Deterministic fallback applied."
            elif "API_KEY_INVALID" in err_str or "401" in err_str or "403" in err_str:
                user_friendly_error = "Gemini API Key invalid or expired. Deterministic fallback applied."
            else:
                user_friendly_error = f"AI provider call encountered an issue ({type(e).__name__}). Safe fallback applied."

            return self._heuristic_triage(
                subject=subject,
                description=description,
                status="fallback",
                reason=user_friendly_error,
                error_message=user_friendly_error,
            )

    def generate_draft_response(
        self,
        ticket_subject: Optional[str] = None,
        ticket_description: Optional[str] = None,
        ticket_category: Optional[str] = None,
        ticket_priority: Optional[str] = None,
        author_name: str = "Author",
        author_email: Optional[str] = None,
        author_city: Optional[str] = None,
        book_title: Optional[str] = None,
        book_isbn: Optional[str] = None,
        book_status: Optional[str] = None,
        existing_messages: Optional[List[Dict[str, Any]]] = None,
        # Direct aliases for flexible testing / caller signatures
        ticket_id: Optional[str] = None,
        subject: Optional[str] = None,
        description: Optional[str] = None,
        category: Optional[str] = None,
        priority: Optional[str] = None,
        author_context: Optional[Dict[str, Any]] = None,
        book_context: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> AiDraftResult:
        """
        Generates an empathetic, policy-accurate author response draft for admin review.
        Incorporates relevant BookLeaf knowledge base policies and known database context.
        """
        now_iso = datetime.now(timezone.utc).isoformat()

        # Resolve aliases
        subj = (ticket_subject or subject or "Author Support Request").strip()
        desc = (ticket_description or description or "").strip()
        cat = ticket_category or category or "General Inquiry"
        pri = ticket_priority or priority or "Medium"

        if author_context:
            author_name = author_context.get("name") or author_name
            author_email = author_context.get("email") or author_email
            author_city = author_context.get("city") or author_city

        if book_context:
            book_title = book_context.get("title") or book_title
            book_isbn = book_context.get("isbn") or book_isbn
            book_status = book_context.get("status") or book_status

        client = self.get_client()

        if client is None:
            return AiDraftResult(
                draft_response="",
                suggested_category=normalize_category(cat),
                suggested_priority=normalize_priority(pri),
                priority_code=PRIORITY_CODE_MAP.get(normalize_priority(pri), "MEDIUM"),
                confidence=0.0,
                reasoning="Gemini API key is not configured on the backend.",
                relevant_policies=[],
                status="unavailable",
                model=self.model_name,
                error_message="Gemini API is not configured. Please set GEMINI_API_KEY in the backend environment to enable automated drafting.",
                created_at=now_iso,
            )

        # Retrieve focused knowledge base slice
        norm_cat = normalize_category(cat)
        knowledge_context = get_relevant_knowledge(norm_cat, f"{subj} {desc}")

        prompt = self._build_draft_prompt(
            subject=subj,
            description=desc,
            category=norm_cat,
            priority=pri,
            author_name=author_name,
            author_email=author_email,
            author_city=author_city,
            book_title=book_title,
            book_isbn=book_isbn,
            book_status=book_status,
            knowledge_context=knowledge_context,
            existing_messages=existing_messages or [],
        )

        try:
            from google.genai import types

            config = types.GenerateContentConfig(
                temperature=0.3,
                response_mime_type="application/json",
                response_schema=AiDraftOutput,
            )

            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config,
            )

            if hasattr(response, "parsed") and response.parsed is not None:
                parsed_output = response.parsed
                if isinstance(parsed_output, dict):
                    parsed_output = AiDraftOutput.model_validate(parsed_output)
            else:
                raw_text = response.text if hasattr(response, "text") else str(response)
                parsed_output = self._parse_json_safely(raw_text, AiDraftOutput)

            sug_cat = normalize_category(parsed_output.suggested_category)
            sug_pri = normalize_priority(parsed_output.suggested_priority)
            pri_code = PRIORITY_CODE_MAP.get(sug_pri, "MEDIUM")

            return AiDraftResult(
                draft_response=parsed_output.draft_response.strip(),
                suggested_category=sug_cat,
                suggested_priority=sug_pri,
                priority_code=pri_code,
                confidence=round(parsed_output.confidence, 2),
                reasoning=parsed_output.reasoning.strip(),
                relevant_policies=parsed_output.relevant_policies or find_relevant_policies(sug_cat),
                status="success",
                model=self.model_name,
                created_at=now_iso,
            )

        except Exception as e:
            sanitized_msg = str(e)
            if self.api_key and self.api_key in sanitized_msg:
                sanitized_msg = sanitized_msg.replace(self.api_key, "[REDACTED]")

            logger.error(f"Gemini draft generation error: {sanitized_msg}")

            return AiDraftResult(
                draft_response="",
                suggested_category=normalize_category(cat),
                suggested_priority=normalize_priority(pri),
                priority_code=PRIORITY_CODE_MAP.get(normalize_priority(pri), "MEDIUM"),
                confidence=0.0,
                reasoning="AI draft generation encountered a provider or network timeout.",
                relevant_policies=[],
                status="error",
                model=self.model_name,
                error_message=f"Draft generation temporarily unavailable ({type(e).__name__}): {sanitized_msg}. Please write a manual response.",
                created_at=now_iso,
            )

    # -------------------------------------------------------------------------
    # Helper & Prompt Methods
    # -------------------------------------------------------------------------

    def _build_triage_prompt(
        self,
        subject: str,
        description: str,
        author_name: Optional[str],
        book_title: Optional[str],
        book_isbn: Optional[str],
    ) -> str:
        return f"""You are the BookLeaf Publishing Support Triage Copilot.
Your mission is to categorize and prioritize the author's inquiry accurately.

APPROVED CATEGORIES (Choose EXACTLY ONE):
- Royalty & Payments: Payouts, minimum ₹1,000 threshold, 80/20 profit split, quarterly reconciliation, tax slips.
- ISBN & Metadata Issues: Book title, author name, blurb, pricing update, barcode or ISBN mismatch.
- Printing & Quality: Manufacturing defects, cover alignment, page defects, binding issues, proof orders (5-7 day SLA).
- Distribution & Availability: Retail channels (Amazon, Flipkart, BookLeaf Direct), stock out resync (24-48h), listing turnaround (7-10 days).
- Book Status & Production Updates: Manuscript status, editing stage, proofreading signoff, publishing milestones.
- General Inquiry: Routine author queries, account contact updates, general questions.

APPROVED PRIORITIES (Choose EXACTLY ONE):
- Critical: Urgent financial delays (>₹10,000, >45 day SLA missed), live ISBN mismatch on retail sites, severe whole-batch print defect.
- High: Missing royalty payout above threshold, print defect on author copies requiring reprint, retail channel outage past 10 days.
- Medium: Standard production milestone questions, blurb/price metadata updates (3-5 day SLA), general royalty schedule queries.
- Low: Routine general questions, address updates, compliment or feedback.

TICKET DETAILS:
- Author: {author_name or 'Author'}
- Associated Book: {book_title or 'General (No Book Attached)'} (ISBN: {book_isbn or 'N/A'})
- Subject: {subject}
- Description: {description}

Produce a structured JSON response matching the schema with category, priority, confidence (0.0 to 1.0), and reasoning.
"""

    def _build_draft_prompt(
        self,
        subject: str,
        description: str,
        category: str,
        priority: str,
        author_name: str,
        author_email: Optional[str],
        author_city: Optional[str],
        book_title: Optional[str],
        book_isbn: Optional[str],
        book_status: Optional[str],
        knowledge_context: str,
        existing_messages: List[Dict[str, Any]],
    ) -> str:
        recent_history = ""
        if existing_messages:
            history_lines = []
            # Anchored Window: If thread is long (> 10 messages), preserve Message #1 as anchor + last 9 messages
            if len(existing_messages) > 10:
                first_msg = existing_messages[0]
                first_sender = f"Author ({author_name})" if first_msg.get("sender_type") == "AUTHOR" else "BookLeaf Support Staff"
                history_lines.append(f"[{first_sender} - Initial Inquiry]: {first_msg.get('message_body', '').strip()}")
                history_lines.append(f"... [{len(existing_messages) - 9} intermediate messages omitted for focus] ...")
                recent_slice = existing_messages[-9:]
            else:
                recent_slice = existing_messages

            for m in recent_slice:
                sender_role = f"Author ({author_name})" if m.get("sender_type") == "AUTHOR" else "BookLeaf Support Staff"
                body = m.get("message_body", "").strip()
                history_lines.append(f"[{sender_role}]: {body}")
            recent_history = f"\nCONVERSATION THREAD (Chronological):\n" + "\n".join(history_lines)

        return f"""You are the senior editorial support specialist at BookLeaf Publishing.
Draft an empathetic, professional, and policy-accurate reply to author '{author_name}'.

{knowledge_context}

AUTHOR & TICKET CONTEXT:
- Author: {author_name} ({author_email or 'Verified Author'}) - Location: {author_city or 'India'}
- Book: {book_title or 'General / Account Level'} (ISBN: {book_isbn or 'Pending'}, Status: {book_status or 'N/A'})
- Ticket Subject: {subject}
- Author Inquiry: {description}
- Current Category: {category}
- Priority: {priority}
{recent_history}

STRICT INSTRUCTIONS:
1. Greet the author warmly: 'Dear {author_name},'
2. Directly answer their query using the specific BookLeaf policies in the knowledge base snippet.
3. If they inquire about royalties, mention the 80/20 net profit split and the 45-day post-quarter payout timeline.
4. If they report a print defect, explain that BookLeaf guarantees craftsmanship and offers free replacement reprints upon verifying defect photos and delivery details.
5. If they report a retail listing being out of stock, explain the 24-48h automated distributor stock resync.
6. Do NOT fabricate transaction reference numbers, dates of bank transfers, or unverified claims.
7. Outline specific next steps and realistic turnaround times.
8. Sign off professionally as 'Warm regards,\nBookLeaf Author Support Team'.

Produce a structured JSON response adhering to the AiDraftOutput schema.
"""

    def _parse_json_safely(self, raw_text: str, schema_cls):
        """Extract and validate JSON against Pydantic schema with fence stripping."""
        cleaned = raw_text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[len("```json"):].strip()
        elif cleaned.startswith("```"):
            cleaned = cleaned[len("```"):].strip()
        if cleaned.endswith("```"):
            cleaned = cleaned[:-len("```")].strip()

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as err:
            logger.warning(f"JSON decode error: {err}. Raw content: {cleaned[:100]}...")
            raise ValueError(f"Model did not return valid JSON: {err}")

        return schema_cls.model_validate(data)

    def _heuristic_triage(
        self,
        subject: str,
        description: str,
        status: str = "fallback",
        reason: str = "Deterministic fallback",
        error_message: Optional[str] = None,
    ) -> AiTriageResult:
        """Deterministic keyword-based classification when Gemini is unavailable."""
        combined = f"{subject} {description}".lower()

        # Category heuristics
        if any(w in combined for w in ["royalty", "payment", "payout", "earnings", "profit", "inr", "bank account", "neft"]):
            cat = "Royalty & Payments"
        elif any(w in combined for w in ["isbn", "barcode", "metadata", "blurb", "synopsis", "bio", "title mismatch"]):
            cat = "ISBN & Metadata Issues"
        elif any(w in combined for w in ["defect", "print", "cover", "binding", "misaligned", "pages", "paper", "quality", "damaged", "smudge"]):
            cat = "Printing & Quality"
        elif any(w in combined for w in ["amazon", "flipkart", "out of stock", "distribution", "listing", "retail", "unavailable"]):
            cat = "Distribution & Availability"
        elif any(w in combined for w in ["status", "typesetting", "proof", "manuscript", "progress", "publication date", "milestone"]):
            cat = "Book Status & Production Updates"
        else:
            cat = "General Inquiry"

        # Priority heuristics
        if any(w in combined for w in ["urgent", "critical", "emergency", "wrong isbn", "severe defect", "unauthorized", "legal"]):
            pri = "Critical"
        elif any(w in combined for w in ["missing payout", "not received", "unpaid", "delay", "delayed", "reprint", "not available", "error", "defect", "fail", "mismatch"]):
            pri = "High"
        elif any(w in combined for w in ["compliment", "thanks", "kudos", "minor feedback", "suggestion"]):
            pri = "Low"
        else:
            pri = "Medium"

        policies = find_relevant_policies(cat)
        clean_reasoning = f"Matched operational keywords for '{cat}' category based on ticket inquiry."

        return AiTriageResult(
            category=cat,
            priority=pri,
            priority_code=PRIORITY_CODE_MAP[pri],
            confidence=0.70,
            reasoning=clean_reasoning,
            status=status,
            model="heuristic-fallback",
            provider="heuristic-fallback",
            applicable_policies=policies,
            error_message=error_message or (reason if status in ("fallback", "unavailable") else None),
            created_at=datetime.now(timezone.utc).isoformat(),
        )


# Singleton instance
ai_service = GeminiService()
