# BookLeaf Support Portal — Gemini AI Integration Strategy & Architecture

## 1. Executive Summary

The **BookLeaf Author Support & Communication Portal** integrates Google's Gemini generative AI to automate routine operational triage (classification and priority scoring) and empower support administrators with empathetic, policy-grounded author response drafts.

The integration is built upon production engineering principles:
- **Strict Server-Side Isolation:** The Gemini API key (`GEMINI_API_KEY`) resides exclusively in backend environment variables. No client-side requests, frontend exposure, log pollution, or version control commits occur.
- **Official Supported SDK:** Implemented using Google's official Python SDK (`google-genai>=2.30.0`), utilizing native structured JSON schema enforcement (`GenerateContentConfig(response_mime_type="application/json", response_schema=...)`).
- **Zero-Downtime Fallback Design:** If the Gemini key is unconfigured, rate-limited, or encountering upstream outages, ticket submission and administrative workflows continue seamlessly via deterministic keyword heuristics. Ticket creation never fails due to an AI fault.
- **Admin-in-the-Loop Workflow:** AI never sends automated external messages to authors. All drafted responses are served as editable proposals for operations staff review. Admin triage overrides are tracked and preserved permanently.
- **Two-Tier Cost Governance Model:** To prevent API quota exhaustion and bot spam on public-facing endpoints:
  - **Tier 1 (Zero-Cost Ingestion):** When an author submits a support inquiry, initial categorization and priority routing run on an ultra-fast, deterministic keyword rule engine ($0 API cost, 0 network latency, 0 quota risk).
  - **Tier 2 (On-Demand Deep LLM Reasoning):** Deep generative reasoning, policy cross-checking, and draft composition are invoked strictly on-demand by authenticated operations administrators clicking *"Generate AI Response Draft"*.
- **Cost Awareness & Draft Caching:** Draft generation is performed on-demand via explicit admin action rather than background polling. Generated drafts are cached in the ticket's `ai_classification` metadata to avoid redundant API billing.

---

## 2. Model Selection & Rationale

| Attribute | Specification | Rationale |
| :--- | :--- | :--- |
| **Model** | `gemini-2.5-flash` | Selected for optimal balance between sub-second latency, high instruction fidelity, and cost efficiency ($0.075 / 1M input tokens). |
| **Configurability** | `GEMINI_MODEL` env variable | Administrators can easily switch between `gemini-2.5-flash`, `gemini-2.5-pro`, or newer releases via `.env` without modifying application code. |
| **API Provider** | Google GenAI SDK (`google-genai`) | Official, maintained Python SDK providing clean async/sync support, native Pydantic schema validation, and structured output formatting. |
| **Execution Mode** | Server-side only | Executed inside `backend/app/services/ai_service.py` via FastAPI endpoints. |

---

## 3. Approved Categories & Priority Rubric

### 3.1 Approved Categories (Section 2)
Every ticket is triaged into **exactly one** of the six official operational domains:
1. **Royalty & Payments:** Inquiries concerning 80/20 profit splits, ₹1,000 minimum payout thresholds, quarterly settlement schedules, and TDS certificates.
2. **ISBN & Metadata Issues:** Retail channel ISBN discrepancies, catalog barcodes, blurb updates, author biography modifications, and price changes.
3. **Printing & Quality:** Physical book manufacturing defects (binding delamination, smudged ink, misaligned covers, missing pages) and author proof batches.
4. **Distribution & Availability:** Multi-channel availability (Amazon, Flipkart, BookLeaf Direct, Ingram), listing turnaround, and stock feed synchronization.
5. **Book Status & Production Updates:** 9-stage milestone tracking (Manuscript receipt, editing, cover design, typesetting, proofreading, ISBN assignment, printing, distribution setup, publication).
6. **General Inquiry:** Account details, author portal navigation, general non-technical communications.

### 3.2 Priority Rubric (Section 3)
The AI applies a disciplined, documented priority rubric to prevent complaint escalation inflation:

