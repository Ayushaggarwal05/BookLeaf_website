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

### 2.2 Two-Tier AI Governance: Deterministic Ingestion vs. Heavy AI Processing
- **Decision:** Multi-tier architectural split. Ticket creation operates under **Tier 1 (Zero-Cost Rule Ingestion)** using regex/keyword heuristics ($0 cost, sub-millisecond latency, zero external API dependency). Deep LLM reasoning (`gemini-2.5-flash`) is deferred to **Tier 2 (On-Demand Admin Operations)**.
- **Trade-off:** Tickets do not receive Gemini's deep contextual reasoning immediately upon author creation.
- **Benefit & Mitigation:** Eliminates vulnerability to bot spam, denial-of-service quota exhaustion, and runaway API expenses on public/author-facing form submissions. When an authenticated administrator opens the ticket, they can invoke Gemini LLM reasoning and grounded draft generation with an explicit click.

### 2.3 On-Demand Draft Generation & Anchored Conversation Window
- **Decision:** Response drafting is triggered **on-demand** by an administrator click rather than pre-generated eagerly for every ticket submission, and leverages an **Anchored Conversation Window** (first initial author inquiry + latest 9 messages).
- **Trade-off:** The admin must wait ~1–2 seconds when clicking "Generate AI Response Draft" on a ticket.
- **Benefit:** Eliminates 80%+ of unnecessary LLM API costs for tickets that admins answer immediately, and avoids running drafts on tickets that are closed or reassigned. The Anchored Window prevents context dilution (never forgetting the core issue) without paying token overhead for lengthy intermediate back-and-forths.

### 2.4 Hybrid Storage (SQLite Dev / PostgreSQL Production)
- **Decision:** Dual-compatible SQLAlchemy models supporting SQLite for frictionless local development and PostgreSQL for scalable production.
- **Trade-off:** SQLite lacks native JSON and sequence types present in Postgres.
- **Mitigation:** SQLite foreign keys are explicitly enforced via connection PRAGMAs (`PRAGMA foreign_keys=ON`). JSON metadata is serialized consistently across both engines, and Alembic migrations target universal SQL types.

### 2.5 Real-Time Synchronization: Heartbeat Polling vs. WebSockets
- **Decision:** Implemented client-side short-polling (10-second conversation heartbeat, 15-second queue refresh) backed by optimistic UI updates.
- **Trade-off:** Slightly higher HTTP request count compared to an open, persistent bidirectional TCP socket stream.
- **Rationale & Resilience:** 
  - Free-tier hosted web services (like Render) spin down or recycle worker dynos during inactive periods, which forcibly severs persistent WebSocket connections and causes high reconnect churn.
  - Short polling is stateless, HTTP/2 multiplexed, and immune to mobile sleep/wake connection drops.
  - For support ticket conversations, a 10-second polling cadence provides near-instantaneous perceived responsiveness with zero stateful connection management overhead on the server.

### 2.6 Cloud Routing: Supabase IPv4 Connection Pooler vs. Direct IPv6
- **Decision:** Routed production PostgreSQL traffic through Supabase's transaction pooler (`aws-0-ap-south-1.pooler.supabase.com:5432`) rather than direct endpoint `db.[REF].supabase.co`.
- **Trade-off:** Adds a single intermediate pooling hop via PgBouncer.
- **Rationale:** Direct Supabase endpoints resolve exclusively to IPv6 addresses in certain AWS regions. Because free-tier Render and common Linux container runtimes lack native dual-stack IPv6 egress routing (`Network is unreachable`), utilizing the dedicated IPv4 pooler ensures guaranteed network reachability and connection persistence across global container boundaries.

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
