import { describe, it, expect, beforeEach, vi } from 'vitest';
import { api, ApiError } from '../api';

describe('API Client Service', () => {
  let mockStorage: Record<string, string> = {};
  const mockEventTarget = new EventTarget();

  beforeEach(() => {
    vi.restoreAllMocks();
    mockStorage = {};

    // Mock localStorage
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

    // Mock window & CustomEvent
    vi.stubGlobal('CustomEvent', class MockCustomEvent extends Event {
      detail: any;
      constructor(type: string, eventInitDict?: CustomEventInit) {
        super(type, eventInitDict);
        this.detail = eventInitDict?.detail;
      }
    });

    vi.stubGlobal('window', {
      dispatchEvent: vi.fn((event: Event) => mockEventTarget.dispatchEvent(event)),
      addEventListener: vi.fn((type: string, listener: any) => mockEventTarget.addEventListener(type, listener)),
      removeEventListener: vi.fn((type: string, listener: any) => mockEventTarget.removeEventListener(type, listener)),
    });
  });

  it('attaches Bearer authorization token when stored in localStorage', async () => {
    localStorage.setItem('bookleaf_token', 'test-jwt-token-123');

    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ id: 'usr_1', email: 'author@bookleaf.in' }),
    });
    vi.stubGlobal('fetch', mockFetch);

    await api.auth.getMe();

    expect(mockFetch).toHaveBeenCalledOnce();
    const calledUrl = mockFetch.mock.calls[0][0];
    const calledOptions = mockFetch.mock.calls[0][1];

    expect(calledUrl).toContain('/auth/me');
    expect(calledOptions.headers.get('Authorization')).toBe('Bearer test-jwt-token-123');
  });

  it('throws ApiError with server error details on failed responses', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 400,
      statusText: 'Bad Request',
      json: async () => ({ detail: 'Selected book is not in your catalog.' }),
    });
    vi.stubGlobal('fetch', mockFetch);

    await expect(
      api.author.createTicket({
        subject: 'Invalid Ticket',
        description: 'Test description',
        book_id: 'bk_unowned',
      })
    ).rejects.toThrow('Selected book is not in your catalog.');
  });

  it('cleans up token and dispatches bookleaf_auth_expired on 401 response', async () => {
    localStorage.setItem('bookleaf_token', 'expired-token');
    localStorage.setItem('bookleaf_user', JSON.stringify({ id: 'usr_1' }));

    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 401,
      statusText: 'Unauthorized',
      json: async () => ({ detail: 'Token has expired.' }),
    });
    vi.stubGlobal('fetch', mockFetch);

    await expect(api.author.getBooks()).rejects.toThrow(ApiError);

    expect(localStorage.getItem('bookleaf_token')).toBeNull();
    expect(localStorage.getItem('bookleaf_user')).toBeNull();
    expect(window.dispatchEvent).toHaveBeenCalled();
  });
});
