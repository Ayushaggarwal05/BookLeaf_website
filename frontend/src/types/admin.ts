import type { AttachmentMetadata, TicketMessage } from './ticket';
export type { AttachmentMetadata, TicketMessage };

export interface AdminAuthorSummary {
  id: string;
  name: string;
  email: string;
  phone?: string | null;
  city?: string | null;
}

export interface AdminBookSummary {
  id: string;
  title: string;
  isbn: string;
  genre: string;
  status: string;
}

export interface AdminUserSummary {
  id: string;
  full_name: string;
  email: string;
  role: string;
}

export interface TicketInternalNote {
  id: string;
  ticket_id: string;
  author_user_id: string;
  note_body: string;
  created_at: string;
  updated_at: string;
}

export interface AdminTicket {
  id: string;
  ticket_number: string;
  author_id: string;
  book_id: string | null;
  subject: string;
  description: string;
  category: string;
  priority: string;
  status: string;
  assigned_to_id: string | null;
  attachments: AttachmentMetadata[];
  ai_classification?: Record<string, any> | null;
  created_at: string;
  updated_at: string;
  resolved_at: string | null;
  author?: AdminAuthorSummary | null;
  book?: AdminBookSummary | null;
  assigned_to?: AdminUserSummary | null;
}

export interface AdminTicketDetail extends AdminTicket {
  messages: TicketMessage[];
  internal_notes: TicketInternalNote[];
}

export interface AdminStatusUpdatePayload {
  status: string;
}

export interface AdminTriageUpdatePayload {
  category?: string;
  priority?: string;
  ai_classification?: Record<string, any> | null;
}

export interface AdminAssignUpdatePayload {
  assigned_to_id: string | null;
}

export interface AdminInternalNotePayload {
  note_body: string;
}

export interface AdminMessagePayload {
  message_body: string;
  attachments?: AttachmentMetadata[];
}

export interface AdminTicketFilters {
  status?: string;
  category?: string;
  priority?: string;
  assigned_to_id?: string;
  date_from?: string;
  date_to?: string;
  search?: string;
  skip?: number;
  limit?: number;
}

export interface AiDraftResponse {
  draft_response: string;
  suggested_category: string;
  suggested_priority: string;
  priority_code: string;
  confidence: number;
  reasoning: string;
  relevant_policies: string[];
  status: 'success' | 'unavailable' | 'error';
  model: string;
  error_message?: string | null;
  created_at: string;
}

