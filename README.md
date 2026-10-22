# BookLeaf Author Support & Communication Portal

Production-minded full-stack support and publishing portal for authors and support agents at BookLeaf Publishing.

---

## Project Structure

```
bookleaf-support-portal/
├── backend/
│   ├── alembic.ini                   # Alembic configuration
│   ├── requirements.txt              # Production and testing Python dependencies
│   ├── seed.py                       # CLI runner for database seeding
│   ├── app/
│   │   ├── main.py                   # FastAPI app factory, CORS, and lifecycles
│   │   ├── core/
│   │   │   ├── config.py             # Environment settings & validation (Pydantic v2)
│   │   │   └── database.py           # SQLAlchemy 2.x engine, session, SQLite PRAGMA hook
│   │   ├── models/                   # SQLAlchemy declarative ORM models
│   │   │   ├── author.py
│   │   │   ├── book.py
│   │   │   ├── ticket.py
│   │   │   ├── ticket_message.py
│   │   │   ├── internal_note.py
│   │   │   └── user.py
│   │   ├── schemas/                  # Pydantic v2 validation and serialization schemas
│   │   ├── api/
│   │   │   └── routes/               # Modular API routers (/health, /authors, /books, /tickets)
│   │   ├── services/                 # Business logic and seed import service
│   │   ├── repositories/             # Data access layer
│   │   └── utils/
│   ├── migrations/                   # Alembic migration scripts
│   └── tests/                        # Full pytest suite (24 automated tests)
├── data/
│   └── bookleaf_sample_data.json     # Official assignment sample dataset
├── docs/
│   └── architecture.md               # Technical architecture & ERD documentation
├── frontend/                         # Reserved for upcoming frontend phase
├── .env.example                      # Environment variables template
├── .gitignore                        # Git exclusion rules
└── README.md                         # Project documentation
```

---

## Quickstart Guide

### 1. Prerequisites
- **Python 3.11+** installed (tested on Python 3.13)
- Windows PowerShell, macOS zsh, or Linux bash

### 2. Set Up Virtual Environment & Dependencies

```bash
# Clone or navigate to the project directory
cd "k:/Work/Assignment for job/BookLeaf"

# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Linux / macOS:
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

### 3. Environment Configuration

Copy the example environment configuration:

```bash
cp .env.example .env
```

Key environment variables:

| Variable | Default | Description |
| :--- | :--- | :--- |
| `DATABASE_URL` | `sqlite:///./bookleaf_dev.db` | Local SQLite database or PostgreSQL connection string |
| `SECRET_KEY` | *(auto-generated)* | 256-bit cryptographically secure JWT secret |
| `GEMINI_API_KEY` | `""` | Google Gemini API key for AI classification & response drafting |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Configurable Google Gemini model identifier |
| `GEMINI_TIMEOUT_SECONDS` | `30` | Network timeout for Gemini provider requests |

> **Note on AI Operation:** If `GEMINI_API_KEY` is not configured, the entire application operates seamlessly in **safe fallback mode**. Ticket creation automatically uses deterministic heuristic classification, and the admin interface displays clean status notices without crashing or leaking provider secrets.

### 4. Run Database Migrations

Apply database migrations to head:

```bash
python -m alembic -c backend/alembic.ini upgrade head
```

### 5. Seed the Official Dataset & Provision Demo Accounts

Seed the database with authors and books from `data/bookleaf_sample_data.json` and initialize demo credentials:

```bash
python backend/seed.py
```

*Note: The seed script is completely idempotent. Running it multiple times safely updates records without duplicating authors, books, or altering user-created support tickets.*

### 6. Demo Credentials for Local & Testing Environments

| Role | Email | Password | Description |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@bookleaf.in` | `Admin@BookLeaf2026!` | Full administrative ticket queue, triage overrides, & AI Copilot |
| **Author** | `priya.sharma@email.com` | `Author@BookLeaf2026!` | Author (AUTH001) catalog, royalties, and support tickets |
| **Author** | `rohit.kapoor@email.com` | `Author@BookLeaf2026!` | Author (AUTH002) catalog, royalties, and support tickets |

### 7. Run Backend Automated Tests

Execute the automated backend test suite with verbose reporting:

```bash
.venv\Scripts\python.exe -m pytest backend/tests -v
```

All **53 tests** cover:
- Gemini AI triage, priority scoring, and knowledge base context extraction
- Mocked Gemini provider tests for response drafting and timeout/error handling
- Offline heuristic fallback and missing API key resilience
- Admin AI draft generation and triage override application endpoints
- Role-based authorization guarding AI endpoints from unauthorized authors
- Authentication & JWT issuance (`POST /api/v1/auth/login`, `GET /api/v1/auth/me`)
- Author-level tenant isolation (cross-author book & ticket access blocked)
- Unowned book ticket submission rejection
- Public conversation vs. private internal note segregation
- Admin cross-author queues, filtering, search, and triage overrides

### 8. Frontend Setup & Build

The frontend is built with React 19, TypeScript, Vite, and Tailwind CSS:

```bash
cd frontend

# Install frontend dependencies
npm install

# Run frontend tests
npm test

# Build production bundle
npm run build

# Start local development server
npm run dev
```

### 9. Start the Backend Server

Start the FastAPI application using Uvicorn:

```bash
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

Once started:
- **Interactive OpenAPI Documentation (Swagger UI)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Alternative API Documentation (ReDoc)**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Health Check Endpoint**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
- **AI Strategy & Architecture**: [docs/ai-strategy.md](docs/ai-strategy.md)
- **API Documentation File**: [docs/api.md](docs/api.md)
- **System Architecture**: [docs/architecture.md](docs/architecture.md)

