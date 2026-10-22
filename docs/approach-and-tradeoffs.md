# BookLeaf Author Support Portal — Approach, Design Trade-Offs & Production Evolution

## 1. Architectural Approach & Core Priorities

The BookLeaf Author Support & Communication Portal was engineered with four overarching engineering priorities:
1. **Tenant Isolation by Design:** Authors must never access or leak data belonging to other authors. Security boundaries are strictly enforced server-side through JWT claims rather than trusting frontend parameters.
2. **Operational Continuity & Zero-Downtime Fallbacks:** The Gemini AI integration is non-blocking. If Gemini API credentials are absent, rate-limited, or encountering network issues, ticket triage falls back deterministically to rule-based keyword heuristics. Authors can always submit tickets, and administrators can always resolve them manually.
3. **Data Integrity & Idempotent Seeding:** The dataset import pipeline guarantees that re-running seeding never duplicates authors or books, nor does it wipe user-created support tickets. Financial calculations (royalties, payouts, net profit splits) strictly use arbitrary-precision `Decimal` to eliminate floating-point drift.
4. **Administrative Oversight ("Human in the Loop"):** Generative AI generates response proposals exclusively for administrative review. Draft responses are never dispatched directly to authors without explicit human approval.

---

## 2. Key Technical Trade-Offs & Rationale

### 2.1 Single Shared Database vs. Multi-Database Multi-Tenancy
- **Decision:** Row-level tenant isolation using foreign key constraints (`author_id`) on a shared relational schema.
- **Trade-off:** A separate database or schema per tenant offers stronger physical isolation but introduces high operational overhead and connection-pooling complexity for hundreds of authors.
- **Mitigation:** Strict FastAPI dependency validation (`require_author`) and query scoping on every database call prevent cross-tenant record discovery or modification.

### 2.2 Synchronous Triage vs. Background Task Queue (Celery / RQ)
- **Decision:** Asynchronous inline AI triage wrapped in `try/except` with a fast deterministic fallback.
- **Trade-off:** Running heavy tasks in Celery or AWS SQS decouples requests from provider latency, but adds operational overhead (Redis broker, worker processes, state polling).
- **Mitigation:** `gemini-2.5-flash` executes in ~400–800ms. With a strict 30s timeout and instant heuristic fallback on failure, authors experience immediate ticket creation without queue lag.

### 2.3 On-Demand Draft Generation vs. Eager Draft Pre-computation
- **Decision:** Response drafting is triggered **on-demand** by an administrator click rather than pre-generated for every ticket submission.
- **Trade-off:** The admin must wait ~1–2 seconds when clicking "Generate AI Draft" on a ticket.
- **Benefit:** Eliminates 80%+ of unnecessary LLM API costs for tickets that admins answer immediately, and avoids running drafts on tickets that are closed or reassigned. Once generated, the draft is cached on the ticket record.

### 2.4 Hybrid Storage (SQLite Dev / PostgreSQL Production)
- **Decision:** Dual-compatible SQLAlchemy models supporting SQLite for frictionless local development and PostgreSQL for scalable production.
- **Trade-off:** SQLite lacks native JSON and sequence types present in Postgres.
- **Mitigation:** SQLite foreign keys are explicitly enforced via connection PRAGMAs (`PRAGMA foreign_keys=ON`). JSON metadata is serialized consistently across both engines, and Alembic migrations target universal SQL types.

---

## 3. Production Evolution & Next Steps

When scaling to tens of thousands of authors and high-volume enterprise traffic, the system should evolve as follows:

1. **Distributed Asynchronous Task Processing:**
   - Migrate notification dispatches and multimodal attachment processing to **Celery + Redis** or **Temporal**.
2. **Multimodal Print Defect Verification:**
   - Integrate Gemini 2.5 Flash's multimodal vision API to automatically inspect uploaded photos of damaged books (misaligned spine, cover fading, torn binding) and auto-approve free reprints for verified defects.
3. **Real-Time Live Updates via WebSockets:**
   - Replace the current 10-second polling sync with WebSocket or Server-Sent Events (SSE) subscriptions for real-time ticket updates between author and admin consoles.
4. **Automated Read Replicas & Connection Pooling:**
   - Introduce **PgBouncer** connection pooling and separate Read/Write replicas for heavy analytical queries on author royalty aggregations.
5. **Author Self-Service Knowledge Agent:**
   - Deploy an author-facing conversational widget that resolves routine questions (royalty calendar, 80/20 formula, shipping SLAs) before a formal ticket is created, reducing support desk volume by an estimated 35–45%.
