import React, { useEffect, useState, useRef, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  ArrowLeft, 
  Send, 
  Lock, 
  User, 
  ShieldCheck, 
  AlertCircle, 
  AlertTriangle,
  CheckCircle2, 
  RefreshCw, 
  Sparkles, 
  FileText,
  Copy,
  Check,
  ArrowDownToLine,
  BookOpen
} from 'lucide-react';
import { api } from '../../services/api';
import type { 
  AdminTicketDetail, 
  AdminUserSummary, 
  AttachmentMetadata,
  AiDraftResponse
} from '../../types/admin';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { StatusBadge } from '../../components/common/StatusBadge';
import { formatDateTime } from '../../utils/formatters';

const CATEGORIES = [
  { value: 'GENERAL_INQUIRY', label: 'General / Account' },
  { value: 'ROYALTY', label: 'Royalty & Payouts' },
  { value: 'PRINT_QUALITY', label: 'Print Quality & Defect' },
  { value: 'DISTRIBUTION', label: 'Distribution & Retail' },
  { value: 'COVER_DESIGN', label: 'Cover & Interior Design' },
  { value: 'METADATA_UPDATE', label: 'Metadata & Listing Updates' },
];

const PRIORITIES = [
  { value: 'LOW', label: 'Low' },
  { value: 'MEDIUM', label: 'Medium' },
  { value: 'HIGH', label: 'High' },
  { value: 'URGENT', label: 'Urgent' },
];

const STATUSES = [
  { value: 'OPEN', label: 'Open' },
  { value: 'IN_PROGRESS', label: 'In Progress' },
  { value: 'WAITING_ON_AUTHOR', label: 'Awaiting Author Reply' },
  { value: 'RESOLVED', label: 'Resolved' },
  { value: 'CLOSED', label: 'Closed' },
];

const POLLING_INTERVAL_MS = 10000; // 10 seconds