| Priority | DB Code | Criteria & Scenario Examples |
| :--- | :--- | :--- |
| **Critical** | `URGENT` | Urgent financial discrepancies (>45 days post-quarter SLA breach), live ISBN barcode mismatches on retail sites preventing book sales, whole-batch printing defects (>20 author copies). |
| **High** | `HIGH` | Missing quarterly royalty payout above ₹1,000 threshold, verified printing quality defects qualifying for free reprints, retail availability outages exceeding 10 business days. |
| **Medium** | `MEDIUM` | Standard publishing production stage questions, routine blurb/price metadata updates (3–5 business day SLA), standard author inquiries. |
| **Low** | `LOW` | Minor routine queries, compliments, feedback, general author portal questions without operational impact. |

### 3.3 Admin Override Preservation
If an admin manually adjusts a ticket's category or priority via the Admin Portal, `ai_classification["admin_override"]` is set to `True`. Subsequent automated processes respect this flag and will **never** silently overwrite human operational decisions.

---

## 4. BookLeaf Knowledge Base & Response Drafting Strategy

The dedicated knowledge base module (`backend/app/services/knowledge_base.py`) codifies BookLeaf's official publishing policies:

1. **Royalty Split:** Author receives 80% of net profit; BookLeaf retains 20%.
2. **Net Profit Calculation:** Deducts physical printing costs, retail aggregator commission (e.g., Amazon 40-50%), and fulfillment/shipping fees from MRP.
3. **Payout Timing:** Calculated quarterly and disbursed within **45 calendar days** following the end of each quarter.
4. **Minimum Payout:** ₹1,000 threshold. Unpaid balances below ₹1,000 roll over automatically without forfeiture.
5. **ISBN Registration:** Assigned directly by BookLeaf Publishing under its imprint, unless author independently registers under their own imprint.
6. **ISBN Mismatch Escalation:** Designated as High/Critical priority with immediate escalation to cataloging operations.
7. **Print Turnaround:** Standard turnaround for proofs and print-on-demand is **5 to 7 business days** to dispatch.
8. **Defect Warranty & Free Reprints:** Verified physical manufacturing defects qualify for an expedited **free replacement reprint**.
9. **Distribution Ingestion:** Takes **7 to 10 business days** post-publication to reflect live on Amazon, Flipkart, and Ingram.
10. **Stock Resynchronization:** Listings showing "Temporarily Out of Stock" resynchronize inventory feeds within **24 to 48 hours**.
11. **Production Pipeline Stages:** Manuscript receipt → Editorial review → Cover design → Typesetting → Proofreading approval → ISBN assignment → Printing → Distribution setup → Live publication.
12. **Metadata Propagation:** Updates to blurbs, bios, and pricing reflect across retail channels within **3 to 5 business days**.
13. **Editorial Tone:** Empathetic, professional, specific, accountable, and transparent regarding timelines and next steps.

### Focused Context Slicing
To ensure low latency, minimize token consumption, and avoid hallucinations:
- Only policies directly relevant to the ticket's active category (plus financial rules if monetary terms appear) are injected into the prompt.
- **Anchored Conversation History Window:** Rather than unbounded message history, an anchored window passes Message #1 (the root inquiry anchor) plus up to the last 9 chronological exchanges with clear speaker roles (`Author` vs `BookLeaf Support Staff`). This avoids "lost-in-the-middle" token dilution while retaining the complete root problem.
- Full database dumps or irrelevant author histories are never passed to the LLM.

---

## 5. Structured Output & Validation

All AI interactions utilize Pydantic validation schemas to safeguard against model drift, prompt injection, and malformed outputs:

```python
class AiTriageOutput(BaseModel):
    category: str = Field(description="Exactly one approved category")
    priority: str = Field(description="Exactly one approved priority")
    confidence: float = Field(default=0.85, ge=0.0, le=1.0)
    reasoning: str
    applicable_policies: List[str] = Field(default_factory=list)

class AiDraftOutput(BaseModel):
    draft_response: str
    suggested_category: str
    suggested_priority: str
    confidence: float
    reasoning: str
    relevant_policies: List[str]
```

