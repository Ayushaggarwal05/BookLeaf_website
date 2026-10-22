import { describe, it, expect } from 'vitest';
import type { CreateTicketPayload, CreateMessagePayload } from '../ticket';

describe('Ticket Type Validation & Payloads', () => {
  it('constructs a valid CreateTicketPayload for book-specific query', () => {
    const payload: CreateTicketPayload = {
      book_id: 'bk_sharma_01',
      subject: 'Inquiry on royalty calculation for Q3',
      description: 'The sales report shows 150 copies sold on Amazon, but royalty seems calculated on 120.',
      category: 'ROYALTY',
      attachments: [{ filename: 'statement.pdf', size: 1048576, type: 'application/pdf' }],
    };

    expect(payload.book_id).toBe('bk_sharma_01');
    expect(payload.category).toBe('ROYALTY');
    expect(payload.attachments).toHaveLength(1);
    expect(payload.attachments?.[0].filename).toBe('statement.pdf');
  });

  it('constructs a valid CreateTicketPayload for general inquiry', () => {
    const payload: CreateTicketPayload = {
      book_id: null,
      subject: 'Updating author profile and biography',
      description: 'Requesting assistance in updating my author bio across distributor channels.',
      category: 'GENERAL_INQUIRY',
    };

    expect(payload.book_id).toBeNull();
    expect(payload.subject.length).toBeGreaterThanOrEqual(3);
  });

  it('constructs an author reply payload with optional attachments', () => {
    const reply: CreateMessagePayload = {
      message_body: 'Thank you for looking into this. Here is the scanned proof.',
      attachments: [{ filename: 'receipt.png', size: 204800, type: 'image/png' }],
    };

    expect(reply.message_body).toContain('scanned proof');
    expect(reply.attachments).toHaveLength(1);
  });
});
