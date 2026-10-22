import React, { useEffect, useState, useRef, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  ArrowLeft, 
  Send, 
  Paperclip, 
  X, 
  BookOpen, 
  User, 
  ShieldCheck, 
  RefreshCw, 
  AlertCircle,
  FileText
} from 'lucide-react';
import { api, ApiError } from '../services/api';
import type { AuthorTicketDetail, AttachmentMetadata, CreateMessagePayload } from '../types/ticket';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { StatusBadge } from '../components/common/StatusBadge';

const POLLING_INTERVAL_MS = 8000; // 8 seconds modest polling interval

export const TicketDetailPage: React.FC = () => {
  const { ticketId } = useParams<{ ticketId: string }>();

  const [ticket, setTicket] = useState<AuthorTicketDetail | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);
  const [lastRefreshedAt, setLastRefreshedAt] = useState<Date>(() => new Date());

  // Reply form states
  const [replyBody, setReplyBody] = useState<string>('');
  const [replyAttachments, setReplyAttachments] = useState<AttachmentMetadata[]>([]);
  const [isSendingReply, setIsSendingReply] = useState<boolean>(false);
  const [replyError, setReplyError] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const isMountedRef = useRef<boolean>(true);

  // Fetch ticket details (silent option for polling)
  const fetchTicket = useCallback(async (silent = false) => {
    if (!ticketId) return;

    if (!silent) {
      setLoading(true);
      setError(null);
    } else {
      setIsRefreshing(true);
    }

    try {
      const data = await api.author.getTicket(ticketId);
      if (isMountedRef.current) {
        setTicket(data);
        setLastRefreshedAt(new Date());
      }
    } catch (err: any) {
      if (isMountedRef.current) {
        if (!silent) {
          setError(err.message || 'Failed to load ticket details.');
        }
      }
    } finally {
      if (isMountedRef.current) {
        setLoading(false);
        setIsRefreshing(false);
      }
    }
  }, [ticketId]);

  // Initial load
  useEffect(() => {
    isMountedRef.current = true;
    fetchTicket(false);

    // Near-real-time polling setup
    const intervalId = setInterval(() => {
      fetchTicket(true);
    }, POLLING_INTERVAL_MS);

    return () => {
      isMountedRef.current = false;
      clearInterval(intervalId);
    };
  }, [fetchTicket]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    const newAttachments: AttachmentMetadata[] = [];
    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      newAttachments.push({
        filename: file.name,
        size: file.size,
        type: file.type || 'application/octet-stream',
      });
    }

    setReplyAttachments((prev) => [...prev, ...newAttachments]);
    e.target.value = '';
  };

  const removeAttachment = (indexToRemove: number) => {
    setReplyAttachments((prev) => prev.filter((_, idx) => idx !== indexToRemove));
  };

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return '';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const formatDate = (isoString: string) => {
    try {
      const date = new Date(isoString);
      return date.toLocaleDateString('en-IN', {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return isoString;
    }
  };

  const handleSendReply = async (e: React.FormEvent) => {
    e.preventDefault();
    setReplyError(null);

    if (!ticketId || !replyBody.trim()) {
      setReplyError('Please enter a response message.');
      return;
    }

    setIsSendingReply(true);

    try {
      const payload: CreateMessagePayload = {
        message_body: replyBody.trim(),
        attachments: replyAttachments,
      };

      const newMessage = await api.author.replyTicket(ticketId, payload);
      
      // Update ticket locally with the new message
      if (ticket) {
        setTicket({
          ...ticket,
          status: ticket.status === 'WAITING_ON_AUTHOR' ? 'IN_PROGRESS' : ticket.status,
          messages: [...ticket.messages, newMessage],
        });
      }

      setReplyBody('');
      setReplyAttachments([]);
      setTimeout(scrollToBottom, 100);
    } catch (err: any) {
      if (err instanceof ApiError) {
        setReplyError(err.message);
      } else {
        setReplyError('Failed to send reply. Please try again.');
      }
    } finally {
      setIsSendingReply(false);
    }
  };

  if (loading) {
    return <LoadingSpinner size="lg" message="Loading conversation thread..." />;
  }

  if (error || !ticket) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-rose-50 border border-rose-200 rounded-xl p-6 flex items-start gap-4">
          <AlertCircle className="w-6 h-6 text-rose-600 flex-shrink-0" />
          <div>
            <h3 className="text-base font-semibold text-rose-900">Query Not Accessible</h3>
            <p className="text-sm text-rose-700 mt-1">
              {error || 'This support query could not be found or does not belong to your author account.'}
            </p>
            <div className="mt-4 flex gap-3">
              <Link
                to="/tickets"
                className="px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white rounded-lg text-xs font-semibold"
              >
                Back to All Queries
              </Link>
              <button
                onClick={() => fetchTicket(false)}
                className="px-4 py-2 bg-white border border-rose-300 text-rose-700 rounded-lg text-xs font-semibold"
              >
                Try Again
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 py-6 space-y-6">
      {/* Top Header & Breadcrumb */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pb-4 border-b border-cream-300">
        <div>
          <Link
            to="/tickets"
            className="inline-flex items-center gap-1.5 text-xs font-medium text-gray-500 hover:text-brand-900 transition mb-2"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to queries</span>
          </Link>
          <div className="flex flex-wrap items-center gap-2.5">
            <h1 className="text-xl sm:text-2xl font-serif font-bold text-brand-950">
              {ticket.subject}
            </h1>
            <span className="font-mono text-xs px-2 py-0.5 rounded bg-cream-200 text-brand-900 font-semibold border border-cream-300">
              {ticket.ticket_number}
            </span>
          </div>
        </div>

        {/* Polling Indicator & Manual Refresh */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 text-[11px] text-gray-500 bg-white px-2.5 py-1 rounded-full border border-cream-300">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span>Live Sync</span>
            <span className="text-gray-400">({Math.round(POLLING_INTERVAL_MS / 1000)}s • {lastRefreshedAt.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })})</span>
          </div>

          <button
            onClick={() => fetchTicket(true)}
            disabled={isRefreshing}
            className="p-1.5 rounded-lg text-gray-500 hover:text-brand-900 hover:bg-cream-100 border border-cream-300 transition"
            title="Refresh conversation now"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin text-brand-700' : ''}`} />
          </button>
        </div>
      </div>

      {/* Ticket Metadata Banner */}
      <div className="bg-white rounded-xl border border-cream-300 p-4 sm:p-5 shadow-soft">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
          <div>
            <span className="text-gray-500 block text-[11px] uppercase tracking-wider mb-1">
              Current Status
            </span>
            <StatusBadge status={ticket.status} type="ticket" />
          </div>

          <div>
            <span className="text-gray-500 block text-[11px] uppercase tracking-wider mb-1">
              Category
            </span>
            <span className="font-semibold text-brand-950">
              {ticket.category?.replace(/_/g, ' ') || 'GENERAL'}
            </span>
          </div>

          <div>
            <span className="text-gray-500 block text-[11px] uppercase tracking-wider mb-1">
              Associated Book
            </span>
            {ticket.book_title ? (
              <span className="font-serif font-medium text-brand-900 flex items-center gap-1">
                <BookOpen className="w-3.5 h-3.5 text-brand-600 flex-shrink-0" />
                <span className="truncate">{ticket.book_title}</span>
              </span>
            ) : (
              <span className="text-gray-500 italic">General / Account</span>
            )}
          </div>

          <div>
            <span className="text-gray-500 block text-[11px] uppercase tracking-wider mb-1">
              Logged On
            </span>
            <span className="text-gray-700 font-mono text-[11px]">
              {formatDate(ticket.created_at)}
            </span>
          </div>
        </div>
      </div>

      {/* Conversation Thread Container */}
      <div className="bg-white rounded-xl border border-cream-300 shadow-soft overflow-hidden">
        <div className="px-5 py-3.5 bg-cream-100 border-b border-cream-300 flex items-center justify-between">
          <span className="text-xs font-semibold uppercase tracking-wider text-gray-700">
            Conversation History ({1 + (ticket.messages?.length || 0)} entries)
          </span>
          <span className="text-[11px] text-gray-500 flex items-center gap-1">
            <ShieldCheck className="w-3.5 h-3.5 text-brand-700" />
            Verified Author Thread
          </span>
        </div>

        <div className="p-5 sm:p-6 space-y-6 max-h-[600px] overflow-y-auto bg-cream-50/30">
          {/* 1. Original Query Message Bubble */}
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-brand-700 text-white flex items-center justify-center text-xs font-bold flex-shrink-0 shadow-soft">
              <User className="w-4 h-4 text-brand-100" />
            </div>
            <div className="flex-1 space-y-2">
              <div className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-brand-950">You (Author)</span>
                  <span className="px-1.5 py-0.2 bg-brand-100 text-brand-800 text-[10px] rounded font-semibold">
                    Original Query
                  </span>
                </div>
                <span className="text-[11px] text-gray-400 font-mono">
                  {formatDate(ticket.created_at)}
                </span>
              </div>

              <div className="bg-white rounded-xl p-4 border border-cream-300 text-sm text-gray-800 leading-relaxed shadow-soft whitespace-pre-wrap">
                {ticket.description}
              </div>

              {/* Attachments for initial query */}
              {ticket.attachments && ticket.attachments.length > 0 && (
                <div className="pt-1">
                  <span className="text-[11px] font-semibold text-gray-500 uppercase tracking-wider block mb-1">
                    Attachments
                  </span>
                  <div className="flex flex-wrap gap-2">
                    {ticket.attachments.map((file, idx) => (
                      <div
                        key={idx}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-cream-100 border border-cream-300 rounded-lg text-xs text-brand-900"
                      >
                        <FileText className="w-3.5 h-3.5 text-brand-700" />
                        <span className="font-medium truncate max-w-[200px]">{file.filename}</span>
                        {file.size && (
                          <span className="text-[10px] text-gray-500 font-mono">
                            ({formatFileSize(file.size)})
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* 2. Subsequent Messages (Author replies & Support replies) */}
          {ticket.messages && ticket.messages.map((msg) => {
            const isAuthor = msg.sender_type === 'AUTHOR';
            const isSystem = msg.sender_type === 'SYSTEM';

            if (isSystem) {
              return (
                <div key={msg.id} className="text-center py-2">
                  <div className="inline-block px-3 py-1 rounded-full bg-cream-200 text-gray-600 text-[11px] border border-cream-300 font-medium">
                    {msg.message_body} • <span className="text-gray-400">{formatDate(msg.created_at)}</span>
                  </div>
                </div>
              );
            }

            return (
              <div key={msg.id} className="flex gap-3">
                {isAuthor ? (
                  <div className="w-8 h-8 rounded-full bg-brand-700 text-white flex items-center justify-center text-xs font-bold flex-shrink-0 shadow-soft">
                    <User className="w-4 h-4 text-brand-100" />
                  </div>
                ) : (
                  <div className="w-8 h-8 rounded-full bg-emerald-800 text-white flex items-center justify-center text-xs font-bold flex-shrink-0 shadow-soft">
                    <ShieldCheck className="w-4 h-4 text-emerald-100" />
                  </div>
                )}

                <div className="flex-1 space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-brand-950">
                        {isAuthor ? 'You (Author)' : msg.sender_name || 'BookLeaf Support Specialist'}
                      </span>
                      <span
                        className={`px-1.5 py-0.2 text-[10px] rounded font-semibold ${
                          isAuthor
                            ? 'bg-brand-100 text-brand-800'
                            : 'bg-emerald-100 text-emerald-900 border border-emerald-200'
                        }`}
                      >
                        {isAuthor ? 'Author Reply' : 'Editorial & Support Team'}
                      </span>
                    </div>
                    <span className="text-[11px] text-gray-400 font-mono">
                      {formatDate(msg.created_at)}
                    </span>
                  </div>

                  <div
                    className={`rounded-xl p-4 border text-sm leading-relaxed shadow-soft whitespace-pre-wrap ${
                      isAuthor
                        ? 'bg-white border-cream-300 text-gray-800'
                        : 'bg-emerald-50/40 border-emerald-200 text-brand-950'
                    }`}
                  >
                    {msg.message_body}
                  </div>

                  {/* Message Attachments */}
                  {msg.attachments && msg.attachments.length > 0 && (
                    <div className="pt-1">
                      <div className="flex flex-wrap gap-2">
                        {msg.attachments.map((file, idx) => (
                          <div
                            key={idx}
                            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-cream-100 border border-cream-300 rounded-lg text-xs text-brand-900"
                          >
                            <FileText className="w-3.5 h-3.5 text-brand-700" />
                            <span className="font-medium truncate max-w-[200px]">
                              {file.filename}
                            </span>
                            {file.size && (
                              <span className="text-[10px] text-gray-500 font-mono">
                                ({formatFileSize(file.size)})
                              </span>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            );
          })}

          <div ref={messagesEndRef} />
        </div>

        {/* Reply Submission Box */}
        <div className="p-4 sm:p-5 bg-white border-t border-cream-300">
          {ticket.status === 'CLOSED' || ticket.status === 'RESOLVED' ? (
            <div className="bg-cream-100 border border-cream-300 rounded-lg p-3 text-xs text-gray-700 flex items-center justify-between">
              <span>
                This query is currently marked as <strong>{ticket.status}</strong>. Sending a new reply will notify the support team and resume active handling.
              </span>
            </div>
          ) : null}

          {replyError && (
            <div className="mb-3 bg-rose-50 border border-rose-300 rounded-lg p-3 text-xs text-rose-800 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-rose-600 flex-shrink-0" />
              <span>{replyError}</span>
            </div>
          )}

          <form onSubmit={handleSendReply} className="space-y-3 mt-2">
            <textarea
              rows={3}
              placeholder="Type your response to the support team..."
              value={replyBody}
              onChange={(e) => setReplyBody(e.target.value)}
              disabled={isSendingReply}
              className="w-full rounded-lg border border-cream-300 px-3.5 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-brand-700 transition leading-relaxed resize-y"
            />

            {/* Attached file badges */}
            {replyAttachments.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {replyAttachments.map((file, idx) => (
                  <div
                    key={idx}
                    className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-cream-100 rounded border border-cream-300 text-xs text-gray-800"
                  >
                    <Paperclip className="w-3 h-3 text-brand-700" />
                    <span className="font-medium truncate max-w-[150px]">{file.filename}</span>
                    <button
                      type="button"
                      onClick={() => removeAttachment(idx)}
                      className="text-gray-400 hover:text-rose-600 ml-1"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </div>
                ))}
              </div>
            )}

            <div className="flex items-center justify-between pt-1">
              <div>
                <input
                  type="file"
                  id="reply-file-input"
                  multiple
                  onChange={handleFileChange}
                  disabled={isSendingReply}
                  className="hidden"
                />
                <label
                  htmlFor="reply-file-input"
                  className="cursor-pointer inline-flex items-center gap-1.5 text-xs font-semibold text-brand-700 hover:text-brand-900 bg-cream-100 hover:bg-cream-200 px-3 py-1.5 rounded-lg border border-cream-300 transition"
                >
                  <Paperclip className="w-3.5 h-3.5" />
                  <span>Attach File</span>
                </label>
              </div>

              <button
                type="submit"
                disabled={isSendingReply || !replyBody.trim()}
                className="inline-flex items-center gap-2 px-5 py-2 rounded-lg bg-brand-700 hover:bg-brand-800 active:bg-brand-900 text-white text-xs font-semibold shadow-soft disabled:opacity-50 transition"
              >
                {isSendingReply ? (
                  <>
                    <LoadingSpinner size="sm" />
                    <span>Sending...</span>
                  </>
                ) : (
                  <>
                    <Send className="w-3.5 h-3.5" />
                    <span>Send Reply</span>
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};
