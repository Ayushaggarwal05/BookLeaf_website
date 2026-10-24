import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  LifeBuoy, 
  PlusCircle, 
  Search, 
  BookOpen, 
  ChevronRight, 
  AlertCircle
} from 'lucide-react';
import { api } from '../services/api';
import type { AuthorTicket } from '../types/ticket';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { StatusBadge } from '../components/common/StatusBadge';

type StatusFilter = 'ALL' | 'ACTIVE' | 'WAITING_ON_AUTHOR' | 'RESOLVED';

export const TicketsPage: React.FC = () => {
  const [tickets, setTickets] = useState<AuthorTicket[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Filters & search
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('ALL');

  const fetchTickets = async (silent = false) => {
    if (!silent) setLoading(true);
    setError(null);
    try {
      const data = await api.author.getTickets();
      setTickets(data);
    } catch (err: any) {
      if (!silent) setError(err.message || 'Failed to load support tickets.');
    } finally {
      if (!silent) setLoading(false);
    }
  };

  useEffect(() => {
    fetchTickets(false);
    const interval = setInterval(() => {
      fetchTickets(true);
    }, 15000); // Auto-refresh author tickets every 15s
    return () => clearInterval(interval);
  }, []);

  // Filter logic
  const filteredTickets = tickets.filter((ticket) => {
    // 1. Status Filter
    if (statusFilter === 'ACTIVE') {
      const activeStatuses = ['OPEN', 'IN_PROGRESS', 'WAITING_ON_AUTHOR'];
      if (!activeStatuses.includes(ticket.status)) return false;
    } else if (statusFilter === 'WAITING_ON_AUTHOR') {
      if (ticket.status !== 'WAITING_ON_AUTHOR') return false;
    } else if (statusFilter === 'RESOLVED') {
      const closedStatuses = ['RESOLVED', 'CLOSED'];
      if (!closedStatuses.includes(ticket.status)) return false;
    }

    // 2. Search query filter
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const matchSubject = ticket.subject.toLowerCase().includes(q);
      const matchNumber = ticket.ticket_number.toLowerCase().includes(q);
      const matchBook = ticket.book_title?.toLowerCase().includes(q) || false;
      const matchCategory = ticket.category?.toLowerCase().includes(q);
      if (!matchSubject && !matchNumber && !matchBook && !matchCategory) {
        return false;
      }
    }

    return true;
  });

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

  const getStatusCount = (filter: StatusFilter) => {
    if (filter === 'ALL') return tickets.length;
    if (filter === 'ACTIVE') {
      return tickets.filter((t) => ['OPEN', 'IN_PROGRESS', 'WAITING_ON_AUTHOR'].includes(t.status)).length;
    }
    if (filter === 'WAITING_ON_AUTHOR') {
      return tickets.filter((t) => t.status === 'WAITING_ON_AUTHOR').length;
    }
    if (filter === 'RESOLVED') {
      return tickets.filter((t) => ['RESOLVED', 'CLOSED'].includes(t.status)).length;
    }
    return 0;
  };

  if (loading) {
    return <LoadingSpinner size="lg" message="Loading author queries..." />;
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="bg-rose-50 border border-rose-200 rounded-xl p-6 flex items-start gap-4">
          <AlertCircle className="w-6 h-6 text-rose-600 flex-shrink-0" />
          <div>
            <h3 className="text-base font-semibold text-rose-900">Failed to load support queries</h3>
            <p className="text-sm text-rose-700 mt-1">{error}</p>
            <button
              onClick={() => fetchTickets(false)}
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
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-6 border-b border-cream-300">
        <div>
          <h1 className="text-2xl sm:text-3xl font-serif font-bold text-brand-950">
            Support Queries
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            Track communication threads with BookLeaf publishing editors and support specialists.
          </p>
        </div>
        <div>
          <Link
            to="/tickets/new"
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg bg-brand-700 hover:bg-brand-800 text-white text-sm font-semibold shadow-soft transition"
          >
            <PlusCircle className="w-4 h-4" />
            <span>Submit a Support Query</span>
          </Link>
        </div>
      </div>

      {/* Filter Tabs and Search Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-3 rounded-xl border border-cream-300 shadow-soft">
        {/* Status Tabs */}
        <div className="flex items-center gap-1 overflow-x-auto pb-1 md:pb-0">
          {(
            [
              { key: 'ALL', label: 'All Queries' },
              { key: 'ACTIVE', label: 'Active' },
              { key: 'WAITING_ON_AUTHOR', label: 'Action Needed' },
              { key: 'RESOLVED', label: 'Resolved / Closed' },
            ] as const
          ).map((tab) => {
            const count = getStatusCount(tab.key);
            const active = statusFilter === tab.key;
            return (
              <button
                key={tab.key}
                onClick={() => setStatusFilter(tab.key)}
                className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg whitespace-nowrap transition ${
                  active
                    ? 'bg-brand-700 text-white shadow-soft'
                    : 'text-gray-600 hover:text-brand-900 hover:bg-cream-100'
                }`}
              >
                <span>{tab.label}</span>
                <span
                  className={`px-1.5 py-0.2 rounded-full text-[10px] font-mono ${
                    active ? 'bg-brand-900 text-brand-100' : 'bg-cream-200 text-gray-700'
                  }`}
                >
                  {count}
                </span>
              </button>
            );
          })}
        </div>

        {/* Search Input */}
        <div className="relative w-full md:w-72">
          <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search query, ID, book..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-3.5 py-1.5 text-xs bg-cream-50 border border-cream-300 rounded-lg text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-brand-700 focus:bg-white transition"
          />
        </div>
      </div>

      {/* Ticket List Display */}
      {filteredTickets.length === 0 ? (
        <div className="bg-white rounded-xl border border-cream-300 p-12 text-center shadow-soft">
          <div className="w-12 h-12 rounded-full bg-cream-100 text-brand-700 flex items-center justify-center mx-auto mb-3">
            <LifeBuoy className="w-6 h-6" />
          </div>
          <h3 className="text-base font-semibold text-brand-950">
            {tickets.length === 0 ? 'No support queries found' : 'No queries match your criteria'}
          </h3>
          <p className="text-xs text-gray-500 max-w-sm mx-auto mt-1 mb-5">
            {tickets.length === 0
              ? 'Whenever you submit an inquiry regarding editorial reviews, royalty checks, or distribution, your threads will appear here.'
              : 'Try clearing your search query or switching to another status tab to view tickets.'}
          </p>
          <Link
            to="/tickets/new"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-brand-700 hover:bg-brand-800 text-white text-xs font-semibold shadow-soft transition"
          >
            <PlusCircle className="w-4 h-4" />
            <span>Create New Support Query</span>
          </Link>
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-cream-300 shadow-soft overflow-hidden">
          {/* Desktop Table View */}
          <div className="hidden lg:block overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-cream-100 border-b border-cream-300 text-[11px] font-semibold text-gray-600 uppercase tracking-wider">
                  <th className="py-3 px-4">Ticket</th>
                  <th className="py-3 px-4">Subject & Context</th>
                  <th className="py-3 px-4">Category</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Created / Updated</th>
                  <th className="py-3 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-cream-200 text-xs">
                {filteredTickets.map((ticket) => (
                  <tr
                    key={ticket.id}
                    className="hover:bg-cream-50/70 transition group cursor-pointer"
                  >
                    {/* Ticket Number & Priority */}
                    <td className="py-4 px-4 font-mono font-medium text-brand-800">
                      <Link
                        to={`/tickets/${ticket.id}`}
                        className="hover:underline flex items-center gap-1.5"
                      >
                        <span>{ticket.ticket_number}</span>
                      </Link>
                      <div className="mt-1">
                        <StatusBadge status={ticket.priority} type="priority" />
                      </div>
                    </td>

                    {/* Subject & Book */}
                    <td className="py-4 px-4">
                      <Link
                        to={`/tickets/${ticket.id}`}
                        className="font-medium text-brand-950 group-hover:text-brand-700 transition block text-sm line-clamp-1"
                      >
                        {ticket.subject}
                      </Link>
                      <div className="flex items-center gap-2 mt-1 text-[11px] text-gray-500">
                        {ticket.book_title ? (
                          <span className="flex items-center gap-1 text-gray-600 font-serif">
                            <BookOpen className="w-3 h-3 text-brand-600" />
                            {ticket.book_title}
                          </span>
                        ) : (
                          <span className="text-gray-400 italic">General Inquiry</span>
                        )}
                        {ticket.attachments && ticket.attachments.length > 0 && (
                          <span className="bg-cream-200 text-gray-700 px-1.5 py-0.2 rounded text-[10px]">
                            {ticket.attachments.length} attachment(s)
                          </span>
                        )}
                      </div>
                    </td>

                    {/* Category */}
                    <td className="py-4 px-4 text-gray-600">
                      <span className="inline-block px-2 py-0.5 rounded bg-cream-100 text-brand-900 border border-cream-200 text-[11px] font-medium">
                        {ticket.category?.replace(/_/g, ' ') || 'GENERAL'}
                      </span>
                    </td>

                    {/* Status */}
                    <td className="py-4 px-4">
                      <StatusBadge status={ticket.status} type="ticket" perspective="author" />
                    </td>

                    {/* Dates */}
                    <td className="py-4 px-4 text-gray-500 text-[11px]">
                      <div>Created: {formatDate(ticket.created_at)}</div>
                      <div className="text-gray-400 text-[10px] mt-0.5">
                        Updated: {formatDate(ticket.updated_at)}
                      </div>
                    </td>

                    {/* Action link */}
                    <td className="py-4 px-4 text-right">
                      <Link
                        to={`/tickets/${ticket.id}`}
                        className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-cream-100 text-brand-900 font-semibold hover:bg-brand-700 hover:text-white transition"
                      >
                        <span>View Thread</span>
                        <ChevronRight className="w-3.5 h-3.5" />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Mobile / Tablet Card View */}
          <div className="lg:hidden divide-y divide-cream-200">
            {filteredTickets.map((ticket) => (
              <Link
                key={ticket.id}
                to={`/tickets/${ticket.id}`}
                className="block p-4 hover:bg-cream-50 transition"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-mono font-medium text-xs text-brand-800">
                    {ticket.ticket_number}
                  </span>
                  <StatusBadge status={ticket.status} type="ticket" perspective="author" />
                </div>
                <h4 className="font-medium text-brand-950 text-sm mb-1">
                  {ticket.subject}
                </h4>
                <div className="text-xs text-gray-500 mb-2">
                  {ticket.book_title ? (
                    <span className="flex items-center gap-1 text-gray-700">
                      <BookOpen className="w-3 h-3 text-brand-600" />
                      {ticket.book_title}
                    </span>
                  ) : (
                    <span className="text-gray-400 italic">General Account Inquiry</span>
                  )}
                </div>
                <div className="flex items-center justify-between text-[11px] text-gray-400 pt-2 border-t border-cream-200">
                  <span>{formatDate(ticket.created_at)}</span>
                  <span className="font-medium text-brand-700 flex items-center gap-1">
                    Open thread <ChevronRight className="w-3 h-3" />
                  </span>
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
