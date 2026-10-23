# BookLeaf API Reference Documentation

## 1. Overview & Architecture

The BookLeaf Author Support Portal REST API is versioned under `/api/v1/`. It enforces **zero-trust authentication** and **author-level tenant isolation**.

- **Base URL**: `http://127.0.0.1:8000`
- **Interactive Documentation**: `http://127.0.0.1:8000/docs` (Swagger UI)
- **Alternative Documentation**: `http://127.0.0.1:8000/redoc` (ReDoc)
- **Protocol**: JSON over HTTP/1.1 or HTTP/2
- **Authentication**: JWT Bearer token via `Authorization: Bearer <TOKEN>`

---

## 2. Authentication & Roles

### Roles
1. **`author`**: Access is strictly limited to their own catalog, royalties, support tickets, and author-visible conversation threads. Authors cannot access other authors' records, create tickets for unowned books, view internal admin notes, or access administrative endpoints.
2. **`admin`**: Support representatives and system administrators. Can view all author tickets, filter, search, re-assign, update status, override triage priority, add private internal notes, and send public responses.

### Demo Credentials (Development & Test Environments)

| Account Type | Email | Password | Role |
| :--- | :--- | :--- | :--- |
| **Demo Admin** | `admin@bookleaf.in` | `Admin@BookLeaf2026!` | `admin` |
| **Demo Author (Priya Sharma)** | `priya.sharma@email.com` | `Author@BookLeaf2026!` | `author` (AUTH001) |
| **Demo Author (Rohit Kapoor)** | `rohit.kapoor@email.com` | `Author@BookLeaf2026!` | `author` (AUTH002) |

---

## 3. Endpoints Reference

### 3.1 Authentication & Identity (`/api/v1/auth`)

#### `POST /api/v1/auth/login`
Authenticate user or author using email and password.

- **Request Body**:
  ```json
  {
    "email": "priya.sharma@email.com",
    "password": "Author@BookLeaf2026!"
  }
  ```
