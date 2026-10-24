# BookLeaf Author Support & Communication Portal - Backend API

Robust, production-minded REST API backend powering the **BookLeaf Publishing** Author Support & Operations Portal. Built with **FastAPI**, **SQLAlchemy 2.0**, **Pydantic v2**, and **Google Gemini 2.5 Flash**.

---

## 🚀 Live Production Deployment

| Service | Provider | URL | Status |
| :--- | :--- | :--- | :--- |
| **Backend REST API** | Render Web Service | [https://bookleaf-backend-dcy8.onrender.com](https://bookleaf-backend-dcy8.onrender.com) | ✅ Healthy (HTTP 200) |
| **Interactive API Docs** | Swagger UI | [https://bookleaf-backend-dcy8.onrender.com/docs](https://bookleaf-backend-dcy8.onrender.com/docs) | ✅ Live |
| **Alternative Docs** | ReDoc | [https://bookleaf-backend-dcy8.onrender.com/redoc](https://bookleaf-backend-dcy8.onrender.com/redoc) | ✅ Live |
| **System Health Check** | FastAPI `/health` | [https://bookleaf-backend-dcy8.onrender.com/health](https://bookleaf-backend-dcy8.onrender.com/health) | ✅ PostgreSQL Connected |
| **Cloud Database** | Supabase PostgreSQL | `aws-0-ap-south-1.pooler.supabase.com:5432` | ✅ Migrated & Seeded |

---

## 1. Overview & Key Capabilities

The BookLeaf backend serves as the core business logic, persistence, and AI orchestration engine for two primary workflows:

### 👤 Author Portal API (`/api/v1/author`)

- **Strict Tenant Isolation**: Authenticated authors can only access their own profile, catalog, and support tickets.
- **My Catalog & Royalties (`/books`)**: Delivers lifetime sales figures, royalties earned, payouts received, and pending balances computed against contract terms.
- **Support Ticket Submission (`/tickets`)**: Ingests author queries linked to specific books or general account inquiries. Automatically performs **Tier 1 ($0 Cost) Deterministic Triage** upon creation so tickets are immediately classified with zero latency.
- **Ticket Threads & Live Updates**: Pollable message threads showing public support agent responses and status updates.

### 🛡️ Operations & Admin Portal API (`/api/v1/admin`)

- **Organization-Wide Queue (`/admin/tickets`)**: Multi-faceted filtering by status (`OPEN`, `IN_PROGRESS`, `WAITING_ON_AUTHOR`, `RESOLVED`, `CLOSED`), priority (`URGENT`, `HIGH`, `MEDIUM`, `LOW`), category, and search queries. Highlights the most urgent and oldest unresolved tickets.
- **AI-Powered Triage & Classification (`/ai-triage`)**: Powered by Google Gemini 2.5 Flash to classify tickets into 6 official categories and assign priority with rationale. Admins retain 1-click override control.
- **AI Drafted Responses (`/ai-draft`)**: Context-aware response generation grounded in BookLeaf's official Knowledge Base and Tone Guidelines (Royalty 45-day SLAs, reprint defect guarantees, 24-48h distributor resync, empathetic tone, zero corporate deflection).
- **Confidential Internal Notes**: Private staff notes visible only to admins and strictly hidden from author endpoints.
- **Ticket Lifecycle Management**: Assign tickets to team members and transition ticket statuses (including `WAITING_ON_AUTHOR`).

---

## 2. Technology Stack

- **Runtime**: Python 3.11+ (tested on Python 3.11 & 3.13)
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (high performance, ASGI, automatic OpenAPI generation)
- **Data Modeling & Validation**: [Pydantic v2](https://docs.pydantic.dev/)
- **ORM & Database**: [SQLAlchemy 2.0](https://www.sqlalchemy.org/) (SQLite for local dev / Supabase PostgreSQL for cloud production)
- **Database Migrations**: [Alembic](https://alembic.sqlalchemy.org/)
- **Authentication**: JWT tokens (HMAC-SHA256 via `pyjwt`) + `passlib[bcrypt]` / `pwdlib` password hashing
- **AI Engine**: Google Gemini API (`google-genai` / Gemini 2.5 Flash) with Two-Tier cost optimization & deterministic keyword fallback
- **Testing**: [pytest](https://docs.pytest.org/) with `httpx` test client (53 automated tests)

---

## 3. Directory Structure

```
backend/
├── alembic.ini                   # Database migration configuration
├── build.sh                      # Cloud deployment build and seed script
├── requirements.txt              # Production and development dependencies
├── seed.py                       # CLI runner for sample dataset import
├── README.md                     # Backend documentation
├── app/
│   ├── __init__.py               # Package init with root sys.path resolution
│   ├── main.py                   # FastAPI application factory, CORS, and lifecycles
│   ├── api/
│   │   └── routes/
│   │       ├── __init__.py       # API router aggregator (/api and /api/v1)
│   │       ├── admin_portal.py   # Admin queue, AI triage, AI draft, staff notes
│   │       ├── author_portal.py  # Author dashboard, book catalog, tickets
│   │       ├── auth.py           # Login, token issuance, credential verification
│   │       ├── authors.py        # Legacy Phase 1 REST endpoint
│   │       ├── books.py          # Legacy Phase 1 REST endpoint
│   │       ├── tickets.py        # Legacy Phase 1 REST endpoint
│   │       └── health.py         # System health & database connectivity check
│   ├── core/
│   │   ├── config.py             # App settings via pydantic-settings (.env)
│   │   ├── database.py           # SQLAlchemy engine, session maker, SQLite PRAGMAs
│   │   ├── dependencies.py       # RBAC auth dependencies (require_author, require_admin)
│   │   └── security.py           # Bcrypt hashing and JWT token encoding/decoding
│   ├── models/                   # SQLAlchemy declarative ORM models
│   │   ├── author.py             # Author profiles and credentials
│   │   ├── book.py               # Book catalog, pricing, and royalty metrics
│   │   ├── ticket.py             # Support tickets, classification, priority
│   │   ├── ticket_message.py     # Conversation thread messages
│   │   ├── internal_note.py      # Confidential staff-only notes
│   │   └── user.py               # Administrative staff accounts
│   ├── repositories/             # Data access layer (CRUD abstraction)
│   ├── schemas/                  # Pydantic request/response validation schemas
│   └── services/                 # Core business logic
│       ├── ai_service.py         # Gemini 2.5 Flash orchestration & deterministic fallback
│       ├── auth_service.py       # Authentication & demo account provisioning
│       ├── knowledge_base.py     # Grounded BookLeaf operating guidelines
│       ├── seed_demo_tickets.py  # Cross-category demo ticket seeder
│       ├── seed_service.py       # Idempotent JSON dataset parser
│       └── ticket_service.py     # Ticket state machine and conversation management
├── migrations/                   # Alembic database migration scripts
│   └── versions/                 # Versioned DDL migrations
└── tests/                        # Full test suite (53 unit & integration tests)
```

---

## 4. Setup & Local Development

### Step 1: Virtual Environment Setup

From the `backend/` directory:

```bash
python -m venv .venv
```

Activate the virtual environment:
- **Windows PowerShell**: `.\.venv\Scripts\Activate.ps1`
- **Linux / macOS**: `source .venv/bin/activate`

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

```bash
cp ../.env.example .env
```

Key environment variables in `.env`:

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `DATABASE_URL` | `sqlite:///./bookleaf_dev.db` | SQLite URI (local) or PostgreSQL pooler URI (production) |
| `JWT_SECRET_KEY` | *(auto-generated)* | 256-bit cryptographically secure secret key |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `120` | JWT token lifespan |
| `GEMINI_API_KEY` | `""` | Google Gemini API key (strictly kept backend-side) |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Configured Gemini model identifier |
| `FRONTEND_ORIGIN` | `https://book-leaf-website-five.vercel.app` | Whitelisted frontend origin |

### Step 4: Run Migrations & Seed Data

```bash
# Run database migrations
python -m alembic -c alembic.ini upgrade head

# Seed authors, books, admin, and demo tickets
python seed.py
```

### Step 5: Start Local Server

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

---

## 5. Live Production Credentials

All author accounts use the shared test password: `Author@BookLeaf2026!`

| Role | Email | Password | Access |
| :--- | :--- | :--- | :--- |
| **Operations Admin** | `admin@bookleaf.in` | `Admin@BookLeaf2026!` | Operations queue, internal notes, Gemini AI copilot |
| **Author (Priya Sharma)** | `priya.sharma@email.com` | `Author@BookLeaf2026!` | Priya Sharma catalog (`BK001`, `BK002`) & support tickets |
| **Author (Rohit Kapoor)** | `rohit.kapoor@email.com` | `Author@BookLeaf2026!` | Rohit Kapoor catalog (`BK003`, `BK004`) & support tickets |
| **Author (Ananya Reddy)** | `ananya.reddy@email.com` | `Author@BookLeaf2026!` | Ananya Reddy catalog (`BK005`) & support tickets |
| **Author (Vikram Joshi)** | `vikram.joshi@email.com` | `Author@BookLeaf2026!` | Vikram Joshi catalog (`BK006`, `BK007`) & support tickets |
| **Author (Meera Nair)** | `meera.nair@email.com` | `Author@BookLeaf2026!` | Meera Nair catalog (`BK008`, `BK009`) & support tickets |

---

## 6. AI Architecture & Best Practices

The AI engine in [`app/services/ai_service.py`](app/services/ai_service.py) incorporates production-grade AI design:

1. **Two-Tier Cost-Aware Architecture**:
   - **Tier 1 (Author Submit)**: Evaluated locally via deterministic keyword rules. Zero latency, $0 API spend.
   - **Tier 2 (Admin On-Demand)**: Gemini 2.5 Flash is invoked only when an agent actively requests AI triage or drafting.
2. **Knowledge Base Grounding**:
   - Ingests official BookLeaf operating policies: 45-day royalty payment SLAs, 14-day reprint defect replacement, 24-48h distributor inventory sync, and anti-deflection empathetic tone guidelines.
3. **Context Window Optimization**:
   - Uses an anchored sliding window (original ticket query + author profile + last 10 messages) with targeted knowledge base citations.
4. **Graceful Fallback & 429 Resilience**:
   - If the Gemini API hits a rate limit or timeout, the system automatically falls back to deterministic rule triage without crashing or interrupting operations.
5. **Strict Key Security**:
   - `GEMINI_API_KEY` is loaded exclusively on the backend from environment variables. It is never transmitted or exposed to the client.

---

## 7. Running the Automated Backend Test Suite

```bash
pytest tests -v
```

### Coverage Breakdown (53 Tests Passing):
- **API Endpoints (`test_api_endpoints.py`)**: Authentication, author book listing, ticket creation, admin queue filtering, reply threads.
- **Tenant Isolation (`test_security_tenant_isolation.py`)**: Confirms authors cannot access other authors' books or tickets, and cannot submit tickets for unowned books.
- **AI Triage & Fallback (`test_ai_gemini.py`)**: Verifies Gemini AI classification, priority scoring, knowledge base retrieval, and offline fallback mode.
- **Dataset Parsing (`test_dataset_parsing.py`)**: Validates JSON dataset integrity, currency types, ISBN formats, and author schemas.
- **Frontend Flow Integration (`test_frontend_flow.py`)**: End-to-end author ticket submission, status updates, internal notes isolation, and AI fallback.
- **Seed Idempotency (`test_seed_idempotency.py`)**: Confirms re-running `seed.py` never duplicates records or damages existing tickets.
- **Database Relationships (`test_relationships.py`)**: Verifies foreign key constraints, cascading deletions, and message thread relationships.
