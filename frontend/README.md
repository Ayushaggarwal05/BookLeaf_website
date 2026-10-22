# BookLeaf Author & Administrative Frontend

Modern, publishing-themed author support and operations interface for **BookLeaf Publishing**, built with React 19, TypeScript, Vite, and Tailwind CSS.

---

## 1. Overview & Key Capabilities

The BookLeaf frontend provides two distinct, role-segregated user experiences:

### Author Portal
- **Dashboard & Performance**: Real-time sales metrics, lifetime copies sold, total royalties earned, paid, and pending balances.
- **My Catalog (`/books`)**: Itemized catalog view of published titles, ISBNs, genres, MRPs, per-copy royalty rates, and lifetime sales metrics.
- **Support Communication Portal (`/tickets`)**: Support ticket submission, search, conversation threads, and file attachment indicators. Restricted strictly to books owned by the authenticated author.
- **Session Protection**: Automatic token renewal, session expiry handling, and isolation from administrative routes.

### Operations & Administrative Dashboard
- **Operations Overview (`/admin`)**: Ticket count summaries by status (`OPEN`, `IN_PROGRESS`, `WAITING_ON_AUTHOR`, `RESOLVED`, `CLOSED`) and priority (`LOW`, `MEDIUM`, `HIGH`, `URGENT`).
- **Ticket Queue Management (`/admin/tickets`)**: Live search, status/priority filtering, staff assignment, and date-range filtering.
- **Ticket Operation Hub (`/admin/tickets/:id`)**:
  - Full author context card with verified catalog information.
  - **Gemini AI Copilot**: On-demand AI policy-grounded draft responses citing BookLeaf business rules (Royalty SLAs, Print Quality, ISBNs, Distribution).
  - **One-Click AI Triage**: Apply AI-suggested category and priority with audit logging.
  - **Confidential Internal Notes**: Admin-only staff notes strictly isolated from author view.
  - **Author Replies**: Sends public responses and transitions tickets to `WAITING_ON_AUTHOR`.

---

## 2. Tech Stack

- **Framework**: React 19 (`react`, `react-dom`)
- **Language**: TypeScript (strict mode, zero build warnings)
- **Routing**: React Router v7 (`react-router-dom`)
- **Styling**: Tailwind CSS with custom BookLeaf publishing palette:
  - Deep Forest Primary: `#0F382A` (`brand-900`) / `#1F5E46` (`brand-700`)
  - Warm Off-White / Cream Card: `#FCFCF9` (`cream-50`)
  - Soft Borders & Restrained Shadows: `#EBEBE6`
- **Icons**: Lucide React (`lucide-react`)
- **Testing**: Vitest (`vitest`)
- **Build Tool**: Vite v8 + Rollup

---

## 3. Getting Started

### Prerequisites
- **Node.js**: v18.0.0 or higher
- **npm**: v9.0.0 or higher
- Running BookLeaf backend at `http://localhost:8000`

### 1. Installation
From the `frontend/` directory:

```bash
npm install
```

### 2. Environment Setup
Create a `.env` file from the example template:

```bash
cp .env.example .env
```

Ensure `VITE_API_BASE_URL` points to your running FastAPI backend:
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### 3. Available Scripts

| Command | Description |
| :--- | :--- |
| `npm run dev` | Starts Vite local development server with Hot Module Replacement |
| `npm test` | Runs the Vitest automated test suite (18 unit & integration tests) |
| `npm run build` | Runs TypeScript type checking (`tsc -b`) and bundles production assets into `dist/` |
| `npm run lint` | Runs Oxlint linter across all TypeScript and TSX source files |
| `npm run preview` | Previews the production build locally |

---

## 4. Directory Structure

```
frontend/
├── public/                      # Static assets and icons
├── src/
│   ├── components/
│   │   ├── admin/               # Admin navigation & management widgets
│   │   │   └── AdminNavbar.tsx
│   │   └── common/              # Reusable UI & route protection
│   │       ├── CurrencyFormatter.tsx
│   │       ├── LoadingSpinner.tsx
│   │       ├── Navbar.tsx
│   │       ├── ProtectedRoute.tsx
│   │       └── StatusBadge.tsx
│   ├── context/
│   │   └── AuthContext.tsx      # Auth state, login/logout, JWT storage
│   ├── pages/
│   │   ├── admin/               # Administrative views
│   │   │   ├── AdminDashboardPage.tsx
│   │   │   ├── AdminTicketDetailPage.tsx
│   │   │   └── AdminTicketsPage.tsx
│   │   ├── BooksPage.tsx        # Author catalog
│   │   ├── DashboardPage.tsx    # Author financial & sales metrics
│   │   ├── LoginPage.tsx        # Authentication entry point
│   │   ├── NewTicketPage.tsx    # Author ticket submission
│   │   ├── TicketDetailPage.tsx # Author ticket conversation
│   │   └── TicketsPage.tsx      # Author ticket list
│   ├── services/
│   │   ├── __tests__/           # API service unit tests
│   │   └── api.ts               # Authenticated API client & endpoints
│   ├── types/
│   │   ├── __tests__/           # TypeScript model tests
│   │   └── *.ts                 # Author, Book, Ticket, Auth schemas
│   ├── utils/                   # Formatting utilities (currency, date, status)
│   ├── App.tsx                  # Client-side router configuration
│   └── main.tsx                 # React application entry point
├── vercel.json                  # SPA routing rewrite rules for Vercel
├── vite.config.ts               # Vite bundler configuration
└── package.json
```

---

## 5. Demo Credentials

| Role | Email | Password | Access |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@bookleaf.in` | `Admin@BookLeaf2026!` | Operations queue, internal notes, AI draft copilot |
| **Author (Priya)** | `priya.sharma@email.com` | `Author@BookLeaf2026!` | Priya Sharma catalog (`BK001`, `BK002`) & support tickets |
| **Author (Rohit)** | `rohit.kapoor@email.com` | `Author@BookLeaf2026!` | Rohit Kapoor catalog (`BK003`) & support tickets |