- **Response `200 OK`**:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "role": "author",
    "user_id": "AUTH001",
    "email": "priya.sharma@email.com",
    "name": "Priya Sharma",
    "author_id": "AUTH001"
  }
  ```
- **Error Responses**: `401 Unauthorized` on invalid email or password.

---

#### `GET /api/v1/auth/me`
Retrieve authenticated user profile and authorized role.

- **Headers**: `Authorization: Bearer <TOKEN>`
- **Response `200 OK`**:
  ```json
  {
    "id": "AUTH001",
    "email": "priya.sharma@email.com",
    "full_name": "Priya Sharma",
    "role": "author",
    "author_id": "AUTH001"
  }
  ```

---

### 3.2 Author Portal (`/api/v1/author`)
*All author endpoints require `Authorization: Bearer <TOKEN>` with role `author`.*

#### `GET /api/v1/author/profile`
Retrieve author profile and aggregated sales & royalty metrics across all published titles.

- **Response `200 OK`**:
  ```json
  {
    "id": "AUTH001",
    "author_id": "AUTH001",
    "name": "Priya Sharma",
    "email": "priya.sharma@email.com",
    "phone": "+91-98765-43210",
    "city": "Mumbai",
    "joined_date": "2023-03-15",
    "total_books": 2,
    "total_copies_sold": 531,
    "total_royalties_earned": "19908.00",
    "total_royalties_paid": "16338.00",
    "total_royalties_pending": "3570.00"
  }
  ```

---

#### `GET /api/v1/author/books`
List all books belonging exclusively to the authenticated author.

- **Response `200 OK`**: Array of `BookResponse` objects.

---

#### `GET /api/v1/author/books/{book_id}`
Retrieve details for a specific book.

- **Tenant Isolation**: Returns `404 Not Found` if the requested book belongs to another author.

---

#### `GET /api/v1/author/royalties`
Retrieve itemized royalty calculations per book and total balances.

- **Response `200 OK`**:
  ```json
  {
    "author_id": "AUTH001",
    "total_books": 2,
    "total_copies_sold": 531,
    "total_royalty_earned": "19908.00",
    "total_royalty_paid": "16338.00",
    "total_royalty_pending": "3570.00",
    "books": [
      {
        "book_id": "BK001",
        "title": "Whispers of the Ganges",
        "isbn": "978-93-5XXXX-01-1",
        "genre": "Literary Fiction",
        "status": "Published & Live",
        "mrp": "399.00",
        "royalty_per_copy": "35.00",
        "total_copies_sold": 342,
        "total_royalty_earned": "11970.00",
        "royalty_paid": "8400.00",
        "royalty_pending": "3570.00",
        "last_payout_date": "2025-10-15"
      }
    ]
  }
  ```

---

#### `POST /api/v1/author/tickets`
Submit a support ticket.

- **Request Body**:
  ```json
  {
    "book_id": "BK001",
    "subject": "Missing Q4 Royalty Statement",
    "description": "Please share the PDF statement for Q4 royalties.",
    "category": "ROYALTY",
    "attachments": [
      {"filename": "bank_statement.pdf", "size": 104857}
    ]
  }
  ```
- **Validation & AI Governance (Tier 1 Ingestion)**:
  - `book_id` is optional (supports account-level tickets).
  - If `book_id` is specified, the system validates that the book belongs to the author (`400 Bad Request` if unowned).
  - Injected fields (`priority`, `status`, `assigned_to_id`, `role`) are discarded; status defaults to `OPEN` and priority to `MEDIUM`.
  - **Zero-Cost Heuristic Triage**: Ingestion operates strictly under Tier 1 rule heuristics ($0 cost, 0 external network requests, sub-millisecond response) with `status: "rule_engine"`. External Gemini LLM API calls are never triggered on public submission to eliminate DDoS bot spam and quota drain.
- **Response `201 Created`**: Returns `AuthorTicketResponse`.

---

#### `GET /api/v1/author/tickets`
List all tickets submitted by the authenticated author.

- **Query Parameters**: `skip` (default 0), `limit` (default 50).
- **Response `200 OK`**: Array of `AuthorTicketResponse` objects.

---

#### `GET /api/v1/author/tickets/{ticket_id}`
Retrieve full ticket conversation.

- **Tenant Isolation**: Returns `404 Not Found` if ticket belongs to another author.
- **Privacy Guarantee**: Internal admin notes are completely excluded from the response.

---

#### `POST /api/v1/author/tickets/{ticket_id}/messages`
Reply to a ticket thread.

- **Request Body**:
  ```json
  {
    "message_body": "Thank you, I will check with my bank.",
    "attachments": []
  }
  ```
- **Response `201 Created`**: Returns created `TicketMessageResponse`.

---

### 3.3 Administrative Portal (`/api/v1/admin`)
*All administrative endpoints require `Authorization: Bearer <TOKEN>` with role `admin`.*

#### `GET /api/v1/admin/tickets`
List tickets across all authors with filtering and search.

- **Query Parameters**:
  - `status`: Filter by `OPEN`, `IN_PROGRESS`, `RESOLVED`, `CLOSED`
  - `category`: Filter by category (e.g. `ROYALTY`, `PRINT_QUALITY`)
  - `priority`: Filter by `LOW`, `MEDIUM`, `HIGH`, `URGENT`
  - `assigned_to_id`: Filter by assigned staff ID
  - `date_from`, `date_to`: Filter by created date range (`YYYY-MM-DD`)
  - `search`: Keyword search across ticket number, subject, description, author name, and author email
  - `skip`, `limit`: Pagination parameters

---

#### `GET /api/v1/admin/tickets/{ticket_id}`
Get complete ticket details including associated author profile, book publication details, public messages, and **confidential internal notes**.

---

#### `PATCH /api/v1/admin/tickets/{ticket_id}/status`
Transition ticket status.

- **Request Body**:
  ```json
  {
    "status": "RESOLVED"
  }
  ```
- **Validation**: Rejects invalid statuses with `422 Unprocessable Content`. Sets `resolved_at` timestamp automatically.

---

#### `PATCH /api/v1/admin/tickets/{ticket_id}/triage`
Override category, priority, or AI classification metadata.

- **Request Body**:
  ```json
  {
    "category": "ROYALTY_ESCALATION",
    "priority": "URGENT",
    "ai_classification": {
      "confidence": 0.98,
      "urgency": "HIGH",
      "sentiment": "URGENT"
    }
  }
  ```

---

#### `PATCH /api/v1/admin/tickets/{ticket_id}/assign`
Assign ticket to an admin staff user.

- **Request Body**:
  ```json
  {
    "assigned_to_id": "USR_ADMIN_DEMO"
  }
  ```

---

#### `POST /api/v1/admin/tickets/{ticket_id}/notes`
Post a confidential internal note. Visible exclusively to administrative staff.

- **Request Body**:
  ```json
  {
    "note_body": "Escalated to Repro India regarding print streak issue on batch #8812."
  }
  ```
- **Response `201 Created`**: Returns `TicketInternalNoteResponse`.

---

#### `POST /api/v1/admin/tickets/{ticket_id}/messages`
Send an author-visible reply. Automatically transitions ticket status to `WAITING_ON_AUTHOR`.

- **Request Body**:
  ```json
  {
    "message_body": "Hello Priya, we have verified your account details and triggered the payout."
  }
  ```
- **Response `201 Created`**: Returns `TicketMessageResponse`.

---

#### `GET /api/v1/admin/admins`
List active administrative staff users for assignment dropdowns.

---

#### `POST /api/v1/admin/tickets/{ticket_id}/ai-draft`
Generate an on-demand AI response draft grounded in BookLeaf operational knowledge base policies (Tier 2 Gemini LLM Reasoning).

- **Headers**: `Authorization: Bearer <TOKEN>` (role `admin`)
- **Query / Body**: None (context is assembled server-side from author profile, book details, and message thread)
- **Anchored Conversation Window**:
  - Automatically isolates and preserves Message #1 (`[Author - Initial Inquiry]`) so the foundational author problem statement is never diluted or dropped.
  - Retains the most recent 9 chronological messages.
  - If the conversation exceeds 10 messages, inserts an explicit omission indicator: `[... X intermediate messages omitted for context focus ...]` to prevent LLM context saturation and reduce token overhead.
- **Response `200 OK`**:
  ```json
  {
    "draft_response": "Dear Priya,\n\nThank you for reaching out regarding your Q4 royalty statement...",
    "suggested_category": "ROYALTY",
    "suggested_priority": "MEDIUM",
    "priority_code": "P3",
    "confidence": 0.95,
    "reasoning": "Ticket concerns royalty payment timing. BookLeaf Policy POL-ROY-001 stipulates payouts occur on the 15th of each month with a INR 500 threshold.",
    "relevant_policies": ["POL-ROY-001: Royalty Calculation & Payment Schedule"],
    "status": "success",
    "model": "gemini-2.5-flash",
    "error_message": null,
    "created_at": "2026-10-22T10:00:00Z"
  }
  ```
- **Caching**: The generated draft, policy citations, and triage recommendations are cached in `ai_classification` on the ticket record to minimize redundant LLM token expenditures on repeated viewings.

---

#### `POST /api/v1/admin/tickets/{ticket_id}/ai-triage`
Run on-demand Gemini AI triage (category classification & priority assessment) without generating an author response draft.

- **Headers**: `Authorization: Bearer <TOKEN>` (role `admin`)
- **Query / Body**: None
- **Token Efficiency**: Ultra-lightweight prompt (~100 tokens vs. ~500 for a draft response), completing in ~300ms.
- **Response `200 OK`**:
  ```json
  {
    "category": "Printing & Quality",
    "priority": "High",
    "priority_code": "HIGH",
    "confidence": 0.95,
    "reasoning": "Author reports 50 defective copies with binding delamination. Aligns with Defect Policy POL-PRT-002.",
    "status": "success",
    "model": "gemini-2.5-flash",
    "created_at": "2026-10-24T00:45:00Z",
    "applicable_policies": [
      "Defect Warranty & Free Reprints: Verified defects qualify for expedited free replacement reprint."
    ]
  }
  ```

---

#### `POST /api/v1/admin/tickets/{ticket_id}/apply-ai-triage`
Apply the AI-suggested category and priority to the ticket record with a single operational click.

- **Headers**: `Authorization: Bearer <TOKEN>` (role `admin`)
- **Response `200 OK`**: Returns updated `AdminTicketResponse` with updated `category`, `priority`, and audit metadata (`applied_by_admin`, `applied_at`).

---

## 4. Error Responses

All error responses adhere to standard HTTP status codes and provide actionable JSON payloads without leaking internal system traces:

```json
{
  "detail": "Descriptive, client-safe error message."
}
```

Validation errors (`422 Unprocessable Content`) return structured field-level breakdowns:

```json
{
  "detail": "Invalid request payload or parameters.",
  "errors": [
    {
      "field": "body -> status",
      "message": "String should match pattern '^(OPEN|IN_PROGRESS|RESOLVED|CLOSED)$'",
      "type": "string_pattern_mismatch"
    }
  ]
}
```
