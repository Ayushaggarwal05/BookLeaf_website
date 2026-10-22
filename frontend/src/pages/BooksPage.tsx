import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { BookOpen, Search, ArrowUpRight, Globe, Printer, Calendar, AlertCircle, PlusCircle } from 'lucide-react';
import { api } from '../services/api';
import type { Book } from '../types/book';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { CurrencyFormatter } from '../components/common/CurrencyFormatter';
import { StatusBadge } from '../components/common/StatusBadge';

export const BooksPage: React.FC = () => {
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [selectedBook, setSelectedBook] = useState<Book | null>(null);

  useEffect(() => {
    const fetchBooks = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await api.author.getBooks();
        setBooks(data);
      } catch (err: any) {
        setError(err.message || 'Failed to fetch your books catalog.');
      } finally {
        setLoading(false);
      }
    };

    fetchBooks();
  }, []);

  const filteredBooks = books.filter((b) => {
    const term = searchTerm.toLowerCase();
    return (
      b.title.toLowerCase().includes(term) ||
      b.isbn.toLowerCase().includes(term) ||
      b.genre.toLowerCase().includes(term) ||
      b.status.toLowerCase().includes(term)
    );
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-serif font-bold text-brand-950">My Books</h1>
          <p className="text-sm text-gray-600 mt-1">
            Track published editions, print partner distribution, and sales performance.
          </p>
        </div>
        <Link
          to="/tickets/new"
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg bg-brand-700 hover:bg-brand-800 text-white text-sm font-medium transition self-start sm:self-auto"
        >
          <PlusCircle className="w-4 h-4" />
          <span>Ask About a Title</span>
        </Link>
      </div>

      {/* Filter / Search Bar */}
      <div className="bg-white p-4 rounded-xl border border-cream-300 shadow-soft flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="relative w-full sm:w-80">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
            <Search className="w-4 h-4" />
          </div>
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search by title, ISBN, or genre..."
            className="w-full pl-9 pr-3 py-2 text-xs bg-cream-50/50 border border-cream-300 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-brand-600"
          />
        </div>
        <div className="text-xs text-gray-500 self-end sm:self-auto">
          Showing {filteredBooks.length} of {books.length} titles
        </div>
      </div>

      {/* Loading & Error States */}
      {loading && <LoadingSpinner size="lg" message="Loading your catalog..." />}

      {error && (
        <div className="bg-rose-50 border border-rose-200 rounded-xl p-6 text-sm text-rose-800 flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-rose-600 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && filteredBooks.length === 0 && (
        <div className="bg-white border border-cream-300 rounded-xl p-12 text-center text-gray-500">
          <BookOpen className="w-10 h-10 text-gray-300 mx-auto mb-3" />
          <h3 className="text-base font-serif font-semibold text-gray-900">No books found</h3>
          <p className="text-xs text-gray-500 mt-1 max-w-sm mx-auto">
            {searchTerm ? `No books matched "${searchTerm}". Try another search term.` : 'No books are currently linked to your author profile.'}
          </p>
        </div>
      )}

      {/* Desktop Table View */}
      {!loading && !error && filteredBooks.length > 0 && (
        <div className="bg-white rounded-xl border border-cream-300 shadow-soft overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-cream-200 text-left text-xs">
              <thead className="bg-cream-100/70 text-gray-600 font-semibold uppercase tracking-wider text-[11px]">
                <tr>
                  <th className="py-3.5 px-4">Title & Details</th>
                  <th className="py-3.5 px-3">Status</th>
                  <th className="py-3.5 px-3">Publication Date</th>
                  <th className="py-3.5 px-3 text-right">MRP</th>
                  <th className="py-3.5 px-3 text-right">Copies Sold</th>
                  <th className="py-3.5 px-3 text-right">Royalty Earned</th>
                  <th className="py-3.5 px-3 text-right">Paid Out</th>
                  <th className="py-3.5 px-4 text-right">Pending Payout</th>
                  <th className="py-3.5 px-3 text-center">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-cream-100">
                {filteredBooks.map((book) => (
                  <tr key={book.id} className="hover:bg-cream-50/60 transition">
                    <td className="py-3.5 px-4">
                      <div className="font-semibold text-gray-900 font-serif text-sm">{book.title}</div>
                      <div className="text-[11px] text-gray-500 flex items-center gap-2 mt-0.5">
                        <span className="font-mono text-gray-600">ISBN: {book.isbn}</span>
                        <span>•</span>
                        <span>{book.genre}</span>
                      </div>
                    </td>
                    <td className="py-3.5 px-3">
                      <StatusBadge type="book_status" value={book.status} />
                    </td>
                    <td className="py-3.5 px-3 text-gray-600">
                      {book.publication_date ? new Date(book.publication_date).toLocaleDateString() : '—'}
                    </td>
                    <td className="py-3.5 px-3 text-right font-medium text-gray-700">
                      {book.mrp ? `₹${book.mrp}` : '—'}
                    </td>
                    <td className="py-3.5 px-3 text-right font-semibold text-gray-900 font-mono">
                      {book.total_copies_sold.toLocaleString('en-IN')}
                    </td>
                    <td className="py-3.5 px-3 text-right font-medium text-brand-900 font-mono">
                      <CurrencyFormatter amount={book.total_royalty_earned} />
                    </td>
                    <td className="py-3.5 px-3 text-right text-emerald-700 font-mono">
                      <CurrencyFormatter amount={book.royalty_paid} />
                    </td>
                    <td className="py-3.5 px-4 text-right font-semibold font-mono text-amber-800">
                      <CurrencyFormatter amount={book.royalty_pending} />
                    </td>
                    <td className="py-3.5 px-3 text-center">
                      <button
                        onClick={() => setSelectedBook(book)}
                        className="px-2.5 py-1 text-xs text-brand-700 hover:text-brand-900 bg-brand-50 hover:bg-brand-100 rounded-md font-medium transition"
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Book Detail Modal / Drawer */}
      {selectedBook && (
        <div className="fixed inset-0 z-50 overflow-y-auto bg-black/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full border border-cream-300 shadow-xl overflow-hidden animate-in fade-in zoom-in-95 duration-150">
            <div className="p-6 border-b border-cream-200 flex items-start justify-between">
              <div>
                <span className="text-xs font-mono font-semibold text-brand-700 block">{selectedBook.book_id}</span>
                <h3 className="text-xl font-serif font-bold text-gray-900 mt-1">{selectedBook.title}</h3>
                <div className="mt-1 flex items-center gap-2">
                  <StatusBadge type="book_status" value={selectedBook.status} />
                  <span className="text-xs text-gray-500">{selectedBook.genre}</span>
                </div>
              </div>
              <button
                onClick={() => setSelectedBook(null)}
                className="text-gray-400 hover:text-gray-600 p-1 text-lg leading-none"
              >
                ✕
              </button>
            </div>

            <div className="p-6 space-y-5 text-xs text-gray-600">
              {/* Financial Metrics */}
              <div className="grid grid-cols-2 gap-3 bg-cream-50 p-4 rounded-xl border border-cream-200">
                <div>
                  <span className="text-gray-500 block">Retail MRP:</span>
                  <span className="font-semibold text-sm text-gray-900 font-mono">
                    {selectedBook.mrp ? `₹${selectedBook.mrp}` : 'Not Set'}
                  </span>
                </div>
                <div>
                  <span className="text-gray-500 block">Author Royalty Rate:</span>
                  <span className="font-semibold text-sm text-brand-800 font-mono">
                    {selectedBook.author_royalty_per_copy ? `₹${selectedBook.author_royalty_per_copy} / copy` : 'Not Set'}
                  </span>
                </div>
                <div>
                  <span className="text-gray-500 block">Cumulative Royalty:</span>
                  <span className="font-bold text-sm text-brand-950 font-mono">
                    <CurrencyFormatter amount={selectedBook.total_royalty_earned} />
                  </span>
                </div>
                <div>
                  <span className="text-gray-500 block">Outstanding Balance:</span>
                  <span className="font-bold text-sm text-amber-800 font-mono">
                    <CurrencyFormatter amount={selectedBook.royalty_pending} />
                  </span>
                </div>
              </div>

              {/* Manufacturing & Distribution */}
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <Printer className="w-4 h-4 text-brand-700" />
                  <span>
                    Print Partner: <strong className="text-gray-800">{selectedBook.print_partner || 'In-House'}</strong>
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-brand-700" />
                  <span>
                    Last Settlement Payout:{' '}
                    <strong className="text-gray-800">
                      {selectedBook.last_royalty_payout_date ? new Date(selectedBook.last_royalty_payout_date).toLocaleDateString() : 'Never'}
                    </strong>
                  </span>
                </div>
                <div>
                  <span className="font-medium text-gray-700 block mb-1.5 flex items-center gap-1.5">
                    <Globe className="w-4 h-4 text-brand-700" /> Available Channels:
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {selectedBook.available_on && selectedBook.available_on.length > 0 ? (
                      selectedBook.available_on.map((channel, i) => (
                        <span key={i} className="px-2 py-0.5 rounded bg-cream-100 border border-cream-300 text-[11px] text-gray-700">
                          {channel}
                        </span>
                      ))
                    ) : (
                      <span className="text-gray-400 italic">None currently active</span>
                    )}
                  </div>
                </div>
              </div>
            </div>

            <div className="p-4 bg-cream-50 border-t border-cream-200 flex justify-between items-center">
              <Link
                to={`/tickets/new?book_id=${selectedBook.id}`}
                className="inline-flex items-center gap-1.5 text-xs text-brand-700 font-semibold hover:text-brand-900"
              >
                <span>Submit Query on this Title</span>
                <ArrowUpRight className="w-3.5 h-3.5" />
              </Link>
              <button
                onClick={() => setSelectedBook(null)}
                className="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 text-xs font-medium rounded-lg"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
