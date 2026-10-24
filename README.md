# BookLeaf Author Support & Communication Portal

Production-minded full-stack support and publishing portal for authors and support operations staff at **BookLeaf Publishing**. Built with **FastAPI**, **SQLAlchemy 2.0**, **PostgreSQL (Supabase)**, **React 19**, **TypeScript**, **Vite**, **Tailwind CSS**, and **Google Gemini 2.5 Flash**.

---

## 🚀 Live Production Deployments

| Component | Platform | Live URL | Status |
| :--- | :--- | :--- | :--- |
| **Frontend Portal** | Vercel Global Edge | [https://book-leaf-website-five.vercel.app](https://book-leaf-website-five.vercel.app) | ✅ Live & Connected |
| **Backend REST API** | Render Web Service | [https://bookleaf-backend-dcy8.onrender.com](https://bookleaf-backend-dcy8.onrender.com) | ✅ Healthy (HTTP 200) |
| **Interactive API Docs** | Render Swagger UI | [https://bookleaf-backend-dcy8.onrender.com/docs](https://bookleaf-backend-dcy8.onrender.com/docs) | ✅ Live |
| **Health Check Endpoint** | FastAPI `/health` | [https://bookleaf-backend-dcy8.onrender.com/health](https://bookleaf-backend-dcy8.onrender.com/health) | ✅ PostgreSQL Connected |
| **Cloud Database** | Supabase PostgreSQL | `aws-0-ap-south-1.pooler.supabase.com:5432` | ✅ Seeded & Migrated |

### 🔑 Demo Accounts for Evaluation

All author accounts use the shared test password: `Author@BookLeaf2026!`

| Role | Email | Password | Access & Capabilities |
| :--- | :--- | :--- | :--- |
| **Operations Admin** | `admin@bookleaf.in` | `Admin@BookLeaf2026!` | Cross-author triage queues, Gemini AI response drafting & triage, private internal staff notes |
| **Author (Priya Sharma)** | `priya.sharma@email.com` | `Author@BookLeaf2026!` | Book catalog (3 titles), royalty ledger, ticket submissions & conversations |
| **Author (Rohit Kapoor)** | `rohit.kapoor@email.com` | `Author@BookLeaf2026!` | Book catalog (2 titles), royalty ledger, ticket submissions & conversations |
| **Author (Ananya Reddy)** | `ananya.reddy@email.com` | `Author@BookLeaf2026!` | Book catalog (1 title), royalty ledger, ticket submissions & conversations |
| **Author (Vikram Joshi)** | `vikram.joshi@email.com` | `Author@BookLeaf2026!` | Book catalog (2 titles), royalty ledger, ticket submissions & conversations |
| **Author (Sneha Kulkarni)** | `sneha.kulkarni@email.com` | `Author@BookLeaf2026!` | Book catalog (3 titles), royalty ledger, ticket submissions & conversations |
| **Author (Diya Chatterjee)** | `diya.chatterjee@email.com` | `Author@BookLeaf2026!` | Book catalog (2 titles), royalty ledger, ticket submissions & conversations |

---

## 🏗️ Project Architecture & Structure

```
bookleaf-support-portal/
├── backend/
│   ├── alembic.ini                   # Alembic database migration configuration
│   ├── build.sh                      # Cloud deployment build script
│   ├── requirements.txt              # Production and testing Python dependencies
│   ├── seed.py                       # CLI runner for database seeding & demo accounts
│   ├── app/
│   │   ├── main.py                   # FastAPI app factory, CORS, and lifecycles
│   │   ├── core/
│   │   │   ├── config.py             # Environment settings & validation (Pydantic v2)
│   │   │   ├── database.py           # SQLAlchemy 2.x engine, connection pooler, SQLite PRAGMA hook
│   │   │   ├── dependencies.py       # RBAC auth middlewares (require_author, require_admin)
│   │   │   └── security.py           # Bcrypt hashing and JWT token issuance
│   │   ├── models/                   # Declarative ORM models (Author, Book, Ticket, Note, User)
│   │   ├── schemas/                  # Pydantic v2 validation and serialization schemas
│   │   ├── api/
│   │   │   └── routes/               # Modular API routers (/health, /auth, /author, /admin)
│   │   ├── repositories/             # Data access layer
│   │   └── services/                 # Business logic, Gemini AI copilot, and knowledge base
│   ├── migrations/                   # Alembic migration scripts
│   └── tests/                        # Full pytest suite (53 automated tests)
├── data/
│   └── bookleaf_sample_data.json     # Official assignment sample dataset (10 authors, 18 books)
├── docs/
│   ├── architecture.md               # Technical architecture, live cloud topology & ERD
│   ├── api.md                        # REST API endpoint reference
│   ├── ai-strategy.md                # Gemini AI triage & prompt engineering design
│   └── approach-and-tradeoffs.md     # Architectural priorities & technical trade-offs
├── frontend/                         # React 19 + TypeScript + Vite UI (18 Vitest tests)
│   ├── src/components/               # Reusable UI & protected role-based routing
│   ├── src/context/                  # Authentication context & session management
│   ├── src/pages/                    # Author portal & admin operations pages
│   ├── src/services/                 # API client & admin API integration
│   ├── src/types/                    # Strict TypeScript data models
│   ├── src/utils/                    # Currency and date formatting utilities
│   ├── vercel.json                   # SPA routing rewrite rules for Vercel
│   └── vite.config.ts                # Vite bundler configuration
├── .env.example                      # Environment variables template
├── .gitignore                        # Git exclusion rules
├── render.yaml                       # Render Infrastructure-as-Code blueprint
└── README.md                         # Project documentation
```

---

## ⚡ Core Features & Capabilities

### 1. Author Self-Service & Royalties Portal
- **Financial Transparency**: Accurate royalty summaries calculated across individual contract terms. Displays total copies sold, lifetime royalty earned, payouts disbursed, and net pending royalties.
- **Published Book Catalog**: Itemized view of ISBNs, publication dates, genres, distribution channels (Amazon India, Flipkart, BookLeaf Store, Amazon US/UK), and print partner assignments.
- **Isolated Ticket Desk**: Authors can file support tickets specifically tied to their published books or general queries.

### 2. Operations Center & Administrative Triage
- **Cross-Author Queue**: High-throughput triage dashboard with multi-facet filtering (Priority, Status, Category, Assigned Staff, Date Range, Text Search).
- **Gemini AI Copilot**: On-demand AI policy-grounded draft responses citing BookLeaf business rules (Royalty 45-day SLAs, reprint defect guarantees, 24-48h distributor resync, empathetic tone, zero corporate deflection).
- **One-Click AI Triage**: Automatically classify inquiries and assess priority based on author urgency and financial impact.
- **Confidential Internal Notes**: Private staff notes completely isolated from author view.

### 3. Real-Time Synchronization
- **Heartbeat Background Polling**: Conversation threads poll every **10 seconds** (`POLLING_INTERVAL_MS = 10000`) with a visible pulsing status indicator.
- **Silent Queue Refresh**: The admin queue and dashboard silently poll every **15 seconds** without flickering or locking user interactions.
- **Manual Instant Sync**: Every screen includes an instant `[↻ Refresh]` trigger.

### 4. Enterprise-Grade Tenant Isolation
- Authors can **only** view and access their own catalog, tickets, and messages.
- An author cannot file a ticket against a book ID belonging to another author.
- Private internal staff notes are excluded from all author-facing endpoints.
- Fully verified by automated regression test suites.

---

## 🧪 Comprehensive Automated Test Suite (71 Tests Passing)

The project includes **71 automated unit and integration tests** across both backend and frontend:

| Test Suite | Framework | Count | Coverage Areas | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Backend** | Pytest + HTTPX | **53 Tests** | Auth, RBAC, tenant isolation, AI triage, offline fallbacks, database relationships, seed idempotency | ✅ **53/53 Passed** |
| **Frontend** | Vitest + RTL | **18 Tests** | API service client, admin API methods, TypeScript data contracts, currency & date formatters | ✅ **18/18 Passed** |
| **Total** | | **71 Tests** | End-to-end fullstack verification | ✅ **71/71 Passed** |

### Running Backend Tests:
```bash
cd backend
python -m pytest tests -v
```

### Running Frontend Tests:
```bash
cd frontend
npm test
```

---

## 🚀 Local Quickstart Guide

### 1. Prerequisites
- **Python 3.11+** installed
- **Node.js 18+** & npm installed

### 2. Backend Setup
```bash
cd backend
python -m venv .venv

# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Linux / macOS:
source .venv/bin/activate

pip install -r requirements.txt
cp ../.env.example .env

# Run migrations and seed data
python -m alembic -c alembic.ini upgrade head
python seed.py

# Start server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Frontend Setup
```bash
cd ../frontend
npm install
cp .env.example .env
npm run dev
```

The frontend will run on `http://localhost:5173` and the backend on `http://localhost:8000`.

---

## 🏛️ Architecture Decisions & Why We Made Them

| Architectural Decision | Alternative Considered | Why We Made This Choice |
| :--- | :--- | :--- |
| **FastAPI + Pydantic v2** | Django / Flask / Express | High-performance async ASGI runtime with automatic OpenAPI Swagger generation and strict request/response data contracts matching publishing business domains. |
| **React 19 + TypeScript + Vite** | Next.js / Vanilla JS / CRA | Extremely fast client-side SPA with sub-2s production builds, zero SSR hydration mismatches, and comprehensive compile-time type safety across author and admin workflows. |
| **Row-Level Tenant Isolation** | Multi-Database Tenancy | Shared PostgreSQL relational schema with server-side JWT claim scoping (`author_id`). Eliminates massive connection pool overhead while mathematically guaranteeing authors cannot query or alter other authors' books or tickets. |
| **Short Polling (10s/15s Heartbeat)** | WebSockets / Socket.io | Stateful persistent TCP sockets frequently disconnect on cloud free-tier sleeping dynos and mobile network switching. Short polling is stateless, HTTP/2 multiplexed, and recovers instantly from network blips without reconnect logic. |
| **Alembic Versioned Migrations** | Raw SQL Scripts | Ensures deterministic, auditable DDL schema evolution across local SQLite and production cloud PostgreSQL without data loss or manual database interventions. |
| **Supabase IPv4 Connection Pooler** | Direct IPv6 Endpoint | Direct Supabase domain endpoints resolve to IPv6, which fail on container platforms like Render that lack IPv6 egress. Using the dedicated IPv4 pooler (`aws-0-ap-south-1.pooler.supabase.com:5432`) guarantees 100% network reachability. |

---

## 🤖 How the AI Integration Works

The portal integrates **Google Gemini 2.5 Flash** to triage inquiries and compose policy-grounded author responses, engineered for production reliability:

```
                           [Author Submits Ticket]
                                      │
                                      ▼
                      ┌───────────────────────────────┐
                      │    Tier 1: Deterministic      │  ◄── $0 API Cost
                      │     Keyword Rule Engine       │  ◄── 0ms Latency
                      └───────────────┬───────────────┘  ◄── DDoS / Spam Proof
                                      │
                                      ▼
                             [Ticket Saved to DB]
                                      │
                      (Admin views ticket in Queue)
                                      │
             ┌────────────────────────┴────────────────────────┐
             ▼                                                 ▼
   [Click "AI Triage"]                             [Click "Generate AI Draft"]
             │                                                 │
             ▼                                                 ▼
┌─────────────────────────┐                       ┌─────────────────────────┐
│  Tier 2: Gemini 2.5     │                       │  Tier 2: Gemini 2.5     │
│  Flash LLM Triage       │                       │  Flash Grounded Draft   │
│  (Structured JSON)      │                       │  (Policy Knowledge Base)│
└─────────────────────────┘                       └─────────────────────────┘
```

### 1. Prompt Strategy
- **Knowledge Base Policy Grounding**: The drafting prompt injects BookLeaf's 13 official publishing operating rules:
  - *Royalties*: 80/20 profit split, ₹1,000 threshold, 45-day post-quarter SLA.
  - *Printing*: 14-day defect replacement guarantee with photographic proof.
  - *Distribution*: 24–48 hour distributor metadata sync across Amazon, Flipkart, and Ingram.
  - *Tone*: Empathetic, professional, non-defensive, with transparent resolution timelines and zero corporate deflection.
- **Anchored Context Window**: Rather than sending unconstrained conversation histories (which inflate token costs and induce hallucination), the prompt constructs an anchored window containing the **original root inquiry + author catalog context + the last 9 messages**.
- **Native JSON Schema Enforcement**: Triage outputs use Gemini's `GenerateContentConfig(response_mime_type="application/json", response_schema=...)` to guarantee schema validity without regex parsing errors.

### 2. Error Handling & Zero-Downtime Resilience
- **Offline Safe Fallback Mode**: If `GEMINI_API_KEY` is missing, unconfigured, or expired, ticket creation and admin queues operate seamlessly without crashing.
- **Rate Limit & Network Recovery (HTTP 429 / Timeouts)**: If the Gemini API hits a rate limit (`RESOURCE_EXHAUSTED`) or network timeout, the system automatically falls back to deterministic rule triage and displays a clean status notice to the staff member.
- **Human-in-the-Loop Governance**: AI drafts are served strictly as editable proposals in the admin composer. AI **never** dispatches unvetted messages directly to authors.

### 3. Cost Management & Governance
- **Two-Tier Architecture**: 
  - *Tier 1 ($0 Cost)*: Public author ticket submission runs purely on-device deterministic keyword heuristics. Zero external API calls, zero cost, completely immune to bot or DDoS quota exhaustion.
  - *Tier 2 (On-Demand)*: Generative LLM reasoning is invoked **strictly on-demand** when an authenticated administrator clicks a button.
- **Draft Caching & Cleanup**: Draft responses are cached in the ticket's `ai_classification` metadata while being reviewed. Once sent or modified, stale drafts are purged to avoid redundant API billing.

---

## ⚠️ Known Limitations & Things to Improve Given More Time

While the system is fully functional, robust, and live in production, the following improvements are prioritized for enterprise scale:

1. **WebSockets / Server-Sent Events (SSE) for Real-Time Streaming**:
   - *Current*: 10-second short polling heartbeat.
   - *Improvement*: Transition to a dedicated WebSocket or SSE connection using Redis Pub/Sub when migrating from sleeping cloud free-tiers to dedicated always-on infrastructure.
2. **Multimodal AI Defect Inspection**:
   - *Current*: Authors describe physical print defects textually.
   - *Improvement*: Leverage Gemini 2.5 Flash's multimodal vision API to inspect uploaded photos of misaligned spines, cover fading, or torn bindings and auto-approve reprint replacements under BookLeaf's 14-day warranty.
3. **Asynchronous Background Task Processing (Celery + Redis)**:
   - *Current*: Email notifications and database operations execute within the FastAPI request-response lifecycle.
   - *Improvement*: Offload transactional email dispatches, webhook calls, and PDF royalty statement generation to a distributed task queue (Celery or Temporal).
4. **Author Self-Service AI Deflection Bot**:
   - *Current*: Authors create tickets that are routed to staff queues.
   - *Improvement*: Introduce a conversational deflection widget on the `/tickets/new` page that answers routine questions (royalty calendars, payout formulas, ISBN turnaround) using policy knowledge before a formal ticket is created, reducing support queue volume by ~35–45%.

---

## 📚 Technical Documentation Index

For detailed architectural decisions, AI strategies, and API specifications, refer to the documents in `docs/`:

- [docs/architecture.md](docs/architecture.md) — Technical Architecture, Live Cloud Topology, and ERD
- [docs/api.md](docs/api.md) — REST API Endpoint Specification and Request/Response Payloads
- [docs/ai-strategy.md](docs/ai-strategy.md) — Gemini AI Strategy, Knowledge Base Grounding, and Prompt Design
- [docs/approach-and-tradeoffs.md](docs/approach-and-tradeoffs.md) — Architectural Priorities, Decision Matrices, and Technical Trade-offs
