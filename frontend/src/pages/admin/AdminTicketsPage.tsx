import React, { useEffect, useState, useCallback } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { 
  Inbox, 
  Search, 
  X, 
  ChevronLeft, 
  ChevronRight, 
  Clock, 
  BookOpen, 
  ShieldCheck, 
  AlertCircle,
  RefreshCw,
  Calendar
} from 'lucide-react';
import { api } from '../../services/api';
import type { AdminTicket, AdminUserSummary, AdminTicketFilters } from '../../types/admin';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { StatusBadge } from '../../components/common/StatusBadge';
import { formatDateTime } from '../../utils/formatters';

const CATEGORIES = [
  { value: '', label: 'All Categories' },
  { value: 'GENERAL_INQUIRY', label: 'General / Account' },
  { value: 'ROYALTY', label: 'Royalty & Payouts' },
  { value: 'PRINT_QUALITY', label: 'Print Quality & Defect' },
  { value: 'DISTRIBUTION', label: 'Distribution & Retail' },
  { value: 'COVER_DESIGN', label: 'Cover & Interior Design' },
  { value: 'METADATA_UPDATE', label: 'Metadata & Listing Updates' },
];

const PRIORITIES = [
  { value: '', label: 'All Priorities' },
  { value: 'LOW', label: 'Low' },
  { value: 'MEDIUM', label: 'Medium' },
  { value: 'HIGH', label: 'High' },
  { value: 'URGENT', label: 'Urgent' },
];

const STATUSES = [
  { value: '', label: 'All Statuses' },
  { value: 'OPEN', label: 'Open' },
  { value: 'IN_PROGRESS', label: 'In Progress' },
  { value: 'WAITING_ON_AUTHOR', label: 'Awaiting Author Reply' },
  { value: 'RESOLVED', label: 'Resolved' },
  { value: 'CLOSED', label: 'Closed' },
  { value: 'RESOLVED,CLOSED', label: 'Resolved & Closed' },
];

const PAGE_SIZE = 20;

