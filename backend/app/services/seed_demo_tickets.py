"""
Seed realistic demo tickets into BookLeaf Support Portal.
Includes diverse categories (Printing, Royalty, Distribution, ISBN, Production, General),
priorities (High, Medium, Low), statuses (Open, In Progress, Waiting on Author),
conversation threads, and internal staff notes.
"""

import sys
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Ensure workspace root is in sys.path
_backend_dir = Path(__file__).resolve().parent.parent.parent
_workspace_root = _backend_dir.parent
for p in [str(_workspace_root), str(_backend_dir)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from backend.app.core.database import SessionLocal
from backend.app.models.ticket import SupportTicket
from backend.app.models.ticket_message import TicketMessage
from backend.app.models.internal_note import TicketInternalNote
from backend.app.models.user import User


def seed_demo_tickets():
    db = SessionLocal()
    try:
        # Check existing count
        cnt = db.query(SupportTicket).count()
        if cnt > 0:
            print(f"Supabase already has {cnt} tickets. Cleaning previous tickets first...")
            db.query(TicketMessage).delete()
            db.query(TicketInternalNote).delete()
            db.query(SupportTicket).delete()
            db.commit()

        admin = db.query(User).filter(User.email == "admin@bookleaf.in").first()
        admin_id = admin.id if admin else "USR_ADMIN_DEMO"

        now = datetime.now(timezone.utc)

        sample_tickets = [
            {
                "ticket_number": "TCK-2026-1001",
                "author_id": "AUTH001",
                "book_id": "BK001",
                "subject": "Cover alignment defect on printed hardcover batch",
                "description": (
                    "I received my author copies today. The cover print is noticeably blurry and the spine "
                    "lettering is shifted left by 8mm on 50 books. About 15 copies also have pages 45-60 bound "
                    "upside down. Need replacement copies before my launch event next weekend."
                ),
                "category": "Printing & Quality",
                "priority": "HIGH",
                "status": "OPEN",
                "created_at": now - timedelta(hours=3),
                "author_name": "Priya Sharma",
                "messages": [
                    {
                        "sender_type": "AUTHOR",
                        "sender_name": "Priya Sharma",
                        "sender_id": "AUTH001",
                        "body": (
                            "I received my author copies today. The cover print is noticeably blurry and the spine "
                            "lettering is shifted left by 8mm on 50 books. About 15 copies also have pages 45-60 bound "
                            "upside down. Need replacement copies before my launch event next weekend."
                        ),
                        "created_at": now - timedelta(hours=3),
                    }
                ],
                "notes": [],
            },
            {
                "ticket_number": "TCK-2026-1002",
                "author_id": "AUTH002",
                "book_id": "BK003",
                "subject": "September quarter royalty payout delay",
                "description": (
                    "I have not received my royalty payout for the quarter ending September. The author dashboard "
                    "shows Rs. 5,280 pending. The 45-day post-quarter deadline has passed. When will this amount "
                    "be credited to my bank account?"
                ),
                "category": "Royalty & Payments",
                "priority": "HIGH",
                "status": "OPEN",
                "created_at": now - timedelta(hours=6),
                "author_name": "Rohit Kapoor",
                "messages": [
                    {
                        "sender_type": "AUTHOR",
                        "sender_name": "Rohit Kapoor",
                        "sender_id": "AUTH002",
                        "body": (
                            "I have not received my royalty payout for the quarter ending September. The author dashboard "
                            "shows Rs. 5,280 pending. The 45-day post-quarter deadline has passed. When will this amount "
                            "be credited to my bank account?"
                        ),
                        "created_at": now - timedelta(hours=6),
                    }
                ],
                "notes": [],
            },
            {
                "ticket_number": "TCK-2026-1003",
                "author_id": "AUTH003",
                "book_id": "BK005",
                "subject": "Book showing Currently Unavailable on Amazon India",
                "description": (
                    "A reader notified me this morning that Between Two Temples is showing Currently Unavailable "
                    "on Amazon India, although it was live last week. Could you please check if there is an automated "
                    "stock feed sync delay with the distributor?"
                ),
                "category": "Distribution & Availability",
                "priority": "MEDIUM",
                "status": "IN_PROGRESS",
                "created_at": now - timedelta(hours=14),
                "author_name": "Ananya Reddy",
                "messages": [
                    {
                        "sender_type": "AUTHOR",
                        "sender_name": "Ananya Reddy",
                        "sender_id": "AUTH003",
                        "body": (
                            "A reader notified me this morning that Between Two Temples is showing Currently Unavailable "
                            "on Amazon India, although it was live last week. Could you please check if there is an automated "
                            "stock feed sync delay with the distributor?"
                        ),
                        "created_at": now - timedelta(hours=14),
                    },
                    {
                        "sender_type": "SUPPORT_AGENT",
                        "sender_name": "BookLeaf Operations",
                        "sender_id": admin_id,
                        "body": (
                            "Hi Ananya, thank you for reaching out. We verified that our Delhi warehouse has stock "
                            "available. We have triggered a manual catalog re-sync with Amazon India, which typically "
                            "updates within 24 to 48 hours."
                        ),
                        "created_at": now - timedelta(hours=10),
                    },
                ],
                "notes": [
                    {
                        "note_body": "Triggered automated stock EDI refresh to Amazon India seller portal. Ref ID: EDI-AMZ-99412.",
                        "created_at": now - timedelta(hours=10),
                    }
                ],
            },
            {
                "ticket_number": "TCK-2026-1004",
                "author_id": "AUTH004",
                "book_id": "BK007",
                "subject": "Title misspelling on retail catalog and outdated author bio",
                "description": (
                    "My book title on retail channels has a typo in the sub-genre header and my author bio still "
                    "references my 2022 employer. Please update these metadata fields across Amazon and Flipkart."
                ),
                "category": "ISBN & Metadata Issues",
                "priority": "HIGH",
                "status": "OPEN",
                "created_at": now - timedelta(hours=20),
                "author_name": "Vikram Joshi",
                "messages": [
                    {
                        "sender_type": "AUTHOR",
                        "sender_name": "Vikram Joshi",
                        "sender_id": "AUTH004",
                        "body": (
                            "My book title on retail channels has a typo in the sub-genre header and my author bio still "
                            "references my 2022 employer. Please update these metadata fields across Amazon and Flipkart."
                        ),
                        "created_at": now - timedelta(hours=20),
                    }
                ],
                "notes": [],
            },
            {
                "ticket_number": "TCK-2026-1005",
                "author_id": "AUTH005",
                "book_id": "BK008",
                "subject": "Manuscript status in Proofreading stage",
                "description": (
                    "My manuscript has been in Proofreading status for over three weeks. I wanted to verify if any "
                    "revision rounds are pending on my end, or if we are ready to move into typesetting and ISBN assignment."
                ),
                "category": "Book Status & Production Updates",
                "priority": "MEDIUM",
                "status": "WAITING_ON_AUTHOR",
                "created_at": now - timedelta(days=2),
                "author_name": "Meera Nair",
                "messages": [
                    {
                        "sender_type": "AUTHOR",
                        "sender_name": "Meera Nair",
                        "sender_id": "AUTH005",
                        "body": (
                            "My manuscript has been in Proofreading status for over three weeks. I wanted to verify if any "
                            "revision rounds are pending on my end, or if we are ready to move into typesetting and ISBN assignment."
                        ),
                        "created_at": now - timedelta(days=2),
                    },
                    {
                        "sender_type": "SUPPORT_AGENT",
                        "sender_name": "Editorial Team",
                        "sender_id": admin_id,
                        "body": (
                            "Dear Meera, our editorial team completed the second proofreading pass and sent the layout proof "
                            "to your email on Tuesday. Please review the layout proof and confirm your approval so we can "
                            "proceed to ISBN assignment."
                        ),
                        "created_at": now - timedelta(days=1),
                    },
                ],
                "notes": [
                    {
                        "note_body": "Awaiting Meera's signed approval on proofreading layout proof #2 sent via DocuSign.",
                        "created_at": now - timedelta(days=1),
                    }
                ],
            },
            {
                "ticket_number": "TCK-2026-1006",
                "author_id": "AUTH006",
                "book_id": None,
                "subject": "Inquiry on Bestseller Breakthrough package upgrade",
                "description": (
                    "I am currently preparing my next manuscript under the Standard Free publishing package. "
                    "What marketing, distribution add-ons, and ISBN features are included in the Bestseller Breakthrough package?"
                ),
                "category": "General Inquiry",
                "priority": "LOW",
                "status": "OPEN",
                "created_at": now - timedelta(days=3),
                "author_name": "Arjun Malhotra",
                "messages": [
                    {
                        "sender_type": "AUTHOR",
                        "sender_name": "Arjun Malhotra",
                        "sender_id": "AUTH006",
                        "body": (
                            "I am currently preparing my next manuscript under the Standard Free publishing package. "
                            "What marketing, distribution add-ons, and ISBN features are included in the Bestseller Breakthrough package?"
                        ),
                        "created_at": now - timedelta(days=3),
                    }
                ],
                "notes": [],
            },
        ]

        for t_data in sample_tickets:
            t_id = f"TCK_{uuid.uuid4().hex[:10].upper()}"
            ticket = SupportTicket(
                id=t_id,
                ticket_number=t_data["ticket_number"],
                author_id=t_data["author_id"],
                book_id=t_data["book_id"],
                subject=t_data["subject"],
                description=t_data["description"],
                category=t_data["category"],
                priority=t_data["priority"],
                status=t_data["status"],
                assigned_to_id=admin_id if t_data["status"] in ("IN_PROGRESS", "WAITING_ON_AUTHOR") else None,
                attachments=[],
                created_at=t_data["created_at"],
                updated_at=now,
            )
            db.add(ticket)
            db.flush()

            for m in t_data["messages"]:
                msg = TicketMessage(
                    id=f"MSG_{uuid.uuid4().hex[:10].upper()}",
                    ticket_id=ticket.id,
                    sender_type=m["sender_type"],
                    sender_id=m["sender_id"],
                    sender_name=m["sender_name"],
                    message_body=m["body"],
                    attachments=[],
                    created_at=m["created_at"],
                    updated_at=m["created_at"],
                )
                db.add(msg)

            for n in t_data["notes"]:
                note = TicketInternalNote(
                    id=f"NOTE_{uuid.uuid4().hex[:10].upper()}",
                    ticket_id=ticket.id,
                    author_user_id=admin_id,
                    note_body=n["note_body"],
                    created_at=n["created_at"],
                    updated_at=n["created_at"],
                )
                db.add(note)

        db.commit()
        print(f"SUCCESS: Seeded {len(sample_tickets)} realistic tickets into Supabase!")
        return len(sample_tickets)

    except Exception as exc:
        db.rollback()
        print(f"ERROR: Failed to seed demo tickets: {exc}", file=sys.stderr)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_tickets()
