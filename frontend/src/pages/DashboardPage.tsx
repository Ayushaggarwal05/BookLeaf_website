import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { BookOpen, Wallet, LifeBuoy, ArrowUpRight, PlusCircle, AlertCircle, Clock, CheckCircle } from 'lucide-react';
import { api } from '../services/api';
import type { AuthorProfile } from '../types/author';
import type { Book } from '../types/book';
import type { AuthorTicket } from '../types/ticket';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { CurrencyFormatter } from '../components/common/CurrencyFormatter';
import { StatusBadge } from '../components/common/StatusBadge';

export const DashboardPage: React.FC = () => {
  const [profile, setProfile] = useState<AuthorProfile | null>(null);
  const [books, setBooks] = useState<Book[]>([]);
  const [tickets, setTickets] = useState<AuthorTicket[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      setLoading(true);
      setError(null);
      try {
        const [profileData, booksData, ticketsData] = await Promise.all([
          api.author.getProfile(),
          api.author.getBooks(),
          api.author.getTickets(),
        ]);
        setProfile(profileData);
        setBooks(booksData);
        setTickets(ticketsData);
      } catch (err: any) {
        setError(err.message || 'Failed to load dashboard metrics.');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) {
    return <LoadingSpinner size="lg" message="Loading author overview..." />;
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="bg-rose-50 border border-rose-200 rounded-xl p-6 flex items-start gap-4">
          <AlertCircle className="w-6 h-6 text-rose-600 flex-shrink-0" />
          <div>
            <h3 className="text-base font-semibold text-rose-900">Failed to load author portal data</h3>
            <p className="text-sm text-rose-700 mt-1">{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="mt-4 px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white rounded-lg text-xs font-semibold"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Calculate book status metrics from real data
  const publishedCount = books.filter((b) => b.status.toLowerCase().includes('live') || b.status.toLowerCase().includes('published')).length;
  const productionCount = books.length - publishedCount;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Welcome & Overview Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 pb-6 border-b border-cream-300">
        <div>
          <h1 className="text-2xl sm:text-3xl font-serif font-bold text-brand-950">
            Welcome back, {profile?.name}
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            Author ID: <span className="font-mono font-semibold text-brand-700">{profile?.author_id}</span> • Member since {profile?.joined_date} • {profile?.city}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            to="/tickets/new"
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg bg-brand-700 hover:bg-brand-800 text-white text-sm font-medium shadow-soft transition"
          >
            <PlusCircle className="w-4 h-4" />
            <span>Submit a Support Query</span>
          </Link>
        </div>
      </div>

      {/* Primary Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Books */}
        <div className="bg-white p-5 rounded-xl border border-cream-300 shadow-soft">
          <div className="flex items-center justify-between text-gray-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Catalog Size</span>
            <BookOpen className="w-4 h-4 text-brand-600" />
          </div>
          <div className="text-2xl font-bold text-brand-950 font-serif">
            {profile?.total_books ?? 0} <span className="text-sm font-normal text-gray-500">Titles</span>
          </div>
          <div className="mt-2 text-xs text-gray-500 flex items-center gap-2">
            <span className="text-emerald-700 font-medium">{publishedCount} Published</span>
            <span>•</span>
            <span className="text-amber-700 font-medium">{productionCount} In Production</span>
          </div>
        </div>

        {/* Royalty Earned */}
        <div className="bg-white p-5 rounded-xl border border-cream-300 shadow-soft">
          <div className="flex items-center justify-between text-gray-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Total Royalty Earned</span>
            <Wallet className="w-4 h-4 text-brand-600" />
          </div>
          <div className="text-2xl font-bold text-brand-950">
            <CurrencyFormatter amount={profile?.total_royalties_earned} />
          </div>
          <div className="mt-2 text-xs text-gray-500">
            Across {profile?.total_copies_sold?.toLocaleString('en-IN') ?? 0} total copies sold
          </div>
        </div>

        {/* Royalty Paid */}
        <div className="bg-white p-5 rounded-xl border border-cream-300 shadow-soft">
          <div className="flex items-center justify-between text-gray-500 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Royalty Paid Out</span>
            <CheckCircle className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="text-2xl font-bold text-emerald-800">
            <CurrencyFormatter amount={profile?.total_royalties_paid} />
          </div>
          <div className="mt-2 text-xs text-gray-500">
            Direct payout via bank transfer
          </div>
        </div>

        {/* Royalty Pending */}
        <div className="bg-white p-5 rounded-xl border border-amber-300/80 bg-gradient-to-br from-white to-amber-50/30 shadow-soft">
          <div className="flex items-center justify-between text-amber-800 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Royalty Pending</span>
            <Clock className="w-4 h-4 text-amber-600" />
          </div>
          <div className="text-2xl font-bold text-amber-900">
            <CurrencyFormatter amount={profile?.total_royalties_pending} />
          </div>
          <div className="mt-2 text-xs text-amber-700 font-medium">
            Awaiting upcoming settlement cycle
          </div>
        </div>
      </div>

      {/* Two Column Layout: Catalog Preview & Recent Tickets */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Books Overview (2 Columns) */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-cream-300 shadow-soft overflow-hidden">
          <div className="px-6 py-4 border-b border-cream-200 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-brand-700" />
              <h2 className="text-base font-serif font-bold text-brand-950">Published Books</h2>
            </div>
            <Link
              to="/books"
              className="text-xs font-medium text-brand-700 hover:text-brand-800 flex items-center gap-1"
            >
              <span>View Full Catalog</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="divide-y divide-cream-100">
            {books.slice(0, 3).map((book) => (
              <div key={book.id} className="p-5 hover:bg-cream-50/50 transition flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2.5">
                    <h3 className="text-sm font-semibold text-gray-900 font-serif">{book.title}</h3>
                    <StatusBadge type="book_status" value={book.status} />
                  </div>
                  <div className="text-xs text-gray-500 flex flex-wrap gap-x-3 gap-y-1">
                    <span>ISBN: <code className="text-gray-700">{book.isbn}</code></span>
                    <span>Genre: {book.genre}</span>
                    {book.mrp && <span>MRP: ₹{book.mrp}</span>}
                  </div>
                </div>

                <div className="text-right flex-shrink-0">
                  <div className="text-xs text-gray-500">Earned / Pending</div>
                  <div className="text-sm font-semibold text-brand-900">
                    <CurrencyFormatter amount={book.total_royalty_earned} />
                    <span className="text-xs text-amber-700 ml-1.5 font-normal">
                      (<CurrencyFormatter amount={book.royalty_pending} /> pending)
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Support Inquiries (1 Column) */}
        <div className="bg-white rounded-xl border border-cream-300 shadow-soft overflow-hidden">
          <div className="px-6 py-4 border-b border-cream-200 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <LifeBuoy className="w-4 h-4 text-brand-700" />
              <h2 className="text-base font-serif font-bold text-brand-950">Recent Support Queries</h2>
            </div>
            <Link
              to="/tickets"
              className="text-xs font-medium text-brand-700 hover:text-brand-800 flex items-center gap-1"
            >
              <span>View All</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="divide-y divide-cream-100">
            {tickets.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                <p className="text-xs">No active queries found.</p>
                <Link
                  to="/tickets/new"
                  className="mt-3 inline-block text-xs font-medium text-brand-700 hover:underline"
                >
                  Create your first ticket →
                </Link>
              </div>
            ) : (
              tickets.slice(0, 4).map((ticket) => (
                <Link
                  key={ticket.id}
                  to={`/tickets/${ticket.id}`}
                  className="block p-4 hover:bg-cream-50/50 transition space-y-1.5"
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-[11px] font-mono text-gray-400 font-medium">{ticket.ticket_number}</span>
                    <StatusBadge type="ticket_status" value={ticket.status} />
                  </div>
                  <h4 className="text-sm font-medium text-gray-900 truncate">{ticket.subject}</h4>
                  <div className="text-[11px] text-gray-500 flex items-center justify-between">
                    <span>{ticket.category}</span>
                    <span>{new Date(ticket.created_at).toLocaleDateString()}</span>
                  </div>
                </Link>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
