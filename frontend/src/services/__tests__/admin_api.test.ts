import { describe, it, expect, beforeEach, vi } from 'vitest';
import { api } from '../api';

describe('Admin API Client Service', () => {
  let mockStorage: Record<string, string> = {};

  beforeEach(() => {
    vi.restoreAllMocks();
    mockStorage = {
      bookleaf_token: 'admin-jwt-token-999',
    };

    const localStorageMock = {
      getItem: vi.fn((key: string) => mockStorage[key] || null),
      setItem: vi.fn((key: string, val: string) => {
        mockStorage[key] = val;
      }),
      removeItem: vi.fn((key: string) => {
        delete mockStorage[key];
      }),
      clear: vi.fn(() => {
        mockStorage = {};
      }),
    };
    vi.stubGlobal('localStorage', localStorageMock);
    vi.stubGlobal('window', {
      dispatchEvent: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
    });
  });

  it('builds query parameters correctly for getTickets', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => [{ id: 'tck_1', subject: 'Urgent Issue', priority: 'URGENT' }],
    });
    vi.stubGlobal('fetch', mockFetch);

    await api.admin.getTickets({
      status: 'OPEN',
      priority: 'URGENT',
      category: 'ROYALTY',
      search: 'Priya',
      skip: 0,
      limit: 20,
    });

    expect(mockFetch).toHaveBeenCalledOnce();
    const calledUrl: string = mockFetch.mock.calls[0][0];
    expect(calledUrl).toContain('/admin/tickets?');
    expect(calledUrl).toContain('status=OPEN');
    expect(calledUrl).toContain('priority=URGENT');
    expect(calledUrl).toContain('category=ROYALTY');
    expect(calledUrl).toContain('search=Priya');
    expect(calledUrl).toContain('skip=0');
    expect(calledUrl).toContain('limit=20');
  });

  it('sends PATCH request to update ticket status', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ id: 'tck_1', status: 'IN_PROGRESS' }),
    });
    vi.stubGlobal('fetch', mockFetch);

    const res = await api.admin.updateStatus('tck_1', { status: 'IN_PROGRESS' });

    expect(mockFetch).toHaveBeenCalledOnce();
    const calledUrl: string = mockFetch.mock.calls[0][0];
    const calledOptions: RequestInit = mockFetch.mock.calls[0][1];

    expect(calledUrl).toContain('/admin/tickets/tck_1/status');
    expect(calledOptions.method).toBe('PATCH');
    expect(JSON.parse(calledOptions.body as string)).toEqual({ status: 'IN_PROGRESS' });
    expect(res.status).toBe('IN_PROGRESS');
  });

  it('sends POST request to log internal admin note', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 201,
      json: async () => ({
        id: 'note_1',
        ticket_id: 'tck_1',
        note_body: 'Investigated with print partner.',
      }),
    });
    vi.stubGlobal('fetch', mockFetch);

    const res = await api.admin.addNote('tck_1', {
      note_body: 'Investigated with print partner.',
    });

    expect(mockFetch).toHaveBeenCalledOnce();
    const calledUrl: string = mockFetch.mock.calls[0][0];
    const calledOptions: RequestInit = mockFetch.mock.calls[0][1];

    expect(calledUrl).toContain('/admin/tickets/tck_1/notes');
    expect(calledOptions.method).toBe('POST');
    expect(JSON.parse(calledOptions.body as string)).toEqual({
      note_body: 'Investigated with print partner.',
    });
    expect(res.id).toBe('note_1');
  });

  it('sends POST request to send author reply', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 201,
      json: async () => ({
        id: 'msg_1',
        ticket_id: 'tck_1',
        sender_type: 'SUPPORT_AGENT',
        message_body: 'We have reprinted your copy.',
      }),
    });
    vi.stubGlobal('fetch', mockFetch);

    const res = await api.admin.sendMessage('tck_1', {
      message_body: 'We have reprinted your copy.',
      attachments: [{ filename: 'receipt.pdf' }],
    });

    expect(mockFetch).toHaveBeenCalledOnce();
    const calledUrl: string = mockFetch.mock.calls[0][0];
    const calledOptions: RequestInit = mockFetch.mock.calls[0][1];

    expect(calledUrl).toContain('/admin/tickets/tck_1/messages');
    expect(calledOptions.method).toBe('POST');
    expect(res.sender_type).toBe('SUPPORT_AGENT');
  });

  it('sends POST request to generate AI draft response', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        draft_response: 'Dear Author, regarding your royalty query...',
        suggested_category: 'Royalty & Payments',
        suggested_priority: 'High',
        priority_code: 'HIGH',
        confidence: 0.95,
        reasoning: 'Ticket asks about Q2 royalty calculation',
        relevant_policies: ['Royalty Split: 80/20 net profit'],
        status: 'success',
        model: 'gemini-2.5-flash',
        created_at: new Date().toISOString(),
      }),
    });
    vi.stubGlobal('fetch', mockFetch);

    const res = await api.admin.generateAiDraft('tck_1');

    expect(mockFetch).toHaveBeenCalledOnce();
    const calledUrl: string = mockFetch.mock.calls[0][0];
    const calledOptions: RequestInit = mockFetch.mock.calls[0][1];

    expect(calledUrl).toContain('/admin/tickets/tck_1/ai-draft');
    expect(calledOptions.method).toBe('POST');
    expect(res.status).toBe('success');
    expect(res.draft_response).toContain('Dear Author');
    expect(res.suggested_category).toBe('Royalty & Payments');
  });

  it('sends POST request to apply AI triage suggestions', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        id: 'tck_1',
        category: 'Royalty & Payments',
        priority: 'HIGH',
      }),
    });
    vi.stubGlobal('fetch', mockFetch);

    const res = await api.admin.applyAiTriage('tck_1');

    expect(mockFetch).toHaveBeenCalledOnce();
    const calledUrl: string = mockFetch.mock.calls[0][0];
    const calledOptions: RequestInit = mockFetch.mock.calls[0][1];

    expect(calledUrl).toContain('/admin/tickets/tck_1/apply-ai-triage');
    expect(calledOptions.method).toBe('POST');
    expect(res.category).toBe('Royalty & Payments');
    expect(res.priority).toBe('HIGH');
  });
});
