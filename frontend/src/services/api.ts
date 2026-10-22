import type { LoginCredentials, TokenResponse, User } from '../types/auth';
import type { AuthorProfile } from '../types/author';
import type { Book, AuthorRoyaltySummary } from '../types/book';
import type { AuthorTicket, AuthorTicketDetail, CreateTicketPayload, CreateMessagePayload, TicketMessage } from '../types/ticket';
import type { 
  AdminTicket, 
  AdminTicketDetail, 
  AdminStatusUpdatePayload, 
  AdminTriageUpdatePayload, 
  AdminAssignUpdatePayload, 
  AdminInternalNotePayload, 
  AdminMessagePayload, 
  AdminTicketFilters, 
  AdminUserSummary,
  TicketInternalNote,
  AiDraftResponse
} from '../types/admin';

// Read API base URL from environment or fall back to standard local backend
const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1').replace(/\/+$/, '');

export class ApiError extends Error {
  status: number;
  errors?: any[];

  constructor(status: number, message: string, errors?: any[]) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.errors = errors;
  }
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
  
  const headers = new Headers(options.headers || {});
  headers.set('Content-Type', 'application/json');

  const token = localStorage.getItem('bookleaf_token');
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorDetail = 'An unexpected error occurred.';
    let validationErrors: any[] | undefined = undefined;

    try {
      const errorJson = await response.json();
      if (typeof errorJson.detail === 'string') {
        errorDetail = errorJson.detail;
      } else if (Array.isArray(errorJson.errors)) {
        validationErrors = errorJson.errors;
        errorDetail = errorJson.detail || 'Validation error.';
      } else if (errorJson.message) {
        errorDetail = errorJson.message;
      }
    } catch {
      errorDetail = response.statusText || errorDetail;
    }

    if (response.status === 401) {
      localStorage.removeItem('bookleaf_token');
      localStorage.removeItem('bookleaf_user');
      window.dispatchEvent(new CustomEvent('bookleaf_auth_expired'));
    }

    throw new ApiError(response.status, errorDetail, validationErrors);
  }

  // Handle empty responses (204 No Content)
  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}

export const api = {
  auth: {
    login: (credentials: LoginCredentials): Promise<TokenResponse> => {
      return request<TokenResponse>('/auth/login', {
        method: 'POST',
        body: JSON.stringify(credentials),
      });
    },
    getMe: (): Promise<User> => {
      return request<User>('/auth/me');
    },
  },

  author: {
    getProfile: (): Promise<AuthorProfile> => {
      return request<AuthorProfile>('/author/profile');
    },
    getBooks: (): Promise<Book[]> => {
      return request<Book[]>('/author/books');
    },
    getBook: (bookId: string): Promise<Book> => {
      return request<Book>(`/author/books/${bookId}`);
    },
    getRoyalties: (): Promise<AuthorRoyaltySummary> => {
      return request<AuthorRoyaltySummary>('/author/royalties');
    },
    getTickets: (): Promise<AuthorTicket[]> => {
      return request<AuthorTicket[]>('/author/tickets');
    },
    getTicket: (ticketId: string): Promise<AuthorTicketDetail> => {
      return request<AuthorTicketDetail>(`/author/tickets/${ticketId}`);
    },
    createTicket: (payload: CreateTicketPayload): Promise<AuthorTicket> => {
      return request<AuthorTicket>('/author/tickets', {
        method: 'POST',
        body: JSON.stringify(payload),
      });
    },
    replyTicket: (ticketId: string, payload: CreateMessagePayload): Promise<TicketMessage> => {
      return request<TicketMessage>(`/author/tickets/${ticketId}/messages`, {
        method: 'POST',
        body: JSON.stringify(payload),
      });
    },
  },

  admin: {
    getTickets: (filters: AdminTicketFilters = {}): Promise<AdminTicket[]> => {
      const params = new URLSearchParams();
      if (filters.status) params.set('status', filters.status);
      if (filters.category) params.set('category', filters.category);
      if (filters.priority) params.set('priority', filters.priority);
      if (filters.assigned_to_id) params.set('assigned_to_id', filters.assigned_to_id);
      if (filters.date_from) params.set('date_from', filters.date_from);
      if (filters.date_to) params.set('date_to', filters.date_to);
      if (filters.search) params.set('search', filters.search);
      if (filters.skip !== undefined) params.set('skip', filters.skip.toString());
      if (filters.limit !== undefined) params.set('limit', filters.limit.toString());

      const qs = params.toString();
      return request<AdminTicket[]>(`/admin/tickets${qs ? `?${qs}` : ''}`);
    },

    getTicket: (ticketId: string): Promise<AdminTicketDetail> => {
      return request<AdminTicketDetail>(`/admin/tickets/${ticketId}`);
    },

    updateStatus: (ticketId: string, payload: AdminStatusUpdatePayload): Promise<AdminTicket> => {
      return request<AdminTicket>(`/admin/tickets/${ticketId}/status`, {
        method: 'PATCH',
        body: JSON.stringify(payload),
      });
    },

    updateTriage: (ticketId: string, payload: AdminTriageUpdatePayload): Promise<AdminTicket> => {
      return request<AdminTicket>(`/admin/tickets/${ticketId}/triage`, {
        method: 'PATCH',
        body: JSON.stringify(payload),
      });
    },

    assignTicket: (ticketId: string, payload: AdminAssignUpdatePayload): Promise<AdminTicket> => {
      return request<AdminTicket>(`/admin/tickets/${ticketId}/assign`, {
        method: 'PATCH',
        body: JSON.stringify(payload),
      });
    },

    addNote: (ticketId: string, payload: AdminInternalNotePayload): Promise<TicketInternalNote> => {
      return request<TicketInternalNote>(`/admin/tickets/${ticketId}/notes`, {
        method: 'POST',
        body: JSON.stringify(payload),
      });
    },

    sendMessage: (ticketId: string, payload: AdminMessagePayload): Promise<TicketMessage> => {
      return request<TicketMessage>(`/admin/tickets/${ticketId}/messages`, {
        method: 'POST',
        body: JSON.stringify(payload),
      });
    },

    getAdmins: (): Promise<AdminUserSummary[]> => {
      return request<AdminUserSummary[]>('/admin/admins');
    },

    generateAiDraft: (ticketId: string): Promise<AiDraftResponse> => {
      return request<AiDraftResponse>(`/admin/tickets/${ticketId}/ai-draft`, {
        method: 'POST',
      });
    },

    applyAiTriage: (ticketId: string): Promise<AdminTicket> => {
      return request<AdminTicket>(`/admin/tickets/${ticketId}/apply-ai-triage`, {
        method: 'POST',
      });
    },
  },
};
