import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

def test_frontend_author_flow():
    """
    Validates the exact sequence of REST API calls made by the React frontend:
    1. Login with author credentials
    2. Retrieve author profile metrics
    3. Retrieve author books catalog
    4. Retrieve author royalties breakdown
    5. Submit support query with book selection & attachment metadata
    6. Fetch author ticket list
    7. Fetch ticket detail and conversation thread
    8. Post author reply message to ticket
    9. Refresh ticket detail (polling simulation) and verify new message
    """
    client = TestClient(app)

    # 1. Login
    login_res = client.post('/api/v1/auth/login', json={
        'email': 'priya.sharma@email.com',
        'password': 'Author@BookLeaf2026!'
    })
    assert login_res.status_code == 200, f'Login failed: {login_res.text}'
    token_data = login_res.json()
    assert 'access_token' in token_data
    assert token_data['role'] == 'author'
    token = token_data['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # 2. Author Profile
    profile_res = client.get('/api/v1/author/profile', headers=headers)
    assert profile_res.status_code == 200
    profile = profile_res.json()
    assert profile['author_id'] == 'AUTH001'
    assert profile['total_books'] >= 1
    assert 'total_royalties_earned' in profile

    # 3. Author Books
    books_res = client.get('/api/v1/author/books', headers=headers)
    assert books_res.status_code == 200
    books = books_res.json()
    assert len(books) >= 1
    target_book_id = books[0]['id']

    # 4. Author Royalties Breakdown
    royalty_res = client.get('/api/v1/author/royalties', headers=headers)
    assert royalty_res.status_code == 200
    royalty = royalty_res.json()
    assert royalty['author_id'] == 'AUTH001'
    assert len(royalty['books']) == len(books)

    # 5. Create Ticket
    ticket_payload = {
        'book_id': target_book_id,
        'subject': 'Frontend E2E Test Query - Royalty Distribution',
        'description': 'Automated validation of support query submission from React frontend.',
        'category': 'ROYALTY',
        'attachments': [{'filename': 'audit_doc.pdf', 'size': 65400, 'type': 'application/pdf'}]
    }
    ticket_res = client.post('/api/v1/author/tickets', headers=headers, json=ticket_payload)
    assert ticket_res.status_code == 201, f'Create ticket failed: {ticket_res.text}'
    ticket = ticket_res.json()
    ticket_id = ticket['id']
    assert ticket['book_id'] == target_book_id
    assert ticket['status'] == 'OPEN'
    assert ticket['priority'] in ['LOW', 'MEDIUM', 'HIGH', 'URGENT']

    # 6. List Tickets
    list_res = client.get('/api/v1/author/tickets', headers=headers)
    assert list_res.status_code == 200
    tickets = list_res.json()
    assert any(t['id'] == ticket_id for t in tickets)

    # 7. Get Ticket Detail
    detail_res = client.get(f'/api/v1/author/tickets/{ticket_id}', headers=headers)
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail['id'] == ticket_id
    assert 'messages' in detail

    # 8. Post Reply Message
    reply_payload = {
        'message_body': 'Following up with distribution receipts.',
        'attachments': [{'filename': 'invoice_copy.png', 'size': 20480, 'type': 'image/png'}]
    }
    reply_res = client.post(f'/api/v1/author/tickets/{ticket_id}/messages', headers=headers, json=reply_payload)
    assert reply_res.status_code == 201
    reply = reply_res.json()
    assert reply['sender_type'] == 'AUTHOR'
    assert reply['message_body'] == reply_payload['message_body']

    # 9. Verify polling / detail contains the reply
    poll_res = client.get(f'/api/v1/author/tickets/{ticket_id}', headers=headers)
    assert poll_res.status_code == 200
    poll_detail = poll_res.json()
    assert len(poll_detail['messages']) >= 1
    assert any(m['id'] == reply['id'] for m in poll_detail['messages'])
