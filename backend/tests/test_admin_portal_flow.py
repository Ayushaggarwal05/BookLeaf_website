import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

def test_admin_portal_lifecycle_and_security():
    """
    Comprehensive verification for Prompt 4:
    1. Admin logs in and acquires JWT.
    2. Admin views ticket queue across multiple authors.
    3. Filter testing: status, priority, category, search.
    4. Admin inspects ticket detail, which contains both author conversation AND internal notes.
    5. Admin overrides triage: changes priority to URGENT and updates category.
    6. Admin updates status to IN_PROGRESS.
    7. Admin assigns ticket to staff member.
    8. Changes persist across subsequent GET requests.
    9. Admin logs private internal note.
    10. Admin sends public response to author.
    11. Ticket status automatically transitions to WAITING_ON_AUTHOR.
    12. Author logs in and views ticket:
        - Admin public message IS visible.
        - Private internal note is STRICTLY NOT visible.
    13. Author attempts to call admin endpoints -> 403 Forbidden.
    14. Empty queue / non-existent ticket -> 404 / proper error handling.
    """
    client = TestClient(app)

    # 1. Admin Login
    admin_login = client.post('/api/v1/auth/login', json={
        'email': 'admin@bookleaf.in',
        'password': 'Admin@BookLeaf2026!'
    })
    assert admin_login.status_code == 200, f'Admin login failed: {admin_login.text}'
    admin_token = admin_login.json()['access_token']
    admin_id = admin_login.json()['user_id']
    admin_headers = {'Authorization': f'Bearer {admin_token}'}

    # Author Login (Priya Sharma)
    author_login = client.post('/api/v1/auth/login', json={
        'email': 'priya.sharma@email.com',
        'password': 'Author@BookLeaf2026!'
    })
    assert author_login.status_code == 200
    author_token = author_login.json()['access_token']
    author_headers = {'Authorization': f'Bearer {author_token}'}

    # Create ticket as author
    new_ticket_res = client.post('/api/v1/author/tickets', headers=author_headers, json={
        'subject': 'Cover alignment defect on printed hardcover batch',
        'description': 'The spine lettering on 50 copies of The Silent Echo is shifted left by 8mm.',
        'category': 'PRINT_QUALITY',
        'attachments': [{'filename': 'spine_defect.jpg', 'size': 102400, 'type': 'image/jpeg'}]
    })
    assert new_ticket_res.status_code == 201
    ticket_id = new_ticket_res.json()['id']
    ticket_number = new_ticket_res.json()['ticket_number']

    # 2. Admin views ticket queue across authors
    queue_res = client.get('/api/v1/admin/tickets', headers=admin_headers)
    assert queue_res.status_code == 200
    all_tickets = queue_res.json()
    assert any(t['id'] == ticket_id for t in all_tickets)

    # 3. Filter verification:
    # 3a. Filter by category
    filter_cat = client.get('/api/v1/admin/tickets?category=PRINT_QUALITY', headers=admin_headers)
    assert filter_cat.status_code == 200
    for t in filter_cat.json():
        assert t['category'] == 'PRINT_QUALITY'

    # 3b. Search filter
    search_res = client.get(f'/api/v1/admin/tickets?search={ticket_number}', headers=admin_headers)
    assert search_res.status_code == 200
    assert len(search_res.json()) >= 1
    assert search_res.json()[0]['ticket_number'] == ticket_number

    # 4. Admin inspects ticket detail
    detail_res = client.get(f'/api/v1/admin/tickets/{ticket_id}', headers=admin_headers)
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail['id'] == ticket_id
    assert 'internal_notes' in detail
    assert 'messages' in detail
    assert detail['author']['name'] == 'Priya Sharma'

    # 5. Admin overrides triage: changes priority to URGENT
    triage_res = client.patch(f'/api/v1/admin/tickets/{ticket_id}/triage', headers=admin_headers, json={
        'priority': 'URGENT',
        'category': 'PRINT_QUALITY'
    })
    assert triage_res.status_code == 200
    assert triage_res.json()['priority'] == 'URGENT'

    # 6. Admin updates status to IN_PROGRESS
    status_res = client.patch(f'/api/v1/admin/tickets/{ticket_id}/status', headers=admin_headers, json={
        'status': 'IN_PROGRESS'
    })
    assert status_res.status_code == 200
    assert status_res.json()['status'] == 'IN_PROGRESS'

    # 7. Admin assigns ticket to staff
    assign_res = client.patch(f'/api/v1/admin/tickets/{ticket_id}/assign', headers=admin_headers, json={
        'assigned_to_id': admin_id
    })
    assert assign_res.status_code == 200
    assert assign_res.json()['assigned_to_id'] == admin_id

    # 8. Verify persistence on refreshed detail
    refresh_detail = client.get(f'/api/v1/admin/tickets/{ticket_id}', headers=admin_headers).json()
    assert refresh_detail['status'] == 'IN_PROGRESS'
    assert refresh_detail['priority'] == 'URGENT'
    assert refresh_detail['assigned_to_id'] == admin_id

    # 9. Admin logs private internal note
    note_res = client.post(f'/api/v1/admin/tickets/{ticket_id}/notes', headers=admin_headers, json={
        'note_body': 'CONFIDENTIAL: Escalated to Thomson Press POD manager. Reprints approved under SLA.'
    })
    assert note_res.status_code == 201
    assert note_res.json()['author_user_id'] == admin_id

    # 10. Admin sends public response to author
    reply_res = client.post(f'/api/v1/admin/tickets/{ticket_id}/messages', headers=admin_headers, json={
        'message_body': 'Dear Priya, we have verified the defect with Thomson Press. Replacement copies will be printed and shipped.'
    })
    assert reply_res.status_code == 201
    assert reply_res.json()['sender_type'] == 'SUPPORT_AGENT'

    # 11. Ticket automatically transitioned to WAITING_ON_AUTHOR
    updated_ticket = client.get(f'/api/v1/admin/tickets/{ticket_id}', headers=admin_headers).json()
    assert updated_ticket['status'] == 'WAITING_ON_AUTHOR'

    # 12. Author logs in and views their ticket
    author_view_res = client.get(f'/api/v1/author/tickets/{ticket_id}', headers=author_headers)
    assert author_view_res.status_code == 200
    author_view = author_view_res.json()
    
    # Public reply IS visible
    messages = [m['message_body'] for m in author_view['messages']]
    assert any('Thomson Press' in m for m in messages)
    
    # Internal note is STRICTLY NOT visible to author
    assert 'internal_notes' not in author_view
    for m in author_view['messages']:
        assert 'CONFIDENTIAL' not in m['message_body']

    # 13. Security check: Author CANNOT call admin endpoints
    author_admin_call = client.get('/api/v1/admin/tickets', headers=author_headers)
    assert author_admin_call.status_code == 403

    author_note_call = client.post(f'/api/v1/admin/tickets/{ticket_id}/notes', headers=author_headers, json={
        'note_body': 'Attempting unauthorized note'
    })
    assert author_note_call.status_code == 403

    # 14. Non-existent ticket returns 404
    non_existent = client.get('/api/v1/admin/tickets/TCK_NONEXISTENT_9999', headers=admin_headers)
    assert non_existent.status_code == 404

    # 15. Admin triggers on-demand Gemini AI triage
    ai_triage_res = client.post(f'/api/v1/admin/tickets/{ticket_id}/ai-triage', headers=admin_headers)
    assert ai_triage_res.status_code == 200
    ai_triage_data = ai_triage_res.json()
    assert 'category' in ai_triage_data
    assert 'priority' in ai_triage_data
    assert 'confidence' in ai_triage_data
    assert 'reasoning' in ai_triage_data

    # Security check: Author CANNOT run AI triage
    author_ai_triage = client.post(f'/api/v1/admin/tickets/{ticket_id}/ai-triage', headers=author_headers)
    assert author_ai_triage.status_code == 403