export const AdminTicketsPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();

  // State
  const [tickets, setTickets] = useState<AdminTicket[]>([]);
  const [hasNextPage, setHasNextPage] = useState<boolean>(false);
  const [admins, setAdmins] = useState<AdminUserSummary[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Filters from URL or default
  const statusParam = searchParams.get('status') || '';
  const priorityParam = searchParams.get('priority') || '';
  const categoryParam = searchParams.get('category') || '';
  const assignedToParam = searchParams.get('assigned_to_id') || '';
  const searchParam = searchParams.get('search') || '';
  const dateFromParam = searchParams.get('date_from') || '';
  const dateToParam = searchParams.get('date_to') || '';
  const pageParam = parseInt(searchParams.get('page') || '1', 10);

  // Filter form inputs
  const [status, setStatus] = useState<string>(statusParam);
  const [priority, setPriority] = useState<string>(priorityParam);
  const [category, setCategory] = useState<string>(categoryParam);
  const [assignedToId, setAssignedToId] = useState<string>(assignedToParam);
  const [searchInput, setSearchInput] = useState<string>(searchParam);
  const [dateFrom, setDateFrom] = useState<string>(dateFromParam);
  const [dateTo, setDateTo] = useState<string>(dateToParam);

  // Fetch admin users for filter dropdown
  useEffect(() => {
    const fetchAdmins = async () => {
      try {
        const staffList = await api.admin.getAdmins();
        setAdmins(staffList);
      } catch (err) {
        console.error('Failed to load admin staff list:', err);
      }
    };
    fetchAdmins();
  }, []);

  // Sync state when URL params change
  useEffect(() => {
    setStatus(statusParam);
    setPriority(priorityParam);
    setCategory(categoryParam);
    setAssignedToId(assignedToParam);
    setSearchInput(searchParam);
    setDateFrom(dateFromParam);
    setDateTo(dateToParam);
  }, [statusParam, priorityParam, categoryParam, assignedToParam, searchParam, dateFromParam, dateToParam]);

  // Load tickets based on current URL query params
  const fetchTickets = useCallback(async (silent = false) => {
    if (!silent) setLoading(true);
    setError(null);

    const skip = (pageParam - 1) * PAGE_SIZE;

    const filterPayload: AdminTicketFilters = {
      skip,
      limit: PAGE_SIZE + 1,
    };

    if (statusParam) filterPayload.status = statusParam;
    if (priorityParam) filterPayload.priority = priorityParam;
    if (categoryParam) filterPayload.category = categoryParam;
    if (assignedToParam) filterPayload.assigned_to_id = assignedToParam;
    if (searchParam) filterPayload.search = searchParam;
    if (dateFromParam) filterPayload.date_from = dateFromParam;
    if (dateToParam) filterPayload.date_to = dateToParam;

    try {
      const data = await api.admin.getTickets(filterPayload);
      if (data.length > PAGE_SIZE) {
        setHasNextPage(true);
        setTickets(data.slice(0, PAGE_SIZE));
      } else {
        setHasNextPage(false);
        setTickets(data);
      }
    } catch (err: any) {
      if (!silent) setError(err.message || 'Failed to fetch tickets from admin queue.');
    } finally {
      if (!silent) setLoading(false);
    }
  }, [statusParam, priorityParam, categoryParam, assignedToParam, searchParam, dateFromParam, dateToParam, pageParam]);

  useEffect(() => {
    fetchTickets(false);
    const interval = setInterval(() => {
      fetchTickets(true);
    }, 15000); // Auto-refresh ticket queue every 15s
    return () => clearInterval(interval);
  }, [fetchTickets]);

  // Apply filters by pushing to URL search params
  const handleApplyFilters = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const nextParams = new URLSearchParams();

    if (status) nextParams.set('status', status);
    if (priority) nextParams.set('priority', priority);
    if (category) nextParams.set('category', category);
    if (assignedToId) nextParams.set('assigned_to_id', assignedToId);
    if (searchInput.trim()) nextParams.set('search', searchInput.trim());
    if (dateFrom) nextParams.set('date_from', dateFrom);
    if (dateTo) nextParams.set('date_to', dateTo);
    nextParams.set('page', '1'); // Reset to page 1

    setSearchParams(nextParams);
  };

  const handleResetFilters = () => {
    setStatus('');
    setPriority('');
    setCategory('');
    setAssignedToId('');
    setSearchInput('');
    setDateFrom('');
    setDateTo('');
    setSearchParams(new URLSearchParams());
  };

  const handlePageChange = (newPage: number) => {
    if (newPage < 1) return;
    const nextParams = new URLSearchParams(searchParams);
    nextParams.set('page', newPage.toString());
    setSearchParams(nextParams);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const [currentTime] = useState(() => Date.now());

  // Helper: Detect tickets older than 48 hours that remain open
  const isAgingTicket = (createdAtIso: string, ticketStatus: string) => {
    if (['RESOLVED', 'CLOSED'].includes(ticketStatus)) return false;
    const createdTime = new Date(createdAtIso).getTime();
    const diffHours = (currentTime - createdTime) / (1000 * 60 * 60);
    return diffHours >= 48;
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-cream-300">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2 py-0.5 rounded bg-brand-100 text-brand-900 font-mono text-[11px] font-bold uppercase tracking-wider">
              Admin Queue
            </span>
            <span className="text-xs text-gray-400">• Cross-Tenant Management</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-serif font-bold text-brand-950">
            Administrative Ticket Queue
          </h1>
          <p className="text-xs text-gray-600 mt-0.5">
            Triage, assign, reply to authors, and log private internal notes across the entire publishing catalog.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => fetchTickets()}
            disabled={loading}
            className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg bg-white border border-cream-300 text-xs font-semibold text-gray-700 hover:text-brand-950 hover:bg-cream-50 transition shadow-soft"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh Queue</span>
          </button>
        </div>
      </div>

      {/* Filter & Search Bar */}
      <form 
        onSubmit={handleApplyFilters}
        className="bg-white rounded-xl border border-cream-300 shadow-soft p-4 space-y-3"
      >
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3">
          {/* Search Input */}
          <div className="lg:col-span-2">
            <label className="block text-[10px] font-semibold uppercase tracking-wider text-gray-500 mb-1">
              Search
            </label>
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="ID, subject, author..."
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                className="w-full pl-8 pr-3 py-1.5 text-xs bg-cream-50 border border-cream-300 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-brand-700 focus:bg-white"
              />
            </div>
          </div>

          {/* Status Filter */}
          <div>
            <label className="block text-[10px] font-semibold uppercase tracking-wider text-gray-500 mb-1">
              Status
            </label>
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              className="w-full px-2.5 py-1.5 text-xs bg-cream-50 border border-cream-300 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-brand-700"
            >
              {STATUSES.map((s) => (
                <option key={s.value} value={s.value}>
                  {s.label}
                </option>
              ))}
            </select>
          </div>

          {/* Priority Filter */}
          <div>
            <label className="block text-[10px] font-semibold uppercase tracking-wider text-gray-500 mb-1">
              Priority
            </label>
            <select
              value={priority}
              onChange={(e) => setPriority(e.target.value)}
              className="w-full px-2.5 py-1.5 text-xs bg-cream-50 border border-cream-300 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-brand-700"
            >
              {PRIORITIES.map((p) => (
                <option key={p.value} value={p.value}>
                  {p.label}
                </option>
              ))}
            </select>
          </div>

          {/* Category Filter */}
          <div>
            <label className="block text-[10px] font-semibold uppercase tracking-wider text-gray-500 mb-1">
              Category
            </label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full px-2.5 py-1.5 text-xs bg-cream-50 border border-cream-300 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-brand-700"
            >
              {CATEGORIES.map((c) => (
                <option key={c.value} value={c.value}>
                  {c.label}
                </option>
              ))}
            </select>
          </div>

          {/* Assigned Staff Filter */}
          <div>
            <label className="block text-[10px] font-semibold uppercase tracking-wider text-gray-500 mb-1">
              Assigned Staff
            </label>
            <select
              value={assignedToId}
              onChange={(e) => setAssignedToId(e.target.value)}
              className="w-full px-2.5 py-1.5 text-xs bg-cream-50 border border-cream-300 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-brand-700"
            >
              <option value="">All Staff</option>
              {admins.map((adm) => (
                <option key={adm.id} value={adm.id}>
                  {adm.full_name}
                </option>
              ))}
            </select>
          </div>

          {/* Action Buttons */}
          <div className="flex items-end gap-2">
            <button
              type="submit"
              className="w-full px-3 py-1.5 bg-brand-700 hover:bg-brand-800 text-white rounded-lg text-xs font-semibold shadow-soft transition"
            >
              Filter
            </button>
            <button
              type="button"
              onClick={handleResetFilters}
              className="p-1.5 text-gray-500 hover:text-gray-900 hover:bg-cream-100 border border-cream-300 rounded-lg transition"
              title="Reset all filters"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Date Range Collapsible Row */}
        <div className="pt-2 border-t border-cream-200 flex flex-wrap items-center gap-4 text-xs text-gray-600">
          <span className="text-[11px] font-semibold flex items-center gap-1 text-gray-500">
            <Calendar className="w-3.5 h-3.5" /> Date Range:
          </span>
          <div className="flex items-center gap-2">
            <span className="text-[11px] text-gray-500">From</span>
            <input
              type="date"
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
              className="px-2 py-1 text-xs bg-cream-50 border border-cream-300 rounded text-gray-800 focus:outline-none focus:ring-1 focus:ring-brand-700"
            />
          </div>
          <div className="flex items-center gap-2">
            <span className="text-[11px] text-gray-500">To</span>
            <input
              type="date"
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
              className="px-2 py-1 text-xs bg-cream-50 border border-cream-300 rounded text-gray-800 focus:outline-none focus:ring-1 focus:ring-brand-700"
            />
          </div>
          {(dateFrom || dateTo) && (
            <button
              type="button"
              onClick={() => { setDateFrom(''); setDateTo(''); handleApplyFilters(); }}
              className="text-[11px] text-brand-700 hover:underline"
            >
              Clear dates
            </button>
          )}
        </div>
      </form>

      {/* Error State */}
      {error && (
        <div className="bg-rose-50 border border-rose-200 rounded-xl p-4 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-rose-600 flex-shrink-0 mt-0.5" />
          <div className="text-xs text-rose-900">
            <span className="font-semibold block">Failed to load ticket queue</span>
            {error}
          </div>
        </div>
      )}

      {/* Ticket Queue Listing */}
      {loading ? (
        <LoadingSpinner size="lg" message="Loading administrative queue..." />
      ) : tickets.length === 0 ? (
        <div className="bg-white rounded-xl border border-cream-300 p-12 text-center shadow-soft">
          <div className="w-12 h-12 rounded-full bg-cream-100 text-brand-700 flex items-center justify-center mx-auto mb-3">
            <Inbox className="w-6 h-6" />
          </div>
          <h3 className="text-base font-semibold text-brand-950">
            {pageParam > 1 ? `No tickets found on page ${pageParam}` : 'No tickets match current filters'}
          </h3>
          <p className="text-xs text-gray-500 max-w-sm mx-auto mt-1 mb-4">
            {pageParam > 1
              ? 'You have reached beyond the end of the available ticket list.'
              : 'Try adjusting status, priority, staff assignment, or search queries.'}
          </p>
          <div className="flex items-center justify-center gap-3">
            {pageParam > 1 && (
              <button
                onClick={() => handlePageChange(pageParam - 1)}
                className="px-4 py-2 bg-brand-700 hover:bg-brand-800 text-white rounded-lg text-xs font-semibold shadow-soft transition cursor-pointer"
              >
                ← Back to Page {pageParam - 1}
              </button>
            )}
            <button
              onClick={handleResetFilters}
              className="px-4 py-2 border border-cream-300 bg-white hover:bg-cream-100 text-gray-700 rounded-lg text-xs font-semibold shadow-soft transition cursor-pointer"
            >
              Reset Filters
            </button>
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-cream-300 shadow-soft overflow-hidden">
          {/* Desktop Table View */}
          <div className="hidden lg:block overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-cream-100 border-b border-cream-300 text-[11px] font-semibold text-gray-600 uppercase tracking-wider">
                  <th className="py-3 px-4">Ticket / Priority</th>
                  <th className="py-3 px-4">Subject & Book</th>
                  <th className="py-3 px-4">Author Details</th>
                  <th className="py-3 px-4">Category</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Assignee</th>
                  <th className="py-3 px-4">Created</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-cream-200 text-xs">
                {tickets.map((ticket) => {
                  const isUrgent = ['URGENT', 'HIGH'].includes(ticket.priority) && !['RESOLVED', 'CLOSED'].includes(ticket.status);
                  const aging = isAgingTicket(ticket.created_at, ticket.status);

                  return (
                    <tr
                      key={ticket.id}
                      className={`hover:bg-cream-50/80 transition group ${
                        isUrgent ? 'bg-rose-50/40' : aging ? 'bg-amber-50/30' : ''
                      }`}
                    >
                      {/* Ticket Number & Priority */}
                      <td className="py-3.5 px-4">
                        <Link
                          to={`/admin/tickets/${ticket.id}`}
                          className="font-mono font-bold text-brand-900 group-hover:underline flex items-center gap-1.5"
                        >
                          <span>{ticket.ticket_number}</span>
                        </Link>
                        <div className="mt-1 flex items-center gap-1">
                          <StatusBadge status={ticket.priority} type="priority" size="sm" />
                          {aging && (
                            <span 
                              className="px-1.5 py-0.2 rounded bg-amber-100 text-amber-900 text-[10px] font-semibold border border-amber-300 flex items-center gap-1"
                              title="Unresolved for over 48 hours"
                            >
                              <Clock className="w-2.5 h-2.5 text-amber-700" /> &gt;48h
                            </span>
                          )}
                        </div>
                      </td>

                      {/* Subject & Book */}
                      <td className="py-3.5 px-4 max-w-[280px]">
                        <Link
                          to={`/admin/tickets/${ticket.id}`}
                          className="font-semibold text-brand-950 group-hover:text-brand-700 transition block truncate"
                          title={ticket.subject}
                        >
                          {ticket.subject}
                        </Link>
                        <div className="flex items-center gap-2 mt-0.5 text-[11px] text-gray-500">
                          {ticket.book ? (
                            <span className="flex items-center gap-1 text-gray-600 truncate">
                              <BookOpen className="w-3 h-3 text-brand-600 flex-shrink-0" />
                              <span className="truncate">{ticket.book.title}</span>
                            </span>
                          ) : (
                            <span className="text-gray-400 italic">General Inquiry</span>
                          )}
                        </div>
                      </td>

                      {/* Author */}
                      <td className="py-3.5 px-4">
                        <div className="font-medium text-gray-900">
                          {ticket.author?.name || 'Unknown Author'}
                        </div>
                        <div className="text-[11px] text-gray-500 font-mono">
                          {ticket.author?.email || ticket.author_id}
                        </div>
                      </td>

                      {/* Category */}
                      <td className="py-3.5 px-4 text-gray-600">
                        <span className="inline-block px-2 py-0.5 rounded bg-cream-100 text-brand-900 border border-cream-200 text-[10px] font-medium">
                          {ticket.category?.replace(/_/g, ' ') || 'GENERAL'}
                        </span>
                      </td>

                      {/* Status */}
                      <td className="py-3.5 px-4">
                        <StatusBadge status={ticket.status} type="ticket" size="sm" />
                      </td>

                      {/* Assigned Admin */}
                      <td className="py-3.5 px-4">
                        {ticket.assigned_to ? (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-emerald-50 text-emerald-900 border border-emerald-200 text-[11px] font-medium">
                            <ShieldCheck className="w-3 h-3 text-emerald-600" />
                            <span>{ticket.assigned_to.full_name}</span>
                          </span>
                        ) : (
                          <span className="text-gray-400 italic text-[11px]">Unassigned</span>
                        )}
                      </td>

                      {/* Creation Date */}
                      <td className="py-3.5 px-4 text-[11px] text-gray-500 font-mono">
                        {formatDateTime(ticket.created_at)}
                      </td>

                      {/* Action */}
                      <td className="py-3.5 px-4 text-right">
                        <Link
                          to={`/admin/tickets/${ticket.id}`}
                          className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-cream-100 text-brand-900 font-semibold hover:bg-brand-700 hover:text-white transition"
                        >
                          <span>Manage</span>
                        </Link>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Mobile / Tablet Cards */}
          <div className="lg:hidden divide-y divide-cream-200">
            {tickets.map((ticket) => (
              <Link
                key={ticket.id}
                to={`/admin/tickets/${ticket.id}`}
                className="block p-4 hover:bg-cream-50 transition"
              >
                <div className="flex items-center justify-between mb-1.5">
                  <span className="font-mono font-bold text-xs text-brand-900">
                    {ticket.ticket_number}
                  </span>
                  <div className="flex items-center gap-1.5">
                    <StatusBadge status={ticket.priority} type="priority" size="sm" />
                    <StatusBadge status={ticket.status} type="ticket" size="sm" />
                  </div>
                </div>

                <h4 className="font-semibold text-brand-950 text-sm mb-1">
                  {ticket.subject}
                </h4>

                <div className="flex items-center justify-between text-xs text-gray-600 mb-2">
                  <span>Author: {ticket.author?.name} ({ticket.author_id})</span>
                  <span>{ticket.assigned_to ? ticket.assigned_to.full_name : 'Unassigned'}</span>
                </div>

                <div className="flex items-center justify-between text-[11px] text-gray-400 pt-2 border-t border-cream-200">
                  <span>{formatDateTime(ticket.created_at)}</span>
                  <span className="font-semibold text-brand-700">Open Ticket →</span>
                </div>
              </Link>
            ))}
          </div>

          {/* Pagination Controls */}
          <div className="p-4 bg-cream-50/50 border-t border-cream-300 flex items-center justify-between text-xs">
            <span className="text-gray-500">
              Showing page <strong>{pageParam}</strong> ({tickets.length} tickets shown)
            </span>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => handlePageChange(pageParam - 1)}
                disabled={pageParam <= 1 || loading}
                title={pageParam <= 1 ? 'You are on the first page' : 'Go to previous page'}
                className="inline-flex items-center gap-1 px-3 py-1.5 rounded border border-cream-300 bg-white text-gray-700 hover:bg-cream-100 disabled:opacity-30 disabled:cursor-not-allowed disabled:bg-cream-100 disabled:text-gray-400 transition"
              >
                <ChevronLeft className="w-3.5 h-3.5" />
                <span>Previous</span>
              </button>
              <button
                type="button"
                onClick={() => handlePageChange(pageParam + 1)}
                disabled={!hasNextPage || loading}
                title={!hasNextPage ? 'No more tickets in this queue' : 'Go to next page'}
                className="inline-flex items-center gap-1 px-3 py-1.5 rounded border border-cream-300 bg-white text-gray-700 hover:bg-cream-100 disabled:opacity-30 disabled:cursor-not-allowed disabled:bg-cream-100 disabled:text-gray-400 transition"
              >
                <span>Next</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
