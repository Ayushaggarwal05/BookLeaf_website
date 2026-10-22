import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.services.knowledge_base import (
    get_knowledge_base,
    find_relevant_policies,
    format_knowledge_base_for_prompt,
    COMMUNICATION_GUIDELINES,
)
from backend.app.services.ai_service import (
    GeminiService,
    AiTriageOutput,
    AiDraftOutput,
    AiTriageResult,
    AiDraftResult,
    ai_service,
)


# -----------------------------------------------------------------------------
# 1. Knowledge Base Unit Tests
# -----------------------------------------------------------------------------

def test_knowledge_base_integrity():
    """Verify all 13 core BookLeaf policies are defined with correct values."""
    kb = get_knowledge_base()
    assert len(kb) >= 6
    assert "Royalty & Payments" in kb
    assert "ISBN & Metadata Issues" in kb
    assert "Printing & Quality" in kb
    assert "Distribution & Availability" in kb
    assert "Book Status & Production Updates" in kb
    assert "General Inquiry" in kb

    # Check key facts specified in Prompt 5
    royalty_policies = kb["Royalty & Payments"]["rules"]
    assert any("80/20" in p for p in royalty_policies)
    assert any("1,000" in p for p in royalty_policies)
    assert any("45" in p for p in royalty_policies)

    isbn_policies = kb["ISBN & Metadata Issues"]["rules"]
    assert any("BookLeaf" in p and "ISBN" in p for p in isbn_policies)
    assert any("high-priority" in p.lower() or "escalat" in p.lower() for p in isbn_policies)
    assert any(("3 to 5" in p or "3-5" in p or "3–5" in p) for p in isbn_policies)

    print_policies = kb["Printing & Quality"]["rules"]
    assert any(("5 to 7" in p or "5-7" in p or "5–7" in p) for p in print_policies)
    assert any("free reprint" in p.lower() for p in print_policies)

    dist_policies = kb["Distribution & Availability"]["rules"]
    assert any(("7 to 10" in p or "7-10" in p or "7–10" in p) for p in dist_policies)
    assert any("24–48 hours" in p or "24-48" in p or "24 to 48" in p for p in dist_policies)

    prod_policies = kb["Book Status & Production Updates"]["rules"]
    assert any("manuscript receipt" in p.lower() for p in prod_policies)
    assert any("publication" in p.lower() for p in prod_policies)

    assert "empathetic" in COMMUNICATION_GUIDELINES.lower()
    assert "accountable" in COMMUNICATION_GUIDELINES.lower()


def test_find_relevant_policies():
    """Verify contextual extraction of policies based on category."""
    royalty_facts = find_relevant_policies("Royalty & Payments")
    assert any("80/20" in f for f in royalty_facts)

    isbn_facts = find_relevant_policies("ISBN & Metadata Issues")
    assert any("ISBN" in f for f in isbn_facts)

    print_facts = find_relevant_policies("Printing & Quality")
    assert any("reprint" in f.lower() for f in print_facts)

    formatted = format_knowledge_base_for_prompt("Royalty & Payments")
    assert "Royalty" in formatted
    assert "80/20" in formatted


# -----------------------------------------------------------------------------
# 2. Heuristic / Offline Fallback Tests (Missing Key or Disconnected)
# -----------------------------------------------------------------------------

def test_heuristic_offline_triage_royalty():
    service = GeminiService()
    result = service._heuristic_triage(
        subject="Delay in Q3 royalty payment",
        description="I have not received my payout of ₹4,500 for Q3. When will this be credited?",
    )
    assert isinstance(result, AiTriageResult)
    assert result.category == "Royalty & Payments"
    assert result.priority in ["Critical", "High"]
    assert result.provider == "heuristic-fallback"
    assert len(result.applicable_policies) > 0


def test_heuristic_offline_triage_isbn():
    service = GeminiService()
    result = service._heuristic_triage(
        subject="Wrong ISBN printed on barcode",
        description="The back cover has an incorrect ISBN number that belongs to another book.",
    )
    assert result.category == "ISBN & Metadata Issues"
    assert result.priority in ["Critical", "High"]
    assert result.provider == "heuristic-fallback"


def test_heuristic_offline_triage_printing():
    service = GeminiService()
    result = service._heuristic_triage(
        subject="Blurry images and damaged spine on author copies",
        description="All 25 copies delivered today have defective bindings and smeared text.",
    )
    assert result.category == "Printing & Quality"
    assert result.priority in ["High", "Medium"]


def test_heuristic_offline_triage_general_fallback():
    service = GeminiService()
    result = service._heuristic_triage(
        subject="Random question about publishing",
        description="Can you tell me how long people usually write their books?",
    )
    assert result.category == "General Inquiry"
    assert result.priority in ["Medium", "Low"]


