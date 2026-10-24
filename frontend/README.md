# BookLeaf Author & Administrative Frontend

Modern, publishing-themed author support and operations interface for **BookLeaf Publishing**, built with **React 19**, **TypeScript**, **Vite**, and **Tailwind CSS**.

---

## 🚀 Live Production Deployment

| Service | Platform | URL |
| :--- | :--- | :--- |
| **Frontend Web App** | Vercel Global Edge | [https://book-leaf-website-five.vercel.app](https://book-leaf-website-five.vercel.app) |
| **Backend REST API** | Render Web Service | [https://bookleaf-backend-dcy8.onrender.com/api/v1](https://bookleaf-backend-dcy8.onrender.com/api/v1) |
| **Interactive API Docs** | Render Swagger UI | [https://bookleaf-backend-dcy8.onrender.com/docs](https://bookleaf-backend-dcy8.onrender.com/docs) |

---

## 1. Overview & Key Capabilities

The BookLeaf frontend provides two distinct, role-segregated user experiences:

### 👤 Author Portal
- **Dashboard & Performance**: Real-time sales metrics, lifetime copies sold, total royalties earned, paid, and pending balances computed against contract terms.
- **My Catalog (`/books`)**: Itemized catalog view of published titles, ISBNs, genres, MRPs, per-copy royalty rates, and lifetime sales metrics.
- **Support Communication Portal (`/tickets`)**: Support ticket submission, search, conversation threads, and file attachment indicators. Restricted strictly to books owned by the authenticated author.
- **Real-Time Polling (10s/15s)**: Conversation threads and ticket lists automatically refresh in the background without full-page reloads.
- **Session Protection**: Automatic token renewal, session expiry handling, and strict client-side isolation from administrative routes.

### 🛡️ Operations & Administrative Dashboard
- **Operations Overview (`/admin`)**: Real-time ticket count summaries by status (`OPEN`, `IN_PROGRESS`, `WAITING_ON_AUTHOR`, `RESOLVED`, `CLOSED`) and priority (`LOW`, `MEDIUM`, `HIGH`, `URGENT`).
- **Ticket Queue Management (`/admin/tickets`)**: Live search, multi-facet status/priority filtering, staff assignment, and date-range filtering.
- **Ticket Operation Hub (`/admin/tickets/:id`)**:
  - Full author context card with verified catalog information.
  - **Gemini AI Copilot**: On-demand AI policy-grounded draft responses citing official BookLeaf business rules (Royalty SLAs, Print Quality, ISBNs, Distribution).
  - **One-Click AI Triage**: Apply AI-suggested category and priority with audit logging.
  - **Confidential Internal Notes**: Admin-only staff notes strictly isolated from author view.
  - **Author Replies**: Sends public responses and transitions tickets to `WAITING_ON_AUTHOR`.

---

## 2. Tech Stack

- **Framework**: React 19 (`react`, `react-dom`)
- **Language**: TypeScript (strict mode, zero build warnings)
- **Routing**: React Router v7 (`react-router-dom`) with SPA rewrite rules in `vercel.json`
- **Styling**: Tailwind CSS with custom BookLeaf publishing palette:
  - Deep Forest Primary: `#0F382A` (`brand-900`) / `#1F5E46` (`brand-700`)
  - Warm Off-White / Cream Card: `#FCFCF9` (`cream-50`)
  - Soft Borders & Restrained Shadows: `#EBEBE6`
- **Icons**: Lucide React (`lucide-react`)
- **Testing**: Vitest (`vitest`) — 18 automated unit and integration tests
- **Build Tool**: Vite v8 + Rollup

---

## 3. Real-Time Synchronization Strategy

Rather than relying on brittle WebSocket connections that drop on sleep or free cloud tiers, BookLeaf uses **heartbeat background polling**:
- **Conversation Threads (`/tickets/:id` & `/admin/tickets/:id`)**: Polls every **10 seconds** (`POLLING_INTERVAL_MS = 10000`) with a visible pulsing indicator and last-refreshed timestamp.
- **Queues & Dashboards (`/admin`, `/admin/tickets`, `/tickets`)**: Polls every **15 seconds** silently without flickering or disrupting user interactions.
- **Instant Manual Refresh**: Every screen features a dedicated `[↻ Refresh]` button for immediate synchronization.

---

## 4. Getting Started

### Prerequisites
- **Node.js**: v18.0.0 or higher
- **npm**: v9.0.0 or higher
- Running BookLeaf backend at `http://localhost:8000` (or the live Render API)

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

Ensure `VITE_API_BASE_URL` points to your backend:
```env
# Local Development
VITE_API_BASE_URL=http://localhost:8000/api/v1

# Or Point to Live Render Backend
# VITE_API_BASE_URL=https://bookleaf-backend-dcy8.onrender.com/api/v1
```

### 3. Available Scripts

| Command | Description |
| :--- | :--- |
| `npm run dev` | Starts Vite local development server with Hot Module Replacement |
| `npm test` | Runs the Vitest automated test suite (18 unit & integration tests) |
| `npm run build` | Runs TypeScript type checking (`tsc -b`) and bundles production assets into `dist/` |
| `npm run preview` | Previews the production build locally |

---

## 5. Directory Structure

```
frontend/
├── public/                      # Static favicon
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
│   ├── index.css                # Tailwind base styles and theme tokens
│   └── main.tsx                 # React application entry point
├── vercel.json                  # SPA routing rewrite rules for Vercel
├── vite.config.ts               # Vite bundler configuration
└── package.json
```

---

## 6. Demo Accounts for Evaluation

All author accounts use the shared test password: `Author@BookLeaf2026!`

| Role | Email | Password | What to Verify |
| :--- | :--- | :--- | :--- |
| **Operations Admin** | `admin@bookleaf.in` | `Admin@BookLeaf2026!` | Global ticket triage queue, Gemini AI Copilot drafting, internal notes |
| **Author (Priya Sharma)** | `priya.sharma@email.com` | `Author@BookLeaf2026!` | 2 published books (*Whispers of the Ganges*, *The Saffron Diaries*), royalty balance |
| **Author (Rohit Kapoor)** | `rohit.kapoor@email.com` | `Author@BookLeaf2026!` | 2 published books (*Code & Karma*, *Startup Sutra*), royalty balance |
| **Author (Ananya Reddy)** | `ananya.reddy@email.com` | `Author@BookLeaf2026!` | 1 published book (*Between Two Temples*), new ticket submission |
| **Author (Sneha Kulkarni)** | `sneha.kulkarni@email.com` | `Author@BookLeaf2026!` | 3 published books (*The Algorithm of Love*, *Ctrl+Alt+Delete My Ex*, *Midnight in Mysore*) |
| **Author (Diya Chatterjee)** | `diya.chatterjee@email.com` | `Author@BookLeaf2026!` | 2 published books (*Durga's Daughters*, *Howrah Nights*), royalty balance |
