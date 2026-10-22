import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  Inbox, 
  AlertTriangle, 
  Clock, 
  CheckCircle2, 
  ArrowUpRight, 
  RefreshCw, 
  AlertCircle,
  BookOpen,
  User,
  ShieldCheck
} from 'lucide-react';
import { api } from '../../services/api';
import type { AdminTicket } from '../../types/admin';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { StatusBadge } from '../../components/common/StatusBadge';
import { formatDateTime } from '../../utils/formatters';

export const AdminDashboardPage: React.FC = () => {
  const [tickets, setTickets] = useState<AdminTicket[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchOverviewData = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.admin.getTickets({ limit: 100 });
      setTickets(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load administrative overview.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOverviewData();
  }, []);

  // Compute metrics from actual ticket data
  const totalTickets = tickets.length;
  const openTickets = tickets.filter((t) => t.status === 'OPEN').length;
  const inProgressTickets = tickets.filter((t) => t.status === 'IN_PROGRESS').length;
  const waitingOnAuthor = tickets.filter((t) => t.status === 'WAITING_ON_AUTHOR').length;
  const resolvedTickets = tickets.filter((t) => ['RESOLVED', 'CLOSED'].includes(t.status)).length;
  
  const urgentTickets = tickets.filter((t) => ['URGENT', 'HIGH'].includes(t.priority) && !['RESOLVED', 'CLOSED'].includes(t.status));
  const unassignedTickets = tickets.filter((t) => !t.assigned_to_id && !['RESOLVED', 'CLOSED'].includes(t.status));

  // Urgent and high priority tickets requiring operational attention
  const priorityTickets = urgentTickets.slice(0, 5);

  // Recent unresolved tickets
  const recentActiveTickets = tickets
    .filter((t) => !['RESOLVED', 'CLOSED'].includes(t.status))
    .slice(0, 6);

  if (loading) {
    return <LoadingSpinner size="lg" message="Loading operations metrics..." />;
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-rose-50 border border-rose-200 rounded-xl p-6 flex items-start gap-4">
          <AlertCircle className="w-6 h-6 text-rose-600 flex-shrink-0" />
          <div>
            <h3 className="text-base font-semibold text-rose-900">Failed to load admin overview</h3>
            <p className="text-sm text-rose-700 mt-1">{error}</p>
            <button
              onClick={fetchOverviewData}
              className="mt-4 px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white rounded-lg text-xs font-semibold"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-6 border-b border-cream-300">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2 py-0.5 rounded bg-brand-100 text-brand-900 font-mono text-[11px] font-bold uppercase tracking-wider">
              Operations Center
            </span>
            <span className="text-xs text-gray-400">• Cross-Author Support Queue</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-serif font-bold text-brand-950">
            Support Operations Overview
          </h1>
          <p className="text-sm text-gray-600 mt-0.5">
            Real-time ticket volume, triage queues, priority escalations, and staff workflows.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchOverviewData}
            className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg bg-white border border-cream-300 text-xs font-semibold text-gray-700 hover:text-brand-950 hover:bg-cream-50 transition shadow-soft"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Refresh</span>
          </button>
          <Link
            to="/admin/tickets"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-brand-700 hover:bg-brand-800 text-white text-xs font-semibold shadow-soft transition"
          >
            <Inbox className="w-4 h-4" />
            <span>Open Ticket Queue</span>
          </Link>
        </div>
      </div>

      {/* Primary KPI Metrics */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3.5">
        {/* Total */}
        <div className="bg-white p-4 rounded-xl border border-cream-300 shadow-soft">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-gray-500 block">
            Total Tickets
          </span>
          <div className="text-2xl font-bold font-serif text-brand-950 mt-1">
            {totalTickets}
          </div>
          <span className="text-[10px] text-gray-400 mt-0.5 block">Across all authors</span>
        </div>

        {/* Urgent & High Priority */}
        <Link 
          to="/admin/tickets?priority=URGENT"
          className={`p-4 rounded-xl border shadow-soft transition block ${
            urgentTickets.length > 0 
              ? 'bg-rose-50/70 border-rose-200 hover:bg-rose-50' 
              : 'bg-white border-cream-300 hover:bg-cream-50'
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-rose-800">
              Urgent / High
            </span>
            <AlertTriangle className="w-4 h-4 text-rose-600" />
          </div>
          <div className="text-2xl font-bold font-serif text-rose-900 mt-1">
            {urgentTickets.length}
          </div>
          <span className="text-[10px] text-rose-700 mt-0.5 block">Requires immediate action</span>
        </Link>

        {/* Open */}
        <Link 
          to="/admin/tickets?status=OPEN"
          className="bg-white p-4 rounded-xl border border-cream-300 shadow-soft hover:bg-cream-50 transition block"
        >
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-emerald-800">
              Open Queue
            </span>
            <Inbox className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="text-2xl font-bold font-serif text-brand-950 mt-1">
            {openTickets}
          </div>
          <span className="text-[10px] text-emerald-700 mt-0.5 block">Unresolved inquiries</span>
        </Link>

        {/* In Progress */}
        <Link 
          to="/admin/tickets?status=IN_PROGRESS"
          className="bg-white p-4 rounded-xl border border-cream-300 shadow-soft hover:bg-cream-50 transition block"
        >
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-sky-800">
              In Progress
            </span>
            <Clock className="w-4 h-4 text-sky-600" />
          </div>
          <div className="text-2xl font-bold font-serif text-brand-950 mt-1">
            {inProgressTickets}
          </div>
          <span className="text-[10px] text-sky-700 mt-0.5 block">Actively handled</span>
        </Link>

        {/* Waiting on Author */}
        <Link 
          to="/admin/tickets?status=WAITING_ON_AUTHOR"
          className="bg-white p-4 rounded-xl border border-cream-300 shadow-soft hover:bg-cream-50 transition block"
        >
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-amber-800">
              Awaiting Author
            </span>
            <User className="w-4 h-4 text-amber-600" />
          </div>
          <div className="text-2xl font-bold font-serif text-brand-950 mt-1">
            {waitingOnAuthor}
          </div>
          <span className="text-[10px] text-amber-700 mt-0.5 block">Staff replied</span>
        </Link>

        {/* Resolved / Closed */}
        <Link 
          to="/admin/tickets?status=RESOLVED"
          className="bg-white p-4 rounded-xl border border-cream-300 shadow-soft hover:bg-cream-50 transition block"
        >
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-gray-600">
              Resolved / Closed
            </span>
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="text-2xl font-bold font-serif text-brand-950 mt-1">
            {resolvedTickets}
          </div>
          <span className="text-[10px] text-gray-500 mt-0.5 block">{unassignedTickets.length} unassigned tickets</span>
        </Link>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left 2 cols: Active Ticket Queue Preview */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-serif font-bold text-brand-950 flex items-center gap-2">
              <span>Active Support Queue</span>
              <span className="text-xs font-normal text-gray-500">
                (Unresolved, newest first)
              </span>
            </h2>
            <Link
              to="/admin/tickets"
              className="text-xs font-semibold text-brand-700 hover:text-brand-900 flex items-center gap-1"
            >
              <span>View all tickets</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="bg-white rounded-xl border border-cream-300 shadow-soft divide-y divide-cream-200 overflow-hidden">
            {recentActiveTickets.length === 0 ? (
              <div className="p-8 text-center text-xs text-gray-500">
                <CheckCircle2 className="w-8 h-8 text-emerald-500 mx-auto mb-2" />
                All support queues are currently clear! No active unresolved tickets.
              </div>
            ) : (
              recentActiveTickets.map((ticket) => (
                <Link
                  key={ticket.id}
                  to={`/admin/tickets/${ticket.id}`}
                  className="block p-4 hover:bg-cream-50/80 transition group"
                >
                  <div className="flex items-start justify-between gap-3 mb-1.5">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-semibold text-brand-800">
                        {ticket.ticket_number}
                      </span>
                      <StatusBadge status={ticket.priority} type="priority" />
                      <StatusBadge status={ticket.status} type="ticket" />
                    </div>
                    <span className="text-[11px] text-gray-400 font-mono">
                      {formatDateTime(ticket.created_at)}
                    </span>
                  </div>

                  <h3 className="text-sm font-semibold text-brand-950 group-hover:text-brand-700 transition line-clamp-1 mb-1">
                    {ticket.subject}
                  </h3>

                  <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-gray-600">
                    <span className="flex items-center gap-1 text-gray-800">
                      <User className="w-3.5 h-3.5 text-brand-600" />
                      <span className="font-medium">{ticket.author?.name || 'Author'}</span>
                      <span className="text-[11px] text-gray-400">({ticket.author_id})</span>
                    </span>

                    {ticket.book && (
                      <span className="flex items-center gap-1 text-gray-600">
                        <BookOpen className="w-3.5 h-3.5 text-gray-400" />
                        <span className="truncate max-w-[200px]">{ticket.book.title}</span>
                      </span>
                    )}

                    <span className="ml-auto text-[11px] font-medium text-brand-700 group-hover:underline">
                      Manage Ticket →
                    </span>
                  </div>
                </Link>
              ))
            )}
          </div>
        </div>

        {/* Right col: Urgent Alerts & AI Copilot Preview */}
        <div className="space-y-6">
          {/* Urgent Tickets Alert Box */}
          <div className="bg-white rounded-xl border border-cream-300 shadow-soft p-5 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-cream-200">
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-rose-600" />
                <h3 className="text-sm font-serif font-bold text-brand-950">
                  Priority Escalations
                </h3>
              </div>
              <span className="px-2 py-0.5 rounded-full bg-rose-100 text-rose-800 text-[10px] font-bold">
                {urgentTickets.length} Pending
              </span>
            </div>

            {priorityTickets.length === 0 ? (
              <p className="text-xs text-gray-500 py-2">
                No urgent tickets requiring immediate intervention.
              </p>
            ) : (
              <ul className="space-y-3">
                {priorityTickets.map((ticket) => (
                  <li key={ticket.id} className="text-xs">
                    <Link
                      to={`/admin/tickets/${ticket.id}`}
                      className="block p-2.5 rounded-lg bg-rose-50/50 hover:bg-rose-50 border border-rose-200 transition"
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-mono text-[11px] font-bold text-rose-900">
                          {ticket.ticket_number}
                        </span>
                        <StatusBadge status={ticket.priority} type="priority" size="sm" />
                      </div>
                      <p className="font-medium text-gray-900 truncate">
                        {ticket.subject}
                      </p>
                      <span className="text-[10px] text-gray-500 mt-1 block">
                        Author: {ticket.author?.name}
                      </span>
                    </Link>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* AI Integration Placeholder Notice (Section 6) */}
          <div className="bg-brand-900 text-white rounded-xl p-5 shadow-soft space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-emerald-300 text-xs font-semibold uppercase tracking-wider">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                <span>Gemini AI Copilot</span>
              </div>
              <span className="px-2 py-0.5 rounded bg-brand-800 text-brand-300 text-[10px] font-mono border border-brand-700">
                Prompt 5 Ready
              </span>
            </div>

            <p className="text-xs text-brand-200 leading-relaxed">
              Automated category classification, priority inference, and AI-suggested draft replies are prepared for activation in Phase 5.
            </p>

            <div className="pt-2 border-t border-brand-800 text-[11px] text-brand-300">
              Manual triage, status transitions, staff assignment, author responses, and confidential internal notes are fully active.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
