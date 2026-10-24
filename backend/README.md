# BookLeaf Author Support & Communication Portal - Backend API

Robust, production-minded REST API backend powering the **BookLeaf Publishing** Author Support & Operations Portal. Built with **FastAPI**, **SQLAlchemy 2.0**, **Pydantic v2**, and **Google Gemini 2.5 Flash**.

---

## 1. Overview & Key Capabilities

The BookLeaf backend serves as the core business logic, persistence, and AI orchestration engine for two primary workflows:

### Author Portal API (`/api/v1/author`)

- **Strict Tenant Isolation**: Authenticated authors can only access their own profile, catalog, and support tickets.
- **My Catalog & Royalties (`/books`)**: Delivers lifetime sales figures, royalties earned, payouts received, and pending balances computed against contract terms.
- **Support Ticket Submission (`/tickets`)**: Ingests author queries linked to specific books or general account inquiries. Automatically performs **Tier 1 ($0 Cost) Deterministic Triage** upon creation so tickets are immediately classified with zero latency.
- **Ticket Threads & Live Updates**: Pollable message threads showing public support agent responses and status updates.

### Operations & Admin Portal API (`/api/v1/admin`)

- **Organization-Wide Queue (`/admin/tickets`)**: Multi-faceted filtering by status (`OPEN`, `IN_PROGRESS`, `WAITING_ON_AUTHOR`, `RESOLVED`, `CLOSED`), priority (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`), category, and search queries. Highlights the most urgent and oldest unresolved tickets.
- **AI-Powered Triage & Classification (`/ai-triage`)**: Powered by Google Gemini 2.5 Flash to classify tickets into 6 official categories and assign priority with rationale. Admins retain 1-click override control.
- **AI Drafted Responses (`/ai-draft`)**: Context-aware response generation grounded in BookLeaf's official Knowledge Base and Tone Guidelines (Royalty 45-day SLAs, reprint defect guarantees, 24-48h distributor resync, zero corporate deflection).
- **Confidential Internal Notes**: Private staff notes visible only to admins and strictly hidden from author endpoints.
- **Ticket Lifecycle Management**: Assign tickets to team members and transition ticket statuses (including `WAITING_ON_AUTHOR`).

---

## 2. Technology Stack

- **Runtime**: Python 3.11+ (tested on Python 3.13)
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (high performance, ASGI, automatic OpenAPI generation)
- **Data Modeling & Validation**: [Pydantic v2](https://docs.pydantic.dev/)
- **ORM & Database**: [SQLAlchemy 2.0](https://www.sqlalchemy.org/) (SQLite for local development / PostgreSQL ready)
- **Database Migrations**: [Alembic](https://alembic.sqlalchemy.org/)
- **Authentication**: JWT tokens (HMAC-SHA256 via `pyjwt`) + `passlib[bcrypt]` password hashing
- **AI Engine**: Google Gemini API (`google-genai` / Gemini 2.5 Flash) with Two-Tier cost optimization & deterministic keyword fallback
- **Testing**: [pytest](https://docs.pytest.org/) with `httpx` test client (53 automated tests)

---

## 3. Directory Structure

```
backend/
├── alembic.ini                   # Database migration configuration
├── build.sh                      # Deployment build and seed script
├── requirements.txt              # Production and development dependencies
├── seed.py                       # CLI runner for sample dataset import
├── README.md                     # Backend documentation
├── app/
│   ├── __init__.py               # App package init (with sys.path fallback)
│   ├── main.py                   # FastAPI application factory, CORS, and lifecycles
│   ├── api/
│   │   └── routes/
│   │       ├── __init__.py       # API v1 router aggregator
│   │       ├── admin_portal.py   # Admin queue, AI triage, AI draft, staff notes
│   │       ├── author_portal.py  # Author dashboard, book catalog, tickets
│   │       ├── auth.py           # Login, token issuance, credential verification
│   │       └── health.py         # System health & database connectivity check
│   ├── core/
│   │   ├── config.py             # App settings via pydantic-settings (.env)
│   │   ├── database.py           # SQLAlchemy engine, session maker, SQLite PRAGMAs
│   │   ├── dependencies.py       # RBAC auth middlewares (require_author, require_admin)
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
│       ├── seed_service.py       # Idempotent JSON dataset parser
│       └── ticket_service.py     # Ticket state machine and conversation management
├── migrations/                   # Alembic database migration scripts
└── tests/                        # Full test suite (53 unit & integration tests)
```

---

## 4. Setup & Installation

### Step 1: Virtual Environment Setup

Navigate to the `backend/` directory:

```bash
cd backend
```

Create a virtual environment (named `.venv`):

```bash
python -m venv .venv
```

Activate the virtual environment:

- **Windows PowerShell**:

  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```

  _(If execution policy blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first)_

- **Windows Command Prompt (cmd)**:

  ```cmd
  .venv\Scripts\activate.bat
  ```

- **Linux / macOS**:
  ```bash
  source .venv/bin/activate
  ```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Environment Variables Configuration

Copy the example environment file from the project root:

```bash
cp ../.env.example .env
```

Key environment configuration variables in `.env`:

| Variable                      | Default Value                              | Description                                         |
| :---------------------------- | :----------------------------------------- | :-------------------------------------------------- |
| `DATABASE_URL`                | `sqlite:///./bookleaf_dev.db`              | SQLite database URI or PostgreSQL connection string |
| `JWT_SECRET_KEY`              | `change-this-to-a-secure-random-secret...` | 256-bit secret key used to sign JWT tokens          |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `120`                                      | JWT token validity window                           |
| `GEMINI_API_KEY`              | `""`                                       | Google Gemini API key (kept strictly on backend)    |
| `GEMINI_MODEL`                | `gemini-2.5-flash`                         | Gemini model identifier                             |
| `DEMO_ADMIN_EMAIL`            | `admin@bookleaf.in`                        | Pre-seeded administrator email                      |
| `DEMO_ADMIN_PASSWORD`         | `Admin@BookLeaf2026!`                      | Pre-seeded administrator password                   |
| `DEMO_AUTHOR_PASSWORD`        | `Author@BookLeaf2026!`                     | Pre-seeded password for all 10 sample authors       |

---

## 5. Database Seeding

The backend includes an idempotent seeding utility that imports authors and books from `data/bookleaf_sample_data.json` and provisions ready-to-use demo accounts:

```bash
python seed.py
```

### Seeded Demo Accounts:

- **Admin Account**:
  - Email: `admin@bookleaf.in`
  - Password: `Admin@BookLeaf2026!`
  - Role: `admin` (access to operations queue, AI triage, drafting, notes)

- **Author Accounts** (All 10 sample authors from JSON dataset):
  - Password for all authors: `Author@BookLeaf2026!`
  - Samples:
    - `priya.sharma@email.com` (Priya Sharma - Literary Fiction)
    - `rohit.kapoor@email.com` (Rohit Kapoor - Tech & Entrepreneurship)
    - `ananya.reddy@email.com` (Ananya Reddy - Poetry)
    - `vikram.joshi@email.com` (Vikram Joshi - Thriller)
    - _(and 6 more authors in the dataset)_

---

## 6. Running the Development Server

Start the FastAPI application with auto-reloading:

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

_Or run via Python module:_

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

The server will start at **`http://127.0.0.1:8000`**.

### Interactive API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Redoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **OpenAPI JSON**: [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)

---

## 7. REST API Endpoints Reference

All application endpoints are prefixed with `/api/v1`:

### Authentication (`/api/v1/auth`)

- `POST /api/v1/auth/login` — Authenticate author or admin with email/password; returns JWT bearer token.
- `GET /api/v1/auth/me` — Retrieve the current authenticated user's profile and role.

### Author Portal (`/api/v1/author`) _(Requires Author Bearer Token)_

- `GET /api/v1/author/dashboard` — Aggregated author statistics (books published, copies sold, royalties).
- `GET /api/v1/author/books` — Itemized list of published titles with ISBN, status, MRP, and royalties.
- `GET /api/v1/author/tickets` — List all support tickets created by the authenticated author.
- `POST /api/v1/author/tickets` — Submit a new support query (initiates Tier 1 deterministic triage).
- `GET /api/v1/author/tickets/{id}` — Get ticket detail and conversation history (internal notes filtered out).
- `POST /api/v1/author/tickets/{id}/reply` — Post a reply to an ongoing ticket thread.

### Admin Portal (`/api/v1/admin`) _(Requires Admin Bearer Token)_

- `GET /api/v1/admin/dashboard` — Global ticket statistics by status, priority, and urgent counts.
- `GET /api/v1/admin/tickets` — Filterable ticket queue (status, priority, category, search, sorting).
- `GET /api/v1/admin/tickets/{id}` — Complete ticket view with author profile, catalog, notes, and messages.
- `PATCH /api/v1/admin/tickets/{id}` — Update ticket status, manual category/priority overrides, or staff assignment.
- `POST /api/v1/admin/tickets/{id}/reply` — Send an official author-facing response (sets status to `WAITING_ON_AUTHOR`).
- `POST /api/v1/admin/tickets/{id}/notes` — Add a confidential internal staff note.
- `POST /api/v1/admin/tickets/{id}/ai-triage` — Trigger on-demand Gemini AI auto-classification and priority scoring.
- `POST /api/v1/admin/tickets/{id}/ai-draft` — Generate an AI draft response grounded in BookLeaf policies.

### Health Check (`/health`)

- `GET /health` — Verifies API liveness and database connectivity.

---

## 8. AI Architecture & Production Best Practices

The AI engine in [`app/services/ai_service.py`](app/services/ai_service.py) incorporates production-grade AI design:

1. **Two-Tier Cost-Aware Architecture**:
   - **Tier 1 (Author Submit)**: Evaluated locally via deterministic keyword rules. Zero latency, $0 API spend.
   - **Tier 2 (Admin On-Demand)**: Gemini 2.5 Flash is invoked only when an agent actively requests AI triage or drafting.
2. **Context Window Optimization**:
   - Rather than sending infinite message histories, the draft engine uses an anchored sliding window (original ticket query + author profile + last 10 messages) with targeted knowledge base citations.
3. **Graceful Fallback & 429 Resilience**:
   - If the Gemini API hits a rate limit (`429 RESOURCE_EXHAUSTED`) or network timeout, the system automatically falls back to deterministic rule triage and provides a clean notice without crashing or interrupting operations.
4. **Strict Key Security**:
   - `GEMINI_API_KEY` is loaded exclusively on the backend from `.env`. It is never transmitted or exposed to the client.

---

## 9. Running the Test Suite

The backend includes a comprehensive test suite covering all critical paths:

```bash
pytest
```

To run with verbose output:

```bash
pytest -v
```

### Test Coverage Highlights (53 Tests):

- **API Endpoints (`test_api_endpoints.py`)**: Authentication, author book listing, ticket creation, admin queue filtering, reply threads.
- **Dataset Parsing (`test_dataset_parsing.py`)**: Validates JSON dataset integrity, currency types, ISBN formats, and author schemas.
- **Frontend Flow Integration (`test_frontend_flow.py`)**: End-to-end author ticket submission, status updates, internal notes isolation, and AI fallback.
- **Seed Idempotency (`test_seed_idempotency.py`)**: Confirms re-running `seed.py` never duplicates records or damages user-created tickets.
- **Invalid Dataset Resilience (`test_invalid_dataset.py`)**: Verifies graceful error handling on malformed JSON structures.