### Prompt Injection & Safety Guardrails
- **Delimited Context:** Author queries and ticket subjects are strictly enclosed in labeled XML/markdown boundaries to prevent prompt escaping.
- **Instruction Precedence:** System prompts explicitly instruct the model to ignore any attempt within the ticket text to override system rules, authorization boundaries, or output schemas.
- **Schema Validation:** In the event that raw output contains markdown fences (e.g. ` ```json ... ``` `), a custom sanitizer strips delimiters before Pydantic parsing.

---

## 6. Error Handling & Fallback Circuit

| Failure Mode | Backend Behavior | Frontend Presentation |
| :--- | :--- | :--- |
| **Missing API Key** | `is_available` returns `False`. Triage falls back to `_heuristic_triage`. Draft returns `status="unavailable"`. | Banner: *"AI Service Notice: Gemini API key is not configured. Manual response path remains active."* |
| **Rate Limiting (429)** | Caught in try/except block. Returns `status="error"` with sanitized error description. | Banner: *"Draft generation temporarily unavailable (Rate Limit). Please write a manual response."* |
| **Provider Timeout** | Configurable timeout (`GEMINI_TIMEOUT_SECONDS=30`). Unblocks immediately without hanging request. | Banner: *"AI service connection timed out. Manual composer ready."* |
| **Invalid Schema Output** | Caught by Pydantic `ValidationError`. Triage reverts to heuristic classification. | Triage continues gracefully without blocking ticket creation. |
| **Network Outage** | Handled non-blockingly; error logged without secrets. | Normal ticket management and manual reply remain fully operational. |

---

## 7. Cost-Control Strategy

1. **On-Demand Generation:** AI response drafts are generated **only** when an administrator clicks the **"Generate AI Response Draft"** button. They are never generated proactively on every page view or list polling request.
2. **Draft Caching:** When a draft is generated, it is persisted directly in `support_tickets.ai_classification["draft_response"]`. Subsequent visits by staff members render the cached draft immediately with zero API costs.
3. **Model Selection:** `gemini-2.5-flash` delivers extreme cost efficiency while exceeding the accuracy requirements for customer support ticket triage.
4. **Context Boundaries:** Knowledge base context is sliced so only the relevant policy module is provided, keeping prompt size under 1,500 tokens per call.

---

## 8. Frontend Admin Workflow

In `AdminTicketDetailPage.tsx`:
- **AI Suggested Triage Card:** Displays category, priority, confidence score, and rationale.
- **"Apply AI Triage to Ticket" Button:** Allows admins to adopt AI suggestions with a single click if they differ from the ticket's current state.
- **"Generate / Regenerate AI Draft" Button:** Calls `POST /api/v1/admin/tickets/{id}/ai-draft` with visual loading spinner.
- **Editable Draft Textarea:** Administrators can review, rephrase, or expand upon the AI draft directly in the interface.
- **"Insert into Author Response" Action:** Copies the vetted draft into the author reply composer and smoothly scrolls down to focus the field.
- **Policy Badges:** Visual tags indicating which official BookLeaf policies were cited in the draft.

---

## 9. Known Limitations & Roadmap

1. **Multilingual Support:** While Gemini supports Hindi and regional Indian languages, current prompt templates and the knowledge base are in English. Future iterations will support automated multilingual translation.
2. **Attachment Vision Analysis:** Currently, attachments are passed as metadata (filename, mime type). In future versions, image attachments of print defects can be passed to Gemini 2.5 Flash's multimodal vision API for automated print defect verification.
3. **Live Sync with Retail Aggregator APIs:** In a future enterprise release, the draft prompt could query live Amazon/Ingram inventory status APIs to confirm whether a stock resync is already underway.