export const AdminTicketDetailPage: React.FC = () => {
  const { ticketId } = useParams<{ ticketId: string }>();

  // Ticket data
  const [ticket, setTicket] = useState<AdminTicketDetail | null>(null);
  const [admins, setAdmins] = useState<AdminUserSummary[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);
  const [lastRefreshedAt, setLastRefreshedAt] = useState<Date>(() => new Date());

  // Action states
  const [selectedStatus, setSelectedStatus] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [selectedPriority, setSelectedPriority] = useState<string>('');
  const [selectedAssignee, setSelectedAssignee] = useState<string>('');
  const [isUpdatingStatus, setIsUpdatingStatus] = useState<boolean>(false);
  const [isUpdatingTriage, setIsUpdatingTriage] = useState<boolean>(false);
  const [isUpdatingAssignee, setIsUpdatingAssignee] = useState<boolean>(false);
  const [toast, setToast] = useState<{ type: 'success' | 'warning' | 'error'; message: string } | null>(null);

  // Author reply form
  const [replyBody, setReplyBody] = useState<string>('');
  const [replyAttachments, setReplyAttachments] = useState<AttachmentMetadata[]>([]);
  const [isSendingReply, setIsSendingReply] = useState<boolean>(false);
  const [replyError, setReplyError] = useState<string | null>(null);

  // Internal note form
  const [noteBody, setNoteBody] = useState<string>('');
  const [isAddingNote, setIsAddingNote] = useState<boolean>(false);
  const [noteError, setNoteError] = useState<string | null>(null);

  // AI Copilot state
  const [isGeneratingDraft, setIsGeneratingDraft] = useState<boolean>(false);
  const [draftResult, setDraftResult] = useState<AiDraftResponse | null>(null);
  const [draftText, setDraftText] = useState<string>('');
  const [aiError, setAiError] = useState<string | null>(null);
  const [isApplyingAiTriage, setIsApplyingAiTriage] = useState<boolean>(false);
  const [copiedDraft, setCopiedDraft] = useState<boolean>(false);

  const isMountedRef = useRef<boolean>(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const replyTextareaRef = useRef<HTMLTextAreaElement>(null);

  const showFeedback = (message: string, type: 'success' | 'warning' | 'error' = 'success') => {
    setToast({ type, message });
    setTimeout(() => {
      if (isMountedRef.current) setToast(null);
    }, 5000);
  };

  const fetchTicket = useCallback(async (silent = false) => {
    if (!ticketId) return;

    if (!silent) {
      setLoading(true);
      setError(null);
    } else {
      setIsRefreshing(true);
    }

    try {
      const [ticketData, adminsList] = await Promise.all([
        api.admin.getTicket(ticketId),
        api.admin.getAdmins(),
      ]);

      if (isMountedRef.current) {
        setTicket(ticketData);
        setAdmins(adminsList);
        setSelectedStatus(ticketData.status);
        setSelectedCategory(ticketData.category);
        setSelectedPriority(ticketData.priority);
        setSelectedAssignee(ticketData.assigned_to_id || '');
        if (ticketData.ai_classification?.draft_response) {
          setDraftText((prev) => prev ? prev : (ticketData.ai_classification?.draft_response || ''));
        }
        setLastRefreshedAt(new Date());
      }
    } catch (err: any) {
      if (isMountedRef.current && !silent) {
        setError(err.message || 'Failed to load ticket details.');
      }
    } finally {
      if (isMountedRef.current) {
        setLoading(false);
        setIsRefreshing(false);
      }
    }
  }, [ticketId]);

  useEffect(() => {
    isMountedRef.current = true;
    fetchTicket(false);

    const intervalId = setInterval(() => {
      fetchTicket(true);
    }, POLLING_INTERVAL_MS);

    return () => {
      isMountedRef.current = false;
      clearInterval(intervalId);
    };
  }, [fetchTicket]);

  // 1. Update Status Action
  const handleStatusChange = async (newStatus: string) => {
    if (!ticket || isUpdatingStatus) return;
    setIsUpdatingStatus(true);
    try {
      const updated = await api.admin.updateStatus(ticket.id, { status: newStatus });
      setTicket((prev) => prev ? { ...prev, status: updated.status, resolved_at: updated.resolved_at } : null);
      setSelectedStatus(updated.status);
      showFeedback(`Status transitioned to ${updated.status}`);
    } catch (err: any) {
      alert(err.message || 'Failed to update ticket status.');
    } finally {
      setIsUpdatingStatus(false);
    }
  };

  // 2. Update Triage (Category & Priority)
  const handleTriageUpdate = async () => {
    if (!ticket || isUpdatingTriage) return;
    setIsUpdatingTriage(true);
    try {
      const updated = await api.admin.updateTriage(ticket.id, {
        category: selectedCategory,
        priority: selectedPriority,
      });
      setTicket((prev) => prev ? { ...prev, category: updated.category, priority: updated.priority } : null);
      showFeedback('Category and Priority triage updated.');
    } catch (err: any) {
      alert(err.message || 'Failed to update triage classification.');
    } finally {
      setIsUpdatingTriage(false);
    }
  };

  // 3. Assign Staff
  const handleAssigneeChange = async (newAssigneeId: string) => {
    if (!ticket || isUpdatingAssignee) return;
    setIsUpdatingAssignee(true);
    try {
      const updated = await api.admin.assignTicket(ticket.id, {
        assigned_to_id: newAssigneeId || null,
      });
      const assignedUser = admins.find((a) => a.id === updated.assigned_to_id) || null;
      setTicket((prev) => prev ? { ...prev, assigned_to_id: updated.assigned_to_id, assigned_to: assignedUser } : null);
      setSelectedAssignee(updated.assigned_to_id || '');
      showFeedback(assignedUser ? `Ticket assigned to ${assignedUser.full_name}` : 'Ticket unassigned');
    } catch (err: any) {
      alert(err.message || 'Failed to assign staff member.');
    } finally {
      setIsUpdatingAssignee(false);
    }
  };

  // 4. Send Author-Visible Reply
  const handleSendReply = async (e: React.FormEvent) => {
    e.preventDefault();
    setReplyError(null);

    if (!ticketId || !replyBody.trim()) {
      setReplyError('Message body cannot be empty.');
      return;
    }

    setIsSendingReply(true);
    try {
      const newMsg = await api.admin.sendMessage(ticketId, {
        message_body: replyBody.trim(),
        attachments: replyAttachments,
      });

      // Update state
      if (ticket) {
        setTicket({
          ...ticket,
          status: ticket.status === 'OPEN' || ticket.status === 'IN_PROGRESS' ? 'WAITING_ON_AUTHOR' : ticket.status,
          messages: [...ticket.messages, newMsg as any],
        });
        setSelectedStatus(ticket.status === 'OPEN' || ticket.status === 'IN_PROGRESS' ? 'WAITING_ON_AUTHOR' : ticket.status);
      }

      setReplyBody('');
      setReplyAttachments([]);
      showFeedback('Author-visible reply sent successfully.');
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    } catch (err: any) {
      setReplyError(err.message || 'Failed to send author reply.');
    } finally {
      setIsSendingReply(false);
    }
  };

  // 5. Add Internal Admin Note
  const handleAddInternalNote = async (e: React.FormEvent) => {
    e.preventDefault();
    setNoteError(null);

    if (!ticketId || !noteBody.trim()) {
      setNoteError('Internal note text cannot be empty.');
      return;
    }

    setIsAddingNote(true);
    try {
      const newNote = await api.admin.addNote(ticketId, {
        note_body: noteBody.trim(),
      });

      if (ticket) {
        setTicket({
          ...ticket,
          internal_notes: [...ticket.internal_notes, newNote],
        });
      }

      setNoteBody('');
      showFeedback('Confidential internal note logged.');
    } catch (err: any) {
      setNoteError(err.message || 'Failed to add internal note.');
    } finally {
      setIsAddingNote(false);
    }
  };

  // 6. AI Copilot Actions
  const handleGenerateAiDraft = async () => {
    if (!ticket) return;
    setIsGeneratingDraft(true);
    setAiError(null);
    try {
      const res = await api.admin.generateAiDraft(ticket.id);
      setDraftResult(res);
      if (res.status === 'success' && res.draft_response) {
        setDraftText(res.draft_response);
        showFeedback('AI draft response generated with BookLeaf policy context.', 'success');
      } else if (res.status === 'unavailable') {
        const errorNotice = res.error_message || 'Gemini API key is not configured on the backend. Automated AI drafting is unavailable.';
        setDraftText('');
        setAiError(errorNotice);
        showFeedback(errorNotice, 'warning');
      } else {
        const errorNotice = res.error_message || 'AI response generation failed. Please check backend configuration.';
        setDraftText('');
        setAiError(errorNotice);
        showFeedback(errorNotice, 'error');
      }
    } catch (err: any) {
      const errorNotice = err.message || 'Failed to communicate with AI drafting service.';
      setDraftText('');
      setAiError(errorNotice);
      showFeedback(errorNotice, 'error');
    } finally {
      setIsGeneratingDraft(false);
    }
  };

  const handleApplyAiTriage = async () => {
    if (!ticket || isApplyingAiTriage) return;
    setIsApplyingAiTriage(true);
    try {
      const updated = await api.admin.applyAiTriage(ticket.id);
      setTicket((prev) => prev ? {
        ...prev,
        category: updated.category,
        priority: updated.priority,
        ai_classification: updated.ai_classification || prev.ai_classification
      } : null);
      setSelectedCategory(updated.category);
      setSelectedPriority(updated.priority);
      showFeedback(`AI triage applied: ${updated.category} (${updated.priority})`);
    } catch (err: any) {
      alert(err.message || 'Failed to apply AI triage.');
    } finally {
      setIsApplyingAiTriage(false);
    }
  };

  const handleInsertDraftIntoReply = () => {
    if (!draftText.trim()) return;
    setReplyBody(draftText);
    showFeedback('Draft inserted into response composer. Review and edit before sending.');
    setTimeout(() => {
      replyTextareaRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' });
      replyTextareaRef.current?.focus();
    }, 100);
  };

  const handleCopyDraft = async () => {
    if (!draftText) return;
    try {
      await navigator.clipboard.writeText(draftText);
      setCopiedDraft(true);
      setTimeout(() => setCopiedDraft(false), 2000);
    } catch {
      // ignore
    }
  };

  if (loading) {
    return <LoadingSpinner size="lg" message="Loading administrative ticket details..." />;
  }

  if (error || !ticket) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-8">
        <div className="bg-rose-50 border border-rose-200 rounded-xl p-6 flex items-start gap-4">
          <AlertCircle className="w-6 h-6 text-rose-600 flex-shrink-0" />
          <div>
            <h3 className="text-base font-semibold text-rose-900">Ticket Not Accessible</h3>
            <p className="text-sm text-rose-700 mt-1">{error || 'Ticket not found.'}</p>
            <Link
              to="/admin/tickets"
              className="mt-4 inline-block px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white rounded-lg text-xs font-semibold"
            >
              Back to Ticket Queue
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      {/* Top Header & Breadcrumbs */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pb-4 border-b border-cream-300">
        <div>
          <Link
            to="/admin/tickets"
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-gray-500 hover:text-brand-900 transition mb-2"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to Queue</span>
          </Link>

          <div className="flex flex-wrap items-center gap-2.5">
            <h1 className="text-xl sm:text-2xl font-serif font-bold text-brand-950">
              {ticket.subject}
            </h1>
            <span className="font-mono text-xs px-2 py-0.5 rounded bg-brand-100 text-brand-900 font-bold border border-brand-300">
              {ticket.ticket_number}
            </span>
          </div>
        </div>

        {/* Polling Indicator & Manual Refresh */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 text-[11px] text-gray-500 bg-white px-2.5 py-1 rounded-full border border-cream-300 shadow-soft">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span>Live Sync</span>
            <span className="text-gray-400">
              ({lastRefreshedAt.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })})
            </span>
          </div>

          <button
            onClick={() => fetchTicket(true)}
            disabled={isRefreshing}
            className="p-1.5 rounded-lg text-gray-600 hover:text-brand-900 hover:bg-cream-100 border border-cream-300 transition"
            title="Refresh ticket now"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin text-brand-700' : ''}`} />
          </button>
        </div>
      </div>

      {/* Action / Warning Toast Banner */}
      {toast && (
        <div
          className={`rounded-xl p-3.5 flex items-center justify-between gap-3 text-xs font-semibold shadow-soft border transition-all ${
            toast.type === 'error'
              ? 'bg-rose-50 border-rose-300 text-rose-900'
              : toast.type === 'warning'
              ? 'bg-amber-50 border-amber-300 text-amber-950'
              : 'bg-emerald-50 border-emerald-300 text-emerald-900'
          }`}
        >
          <div className="flex items-center gap-2">
            {toast.type === 'error' && <AlertCircle className="w-4 h-4 text-rose-600 flex-shrink-0" />}
            {toast.type === 'warning' && <AlertTriangle className="w-4 h-4 text-amber-700 flex-shrink-0" />}
            {toast.type === 'success' && <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />}
            <span>{toast.message}</span>
          </div>
          <button
            type="button"
            onClick={() => setToast(null)}
            className="text-xs opacity-60 hover:opacity-100 transition px-1.5 py-0.5 rounded hover:bg-black/5"
            title="Dismiss notice"
          >
            ✕
          </button>
        </div>
      )}

      {/* Main Grid: Left 2 Cols (Conversation & Notes), Right 1 Col (Triage & Context) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column (2 cols): Conversation & Internal Notes */}
        <div className="lg:col-span-2 space-y-6">
          {/* Author Query & Public Conversation Thread */}
          <div className="bg-white rounded-xl border border-cream-300 shadow-soft overflow-hidden">
            <div className="px-5 py-3.5 bg-cream-100 border-b border-cream-300 flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-gray-700">
                Author-Visible Communication ({1 + (ticket.messages?.length || 0)} messages)
              </span>
              <span className="text-[11px] text-emerald-700 font-semibold flex items-center gap-1">
                <ShieldCheck className="w-3.5 h-3.5" />
                Visible to Author
              </span>
            </div>

            <div className="p-5 space-y-6 max-h-[550px] overflow-y-auto bg-cream-50/20">
              {/* 1. Original Author Query */}
              <div className="flex gap-3">
                <div className="w-8 h-8 rounded-full bg-brand-800 text-white flex items-center justify-center text-xs font-bold flex-shrink-0 shadow-soft">
                  <User className="w-4 h-4 text-brand-100" />
                </div>
                <div className="flex-1 space-y-1.5">
                  <div className="flex items-center justify-between text-xs">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-brand-950">
                        {ticket.author?.name || 'Author'}
                      </span>
                      <span className="px-1.5 py-0.2 bg-brand-100 text-brand-800 text-[10px] rounded font-semibold">
                        Author Inquiry
                      </span>
                    </div>
                    <span className="text-[11px] text-gray-400 font-mono">
                      {formatDateTime(ticket.created_at)}
                    </span>
                  </div>

                  <div className="bg-white rounded-xl p-4 border border-cream-300 text-xs text-gray-800 leading-relaxed shadow-soft whitespace-pre-wrap">
                    {ticket.description}
                  </div>

                  {ticket.attachments && ticket.attachments.length > 0 && (
                    <div className="flex flex-wrap gap-2 pt-1">
                      {ticket.attachments.map((file, idx) => (
                        <div
                          key={idx}
                          className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-cream-100 border border-cream-300 rounded text-[11px] text-brand-900"
                        >
                          <FileText className="w-3 h-3 text-brand-700" />
                          <span className="font-medium truncate max-w-[200px]">{file.filename}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {/* 2. Messages List */}
              {ticket.messages && ticket.messages.map((msg) => {
                const isAuthor = msg.sender_type === 'AUTHOR';
                const isSystem = msg.sender_type === 'SYSTEM';

                if (isSystem) {
                  return (
                    <div key={msg.id} className="text-center py-1">
                      <span className="inline-block px-3 py-1 rounded-full bg-cream-200 text-gray-600 text-[10px] border border-cream-300">
                        {msg.message_body} • {formatDateTime(msg.created_at)}
                      </span>
                    </div>
                  );
                }

                return (
                  <div key={msg.id} className="flex gap-3">
                    {isAuthor ? (
                      <div className="w-8 h-8 rounded-full bg-brand-800 text-white flex items-center justify-center text-xs font-bold flex-shrink-0 shadow-soft">
                        <User className="w-4 h-4 text-brand-100" />
                      </div>
                    ) : (
                      <div className="w-8 h-8 rounded-full bg-emerald-800 text-white flex items-center justify-center text-xs font-bold flex-shrink-0 shadow-soft">
                        <ShieldCheck className="w-4 h-4 text-emerald-100" />
                      </div>
                    )}

                    <div className="flex-1 space-y-1.5">
                      <div className="flex items-center justify-between text-xs">
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-brand-950">
                            {isAuthor ? ticket.author?.name || 'Author' : msg.sender_name || 'Staff Member'}
                          </span>
                          <span
                            className={`px-1.5 py-0.2 text-[10px] rounded font-semibold ${
                              isAuthor
                                ? 'bg-brand-100 text-brand-800'
                                : 'bg-emerald-100 text-emerald-900 border border-emerald-200'
                            }`}
                          >
                            {isAuthor ? 'Author Reply' : 'BookLeaf Operations Staff'}
                          </span>
                        </div>
                        <span className="text-[11px] text-gray-400 font-mono">
                          {formatDateTime(msg.created_at)}
                        </span>
                      </div>

                      <div
                        className={`rounded-xl p-4 border text-xs leading-relaxed shadow-soft whitespace-pre-wrap ${
                          isAuthor
                            ? 'bg-white border-cream-300 text-gray-800'
                            : 'bg-emerald-50/40 border-emerald-200 text-brand-950'
                        }`}
                      >
                        {msg.message_body}
                      </div>

                      {msg.attachments && msg.attachments.length > 0 && (
                        <div className="flex flex-wrap gap-2 pt-1">
                          {msg.attachments.map((file, idx) => (
                            <div
                              key={idx}
                              className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-cream-100 border border-cream-300 rounded text-[11px] text-brand-900"
                            >
                              <FileText className="w-3 h-3 text-brand-700" />
                              <span className="font-medium truncate max-w-[200px]">{file.filename}</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}

              <div ref={messagesEndRef} />
            </div>

            {/* Author Response Composer */}
            <div className="p-4 bg-white border-t border-cream-300">
              <span className="text-[11px] font-semibold text-gray-700 uppercase tracking-wider block mb-1">
                Compose Author-Visible Response
              </span>
              <p className="text-[11px] text-gray-500 mb-2">
                This response will be visible in the author's support portal and will automatically update the status to <strong>Awaiting Author Reply</strong> if open/in-progress.
              </p>

              {replyError && (
                <div className="mb-3 bg-rose-50 border border-rose-300 rounded-lg p-2.5 text-xs text-rose-800 flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 text-rose-600 flex-shrink-0" />
                  <span>{replyError}</span>
                </div>
              )}

              <form onSubmit={handleSendReply} className="space-y-3">
                <textarea
                  ref={replyTextareaRef}
                  rows={3}
                  placeholder="Type an official response to the author..."
                  value={replyBody}
                  onChange={(e) => setReplyBody(e.target.value)}
                  disabled={isSendingReply}
                  className="w-full rounded-lg border border-cream-300 p-3 text-xs focus:outline-none focus:ring-2 focus:ring-brand-700 transition leading-relaxed resize-y"
                />

                <div className="flex items-center justify-between">
                  <span className="text-[11px] text-gray-400">
                    Press send to notify author thread
                  </span>

                  <button
                    type="submit"
                    disabled={isSendingReply || !replyBody.trim()}
                    className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-emerald-700 hover:bg-emerald-800 text-white text-xs font-semibold shadow-soft disabled:opacity-50 transition"
                  >
                    {isSendingReply ? (
                      <>
                        <LoadingSpinner size="sm" />
                        <span>Sending Reply...</span>
                      </>
                    ) : (
                      <>
                        <Send className="w-3.5 h-3.5" />
                        <span>Send Response to Author</span>
                      </>
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>

          {/* Private Internal Notes (Strict Staff-Only Isolation) */}
          <div className="bg-amber-50/50 rounded-xl border border-amber-200/90 shadow-soft overflow-hidden">
            <div className="px-5 py-3.5 bg-amber-100/70 border-b border-amber-200 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Lock className="w-4 h-4 text-amber-800" />
                <span className="text-xs font-bold uppercase tracking-wider text-amber-950">
                  Private Internal Notes ({ticket.internal_notes?.length || 0})
                </span>
              </div>
              <span className="px-2 py-0.5 rounded bg-amber-200/80 text-amber-900 text-[10px] font-mono font-bold uppercase border border-amber-300">
                Staff Only • Hidden from Author
              </span>
            </div>

            <div className="p-5 space-y-4">
              {ticket.internal_notes && ticket.internal_notes.length === 0 ? (
                <p className="text-xs text-amber-900/70 italic">
                  No internal notes recorded yet. Add operational context, investigation details, or finance reconciliation notes below.
                </p>
              ) : (
                ticket.internal_notes?.map((note) => (
                  <div
                    key={note.id}
                    className="bg-white rounded-lg p-3.5 border border-amber-200 text-xs shadow-soft space-y-1.5"
                  >
                    <div className="flex items-center justify-between text-[11px] text-amber-950/80">
                      <span className="font-semibold flex items-center gap-1">
                        <Lock className="w-3 h-3 text-amber-700" />
                        Staff User: <span className="font-mono text-amber-800">{note.author_user_id}</span>
                      </span>
                      <span className="font-mono text-gray-400">
                        {formatDateTime(note.created_at)}
                      </span>
                    </div>
                    <p className="text-gray-800 whitespace-pre-wrap leading-relaxed">
                      {note.note_body}
                    </p>
                  </div>
                ))
              )}

              {/* Note Composer */}
              <form onSubmit={handleAddInternalNote} className="space-y-2 pt-2 border-t border-amber-200">
                {noteError && (
                  <div className="bg-rose-50 border border-rose-300 rounded p-2 text-xs text-rose-800">
                    {noteError}
                  </div>
                )}
                <textarea
                  rows={2}
                  placeholder="Add a private note (e.g. 'Investigated with warehouse: 20 defect copies re-shipped on tracking #1234')..."
                  value={noteBody}
                  onChange={(e) => setNoteBody(e.target.value)}
                  disabled={isAddingNote}
                  className="w-full rounded-lg border border-amber-300 p-2.5 text-xs bg-white focus:outline-none focus:ring-2 focus:ring-amber-600 transition resize-y"
                />
                <div className="flex justify-end">
                  <button
                    type="submit"
                    disabled={isAddingNote || !noteBody.trim()}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-amber-700 hover:bg-amber-800 text-white text-xs font-semibold shadow-soft disabled:opacity-50 transition"
                  >
                    <Lock className="w-3 h-3" />
                    <span>{isAddingNote ? 'Saving...' : 'Save Internal Note'}</span>
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>

        {/* Right Column: Workflow, Triage, Author Details, AI Copilot */}
        <div className="space-y-6">
          {/* Workflow & Status Transitions */}
          <div className="bg-white rounded-xl border border-cream-300 p-5 shadow-soft space-y-4">
            <h3 className="text-xs font-bold uppercase tracking-wider text-gray-700 pb-2 border-b border-cream-200">
              Workflow & Status
            </h3>

            <div>
              <label className="block text-[11px] font-semibold text-gray-500 uppercase tracking-wider mb-1.5">
                Current Ticket Status
              </label>
              <div className="flex items-center gap-2 mb-3">
                <StatusBadge status={ticket.status} type="ticket" size="md" />
              </div>

              <select
                value={selectedStatus}
                onChange={(e) => handleStatusChange(e.target.value)}
                disabled={isUpdatingStatus}
                className="w-full px-3 py-2 rounded-lg border border-cream-300 text-xs bg-cream-50 focus:outline-none focus:ring-2 focus:ring-brand-700 font-semibold"
              >
                {STATUSES.map((st) => (
                  <option key={st.value} value={st.value}>
                    Change to: {st.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Quick Status Buttons */}
            <div className="pt-2 border-t border-cream-200 flex flex-wrap gap-2">
              <button
                type="button"
                onClick={() => handleStatusChange('IN_PROGRESS')}
                disabled={ticket.status === 'IN_PROGRESS' || isUpdatingStatus}
                className="px-2.5 py-1 text-[11px] font-semibold rounded bg-sky-50 text-sky-800 hover:bg-sky-100 border border-sky-200 disabled:opacity-40"
              >
                Start Progress
              </button>
              <button
                type="button"
                onClick={() => handleStatusChange('RESOLVED')}
                disabled={ticket.status === 'RESOLVED' || isUpdatingStatus}
                className="px-2.5 py-1 text-[11px] font-semibold rounded bg-emerald-50 text-emerald-800 hover:bg-emerald-100 border border-emerald-200 disabled:opacity-40"
              >
                Mark Resolved
              </button>
              <button
                type="button"
                onClick={() => handleStatusChange('CLOSED')}
                disabled={ticket.status === 'CLOSED' || isUpdatingStatus}
                className="px-2.5 py-1 text-[11px] font-semibold rounded bg-gray-100 text-gray-700 hover:bg-gray-200 border border-gray-300 disabled:opacity-40"
              >
                Close Ticket
              </button>
            </div>
          </div>

          {/* Triage & Staff Assignment */}
          <div className="bg-white rounded-xl border border-cream-300 p-5 shadow-soft space-y-4">
            <h3 className="text-xs font-bold uppercase tracking-wider text-gray-700 pb-2 border-b border-cream-200">
              Triage & Assignment
            </h3>

            {/* Staff Assignment */}
            <div>
              <label className="block text-[11px] font-semibold text-gray-500 uppercase tracking-wider mb-1">
                Assigned Staff Member
              </label>
              <select
                value={selectedAssignee}
                onChange={(e) => handleAssigneeChange(e.target.value)}
                disabled={isUpdatingAssignee}
                className="w-full px-3 py-2 rounded-lg border border-cream-300 text-xs bg-cream-50 focus:outline-none focus:ring-2 focus:ring-brand-700"
              >
                <option value="">— Unassigned —</option>
                {admins.map((adm) => (
                  <option key={adm.id} value={adm.id}>
                    {adm.full_name} ({adm.email})
                  </option>
                ))}
              </select>
            </div>

            {/* Category */}
            <div>
              <label className="block text-[11px] font-semibold text-gray-500 uppercase tracking-wider mb-1">
                Category
              </label>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="w-full px-3 py-2 rounded-lg border border-cream-300 text-xs bg-cream-50 focus:outline-none focus:ring-2 focus:ring-brand-700"
              >
                {CATEGORIES.map((cat) => (
                  <option key={cat.value} value={cat.value}>
                    {cat.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Priority */}
            <div>
              <label className="block text-[11px] font-semibold text-gray-500 uppercase tracking-wider mb-1">
                Priority
              </label>
              <select
                value={selectedPriority}
                onChange={(e) => setSelectedPriority(e.target.value)}
                className="w-full px-3 py-2 rounded-lg border border-cream-300 text-xs bg-cream-50 focus:outline-none focus:ring-2 focus:ring-brand-700"
              >
                {PRIORITIES.map((pri) => (
                  <option key={pri.value} value={pri.value}>
                    {pri.label}
                  </option>
                ))}
              </select>
            </div>

            <button
              type="button"
              onClick={handleTriageUpdate}
              disabled={isUpdatingTriage || (selectedCategory === ticket.category && selectedPriority === ticket.priority)}
              className="w-full px-4 py-2 bg-brand-700 hover:bg-brand-800 text-white rounded-lg text-xs font-semibold shadow-soft disabled:opacity-40 transition"
            >
              {isUpdatingTriage ? 'Updating Triage...' : 'Save Triage Overrides'}
            </button>
          </div>

          {/* Author & Book Details Panel */}
          <div className="bg-white rounded-xl border border-cream-300 p-5 shadow-soft space-y-4">
            <h3 className="text-xs font-bold uppercase tracking-wider text-gray-700 pb-2 border-b border-cream-200">
              Author & Book Context
            </h3>

            {/* Author Card */}
            <div className="space-y-1.5 text-xs">
              <span className="text-[10px] font-bold uppercase tracking-wider text-gray-400 block">
                Author
              </span>
              <div className="font-semibold text-brand-950 text-sm">
                {ticket.author?.name || 'Unknown Author'}
              </div>
              <div className="text-gray-600 font-mono text-[11px]">
                {ticket.author?.email}
              </div>
              {ticket.author?.phone && (
                <div className="text-gray-500 text-[11px]">
                  Phone: {ticket.author.phone}
                </div>
              )}
              {ticket.author?.city && (
                <div className="text-gray-500 text-[11px]">
                  City: {ticket.author.city}
                </div>
              )}
              <div className="text-brand-700 font-mono text-[11px]">
                ID: {ticket.author_id}
              </div>
            </div>

            {/* Book Card */}
            <div className="pt-3 border-t border-cream-200 space-y-1.5 text-xs">
              <span className="text-[10px] font-bold uppercase tracking-wider text-gray-400 block">
                Associated Book
              </span>
              {ticket.book ? (
                <>
                  <div className="font-serif font-bold text-brand-950 text-sm">
                    {ticket.book.title}
                  </div>
                  <div className="text-gray-500 text-[11px]">
                    ISBN: <span className="font-mono">{ticket.book.isbn}</span>
                  </div>
                  <div className="text-gray-500 text-[11px]">
                    Genre: {ticket.book.genre}
                  </div>
                  <div>
                    <StatusBadge status={ticket.book.status} type="book_status" size="sm" />
                  </div>
                </>
              ) : (
                <div className="text-gray-400 italic text-xs">
                  General account inquiry (no book attached)
                </div>
              )}
            </div>
          </div>

          {/* Gemini AI Copilot Card */}
          <div className="bg-emerald-50/40 border border-emerald-200/90 rounded-xl p-5 shadow-soft space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-emerald-200">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-emerald-700" />
                <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-950">
                  Gemini AI Copilot
                </h3>
              </div>
              <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 text-[10px] font-mono font-bold border border-emerald-300">
                {draftResult?.model || ticket.ai_classification?.provider || 'gemini-2.5-flash'}
              </span>
            </div>

            {/* AI Classification & Triage Recommendation */}
            {(ticket.ai_classification || draftResult) && (
              <div className="space-y-2 bg-white rounded-lg p-3.5 border border-emerald-200/80 text-xs shadow-soft">
                <div className="flex items-center justify-between text-[11px] text-gray-500 font-semibold uppercase">
                  <span>AI Suggested Triage</span>
                  {(draftResult?.confidence || ticket.ai_classification?.confidence) && (
                    <span className="font-mono text-emerald-700 font-bold">
                      {Math.round(((draftResult?.confidence || ticket.ai_classification?.confidence) || 0) * 100)}% Confidence
                    </span>
                  )}
                </div>

                <div className="flex flex-wrap gap-2 pt-1">
                  <span className="px-2 py-0.5 rounded bg-emerald-50 text-emerald-900 border border-emerald-200 font-medium">
                    Category: <strong>{draftResult?.suggested_category || ticket.ai_classification?.category}</strong>
                  </span>
                  <span className="px-2 py-0.5 rounded bg-brand-50 text-brand-900 border border-brand-200 font-medium">
                    Priority: <strong>{draftResult?.suggested_priority || ticket.ai_classification?.priority}</strong>
                  </span>
                </div>

                {(draftResult?.reasoning || ticket.ai_classification?.reasoning) && (
                  <p className="text-[11px] text-gray-600 leading-relaxed pt-1 italic">
                    "{draftResult?.reasoning || ticket.ai_classification?.reasoning}"
                  </p>
                )}

                {ticket.ai_classification?.admin_override && (
                  <div className="text-[10px] text-amber-700 bg-amber-50 px-2 py-1 rounded border border-amber-200 font-semibold">
                    Admin override active — AI suggestion preserved separately.
                  </div>
                )}

                {/* Apply AI Triage Button if different */}
                {((draftResult?.suggested_category && draftResult.suggested_category !== ticket.category) ||
                  (ticket.ai_classification?.category && ticket.ai_classification.category !== ticket.category) ||
                  (draftResult?.priority_code && draftResult.priority_code !== ticket.priority)) && (
                  <div className="pt-2">
                    <button
                      type="button"
                      onClick={handleApplyAiTriage}
                      disabled={isApplyingAiTriage}
                      className="w-full px-3 py-1.5 rounded-lg bg-emerald-700 hover:bg-emerald-800 text-white text-[11px] font-semibold transition flex items-center justify-center gap-1.5 shadow-soft disabled:opacity-50"
                    >
                      {isApplyingAiTriage ? (
                        <>
                          <LoadingSpinner size="sm" />
                          <span>Applying Triage...</span>
                        </>
                      ) : (
                        <>
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          <span>Apply AI Triage to Ticket</span>
                        </>
                      )}
                    </button>
                  </div>
                )}
              </div>
            )}

            {/* AI Error / Unavailable Banner */}
            {aiError && (
              <div className="bg-rose-50 border border-rose-200 rounded-lg p-3 text-xs text-rose-800 space-y-1">
                <div className="flex items-center gap-1.5 font-bold text-rose-900">
                  <AlertCircle className="w-4 h-4 text-rose-600 flex-shrink-0" />
                  <span>AI Service Notice</span>
                </div>
                <p className="text-[11px] text-rose-700 leading-relaxed">{aiError}</p>
                <p className="text-[10px] text-gray-500">
                  You can compose and send a manual response below without AI assistance.
                </p>
              </div>
            )}

            {/* Relevant Policies Context */}
            {((draftResult?.relevant_policies && draftResult.relevant_policies.length > 0) ||
              (ticket.ai_classification?.applicable_policies && ticket.ai_classification.applicable_policies.length > 0)) && (
              <div className="space-y-1 text-xs">
                <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-900 flex items-center gap-1">
                  <BookOpen className="w-3 h-3 text-emerald-700" />
                  Referenced Operating Policies
                </span>
                <div className="flex flex-wrap gap-1.5 pt-0.5">
                  {(draftResult?.relevant_policies || ticket.ai_classification?.applicable_policies || []).map((policy: string, idx: number) => (
                    <span
                      key={idx}
                      className="px-2 py-0.5 rounded-full bg-white text-emerald-900 text-[10px] border border-emerald-200 shadow-soft"
                    >
                      {policy}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Editable AI Draft Section */}
            {draftText ? (
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <label className="text-[11px] font-bold text-emerald-950 uppercase tracking-wider">
                    Editable Draft for Staff Review
                  </label>
                  <span className="text-[10px] text-gray-400">
                    Never auto-sent to author
                  </span>
                </div>

                <textarea
                  rows={6}
                  value={draftText}
                  onChange={(e) => setDraftText(e.target.value)}
                  placeholder="AI-generated draft proposal..."
                  className="w-full rounded-lg border border-emerald-300 p-3 text-xs bg-white focus:outline-none focus:ring-2 focus:ring-emerald-600 font-sans leading-relaxed transition resize-y shadow-soft"
                />

                <div className="flex items-center gap-2 pt-1">
                  <button
                    type="button"
                    onClick={handleInsertDraftIntoReply}
                    className="flex-1 inline-flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg bg-emerald-700 hover:bg-emerald-800 text-white text-xs font-semibold shadow-soft transition"
                    title="Insert this draft into author response composer"
                  >
                    <ArrowDownToLine className="w-3.5 h-3.5" />
                    <span>Insert into Response</span>
                  </button>

                  <button
                    type="button"
                    onClick={handleCopyDraft}
                    className="px-3 py-2 rounded-lg bg-white hover:bg-cream-100 text-gray-700 border border-cream-300 text-xs font-semibold shadow-soft transition inline-flex items-center gap-1"
                    title="Copy draft to clipboard"
                  >
                    {copiedDraft ? (
                      <>
                        <Check className="w-3.5 h-3.5 text-emerald-600" />
                        <span className="text-emerald-700">Copied</span>
                      </>
                    ) : (
                      <>
                        <Copy className="w-3.5 h-3.5 text-gray-500" />
                        <span>Copy</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            ) : null}

            {/* Generate / Regenerate Action Button */}
            <div>
              <button
                type="button"
                onClick={handleGenerateAiDraft}
                disabled={isGeneratingDraft}
                className="w-full inline-flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-white hover:bg-cream-100 text-emerald-900 border border-emerald-300 text-xs font-semibold shadow-soft disabled:opacity-50 transition"
              >
                {isGeneratingDraft ? (
                  <>
                    <LoadingSpinner size="sm" />
                    <span>Consulting BookLeaf Policy & Drafting...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-3.5 h-3.5 text-emerald-600" />
                    <span>{draftText ? 'Regenerate AI Draft' : 'Generate AI Response Draft'}</span>
                  </>
                )}
              </button>
              <p className="text-[10px] text-gray-400 text-center mt-1.5">
                Grounds draft on official BookLeaf royalty, printing, distribution, and production policies.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