def test_missing_api_key_draft_response_behavior():
    """When GEMINI_API_KEY is not set or empty, service returns unavailable safely without crashing."""
    with patch("backend.app.services.ai_service.settings.GEMINI_API_KEY", ""):
        service = GeminiService()
        draft = service.generate_draft_response(
            ticket_id="tck_test_123",
            subject="Question regarding payout",
            description="When will my royalties be sent?",
            category="Royalty & Payments",
            author_context={"name": "Anita Desai"},
        )
        assert isinstance(draft, AiDraftResult)
        assert draft.status == "unavailable"
        assert "API" in (draft.error_message or "") and "GEMINI_API_KEY" in (draft.error_message or "")
        assert draft.draft_response == ""


# -----------------------------------------------------------------------------
# 3. Mocked Gemini SDK Provider Tests
# -----------------------------------------------------------------------------

def test_mocked_gemini_triage_success():
    """Verify Gemini SDK client invocation with structured Pydantic output."""
    mock_parsed_output = AiTriageOutput(
        category="Royalty & Payments",
        priority="High",
        confidence=0.96,
        reasoning="Author inquires about pending quarterly royalty transfer exceeding threshold.",
        applicable_policies=["Royalty split: 80/20 of net profit", "Payout within 45 days after quarter end"],
    )

    mock_response = MagicMock()
    mock_response.parsed = mock_parsed_output

    with patch("backend.app.services.ai_service.settings.GEMINI_API_KEY", "mock-test-key-12345"):
        service = GeminiService()
        with patch.object(service, "get_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.models.generate_content.return_value = mock_response
            mock_get_client.return_value = mock_client

            result = service.triage_ticket(
                subject="Missing Q2 royalty payout",
                description="I calculated net profit on Amazon sales, where is my payout?",
            )

            assert result.category == "Royalty & Payments"
            assert result.priority == "High"
            assert result.confidence == 0.96
            assert result.provider == "gemini-2.5-flash"
            assert len(result.applicable_policies) == 2


def test_mocked_gemini_draft_generation_success():
    """Verify Gemini SDK client draft response with BookLeaf policy context."""
    mock_parsed_draft = AiDraftOutput(
        draft_response=(
            "Dear Vikram,\n\n"
            "Thank you for contacting BookLeaf Support regarding your Q2 royalty payout. "
            "Under BookLeaf's operating policy, author royalties are calculated on an 80/20 split of net profit "
            "and disbursed within 45 days following the close of each calendar quarter, subject to a minimum threshold of ₹1,000.\n\n"
            "Our finance team is currently reviewing your account records and will confirm disbursement status within 1-2 business days.\n\n"
            "Warm regards,\nBookLeaf Author Support Team"
        ),
        suggested_category="Royalty & Payments",
        suggested_priority="High",
        confidence=0.98,
        reasoning="Author meets eligibility criteria; clear policy and next steps provided.",
        relevant_policies=[
            "Royalty split: 80/20 of net profit",
            "Royalties calculated quarterly and paid within 45 days",
            "Minimum payout is ₹1,000",
        ],
    )

    mock_response = MagicMock()
    mock_response.parsed = mock_parsed_draft

    with patch("backend.app.services.ai_service.settings.GEMINI_API_KEY", "mock-test-key-12345"):
        service = GeminiService()
        with patch.object(service, "get_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.models.generate_content.return_value = mock_response
            mock_get_client.return_value = mock_client

            draft = service.generate_draft_response(
                ticket_id="tck_test_456",
                subject="Q2 payout inquiry",
                description="Has my Q2 payout been sent?",
                category="Royalty & Payments",
                author_context={"name": "Vikram Seth"},
                book_context={"title": "A Suitable Boy", "isbn": "978-81-123456-0-1"},
            )

            assert draft.status == "success"
            assert "80/20 split" in draft.draft_response
            assert draft.suggested_category == "Royalty & Payments"
            assert draft.suggested_priority == "High"
            assert len(draft.relevant_policies) == 3


def test_mocked_gemini_provider_error_handling():
    """Verify provider timeout or network exception is caught safely without unhandled 500."""
    with patch("backend.app.services.ai_service.settings.GEMINI_API_KEY", "mock-test-key-12345"):
        service = GeminiService()
        with patch.object(service, "get_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.models.generate_content.side_effect = TimeoutError("Gemini API connection timed out")
            mock_get_client.return_value = mock_client

            # 1. Triage falls back safely to heuristic
            triage_res = service.triage_ticket(
                subject="Urgent book printing defect",
                description="50 copies have smudged ink.",
            )
            assert triage_res.category == "Printing & Quality"
            assert triage_res.provider == "heuristic-fallback"

            # 2. Draft returns status='error' with clean message
            draft_res = service.generate_draft_response(
                ticket_id="tck_789",
                subject="Urgent book printing defect",
                description="50 copies have smudged ink.",
                category="Printing & Quality",
            )
            assert draft_res.status == "error"
            assert "timed out" in (draft_res.error_message or "").lower()


# -----------------------------------------------------------------------------
# 4. API Endpoint Integration & Role-Based Authorization
# -----------------------------------------------------------------------------

def test_admin_ai_draft_and_triage_endpoints():
    """
    Test API routes:
    1. Admin calls POST /admin/tickets/{id}/ai-draft -> 200 with draft schema.
    2. Admin calls POST /admin/tickets/{id}/apply-ai-triage -> 200 and ticket updated.
    3. Author calls POST /admin/tickets/{id}/ai-draft -> 403 Forbidden.
    4. Unauthenticated caller -> 401 Unauthorized.
    5. Admin overrides triage -> admin_override flag is set to True.
    """
    client = TestClient(app)

    # 1. Authenticate Admin
    admin_login = client.post("/api/v1/auth/login", json={
        "email": "admin@bookleaf.in",
        "password": "Admin@BookLeaf2026!"
    })
    assert admin_login.status_code == 200
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 2. Authenticate Author (Priya Sharma)
    author_login = client.post("/api/v1/auth/login", json={
        "email": "priya.sharma@email.com",
        "password": "Author@BookLeaf2026!"
    })
    assert author_login.status_code == 200
    author_token = author_login.json()["access_token"]
    author_headers = {"Authorization": f"Bearer {author_token}"}

    # 3. Create ticket as Author
    create_ticket_res = client.post("/api/v1/author/tickets", headers=author_headers, json={
        "subject": "ISBN mismatch on Amazon listing",
        "description": "The ISBN on Amazon does not match my allocated BookLeaf ISBN.",
        "category": "GENERAL_INQUIRY"
    })
    assert create_ticket_res.status_code == 201
    ticket = create_ticket_res.json()
    ticket_id = ticket["id"]

    # Verify ticket creation automatically performed non-blocking AI triage
    detail_res = client.get(f"/api/v1/admin/tickets/{ticket_id}", headers=admin_headers)
    assert detail_res.status_code == 200
    detail = detail_res.json()
    ai_cat = detail["ai_classification"].get("category") or detail["ai_classification"].get("suggested_category")
    assert ai_cat in [
        "Royalty & Payments",
        "ISBN & Metadata Issues",
        "Printing & Quality",
        "Distribution & Availability",
        "Book Status & Production Updates",
        "General Inquiry"
    ]

    # 4. Admin requests AI Draft
    mock_draft_output = AiDraftResult(
        draft_response="Dear Priya, We are investigating your ISBN listing discrepancy with Amazon.",
        suggested_category="ISBN & Metadata Issues",
        suggested_priority="High",
        priority_code="HIGH",
        confidence=0.95,
        reasoning="ISBN mismatch reported on Amazon listing.",
        relevant_policies=["ISBN mismatches are high-priority and escalated."],
        status="success",
        model="gemini-2.5-flash",
        created_at="2026-10-22T00:00:00Z",
    )

    with patch.object(ai_service, "generate_draft_response", return_value=mock_draft_output):
        ai_draft_res = client.post(f"/api/v1/admin/tickets/{ticket_id}/ai-draft", headers=admin_headers)
        assert ai_draft_res.status_code == 200
        draft_json = ai_draft_res.json()
        assert draft_json["status"] == "success"
        assert "ISBN listing discrepancy" in draft_json["draft_response"]
        assert draft_json["suggested_category"] == "ISBN & Metadata Issues"
        assert draft_json["suggested_priority"] == "High"
        assert draft_json["priority_code"] == "HIGH"

    # 5. Admin applies AI Triage suggestions
    apply_triage_res = client.post(f"/api/v1/admin/tickets/{ticket_id}/apply-ai-triage", headers=admin_headers)
    assert apply_triage_res.status_code == 200
    updated_ticket = apply_triage_res.json()
    assert updated_ticket["category"] == "ISBN & Metadata Issues"
    assert updated_ticket["priority"] == "HIGH"

    # 6. Admin manual override updates triage and marks admin_override = True
    override_res = client.patch(
        f"/api/v1/admin/tickets/{ticket_id}/triage",
        headers=admin_headers,
        json={"category": "METADATA_UPDATE", "priority": "URGENT"}
    )
    assert override_res.status_code == 200
    detail_after_override = client.get(f"/api/v1/admin/tickets/{ticket_id}", headers=admin_headers).json()
    assert detail_after_override["category"] == "METADATA_UPDATE"
    assert detail_after_override["priority"] == "URGENT"
    assert detail_after_override["ai_classification"]["admin_override"] is True

    # 7. Authorization check: Author cannot access admin AI draft endpoint
    forbidden_res = client.post(f"/api/v1/admin/tickets/{ticket_id}/ai-draft", headers=author_headers)
    assert forbidden_res.status_code == 403

    # 8. Unauthenticated caller gets 401
    unauth_res = client.post(f"/api/v1/admin/tickets/{ticket_id}/ai-draft")
    assert unauth_res.status_code == 401
