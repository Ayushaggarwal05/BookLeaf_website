export interface AttachmentMetadata {
  filename: string;
  size?: number;
  url?: string;
  type?: string;
}

export interface TicketMessage {
  id: string;
  ticket_id: string;
  sender_type: 'AUTHOR' | 'SUPPORT_AGENT' | 'SYSTEM';
  sender_id?: string | null;
  sender_name: string;
  message_body: string;
  attachments: AttachmentMetadata[];
  created_at: string;
  updated_at: string;
}

export interface AuthorTicket {
  id: string;
  ticket_number: string;
  author_id: string;
  book_id: string | null;
  book_title: string | null;
  subject: string;
  description: string;
  category: string;
  priority: string;
  status: 'OPEN' | 'IN_PROGRESS' | 'WAITING_ON_AUTHOR' | 'RESOLVED' | 'CLOSED' | string;
  attachments: AttachmentMetadata[];
  created_at: string;
  updated_at: string;
  resolved_at: string | null;
}

export interface AuthorTicketDetail extends AuthorTicket {
  messages: TicketMessage[];
}

export interface CreateTicketPayload {
  book_id?: string | null;
  subject: string;
  description: string;
  category?: string;
  attachments?: AttachmentMetadata[];
}

export interface CreateMessagePayload {
  message_body: string;
  attachments?: AttachmentMetadata[];
}
