import React, { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { 
  Send, 
  Paperclip, 
  X, 
  AlertCircle, 
  CheckCircle2, 
  HelpCircle,
  ArrowLeft 
} from 'lucide-react';
import { api, ApiError } from '../services/api';
import type { Book } from '../types/book';
import type { AttachmentMetadata, CreateTicketPayload } from '../types/ticket';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

const TICKET_CATEGORIES = [
  { value: 'GENERAL_INQUIRY', label: 'General / Account Level Inquiry' },
  { value: 'ROYALTY', label: 'Royalty & Payout Reconciliation' },
  { value: 'PRINT_QUALITY', label: 'Print Quality & Defect Report' },
  { value: 'DISTRIBUTION', label: 'Distribution & Online Retail Channels' },
  { value: 'COVER_DESIGN', label: 'Cover & Interior Design Updates' },
  { value: 'METADATA_UPDATE', label: 'Metadata & Listing Updates (Price, Blurb)' },
];

export const NewTicketPage: React.FC = () => {
  const navigate = useNavigate();

  // Form states
  const [books, setBooks] = useState<Book[]>([]);
  const [selectedBookId, setSelectedBookId] = useState<string>('');
  const [category, setCategory] = useState<string>('GENERAL_INQUIRY');
  const [subject, setSubject] = useState<string>('');
  const [description, setDescription] = useState<string>('');
  const [attachments, setAttachments] = useState<AttachmentMetadata[]>([]);

  // Validation & UI states
  const [validationErrors, setValidationErrors] = useState<{ [key: string]: string }>({});
  const [loadingBooks, setLoadingBooks] = useState<boolean>(true);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [serverError, setServerError] = useState<string | null>(null);
  const [successTicketId, setSuccessTicketId] = useState<string | null>(null);

  // Fetch author's books on mount
  useEffect(() => {
    const fetchBooks = async () => {
      try {
        const authorBooks = await api.author.getBooks();
        setBooks(authorBooks);
      } catch (err: any) {
        console.error('Failed to load books for ticket creation:', err);
      } finally {
        setLoadingBooks(false);
      }
    };

    fetchBooks();
  }, []);

  // Handle client-side file selection (metadata extraction)
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

    setAttachments((prev) => [...prev, ...newAttachments]);
    // Reset file input
    e.target.value = '';
  };

  const removeAttachment = (indexToRemove: number) => {
    setAttachments((prev) => prev.filter((_, idx) => idx !== indexToRemove));
  };

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return '';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const validate = (): boolean => {
    const errors: { [key: string]: string } = {};

    if (!subject.trim()) {
      errors.subject = 'Subject is required.';
    } else if (subject.trim().length < 3) {
      errors.subject = 'Subject must be at least 3 characters.';
    } else if (subject.trim().length > 255) {
      errors.subject = 'Subject cannot exceed 255 characters.';
    }

    if (!description.trim()) {
      errors.description = 'Description is required.';
    } else if (description.trim().length < 5) {
      errors.description = 'Description must be at least 5 characters.';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setServerError(null);

    if (!validate()) {
      return;
    }

    setIsSubmitting(true);

    try {
      const payload: CreateTicketPayload = {
        book_id: selectedBookId ? selectedBookId : null,
        category: category,
        subject: subject.trim(),
        description: description.trim(),
        attachments: attachments,
      };

      const createdTicket = await api.author.createTicket(payload);
      setSuccessTicketId(createdTicket.id);

      // Redirect after a brief moment for user confirmation
      setTimeout(() => {
        navigate(`/tickets/${createdTicket.id}`);
      }, 1200);
    } catch (err: any) {
      if (err instanceof ApiError) {
        setServerError(err.message);
      } else {
        setServerError('Failed to submit ticket. Please check your internet connection and try again.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8 space-y-6">
      {/* Navigation / Back link */}
      <div>
        <Link
          to="/tickets"
          className="inline-flex items-center gap-1.5 text-xs font-medium text-gray-500 hover:text-brand-900 transition mb-3"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to all queries</span>
        </Link>
        <h1 className="text-2xl sm:text-3xl font-serif font-bold text-brand-950">
          Submit a Support Query
        </h1>
        <p className="text-sm text-gray-600 mt-1">
          Have questions regarding your manuscript, royalties, print copies, or listing? Our editorial and publishing support team will assist you.
        </p>
      </div>

      {/* Success Banner */}
      {successTicketId && (
        <div className="bg-emerald-50 border border-emerald-300 rounded-xl p-5 flex items-start gap-4">
          <CheckCircle2 className="w-6 h-6 text-emerald-600 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="text-base font-semibold text-emerald-900">
              Query Submitted Successfully
            </h3>
            <p className="text-sm text-emerald-700 mt-1">
              Your ticket has been logged and assigned to our author support team. Redirecting to your ticket thread...
            </p>
          </div>
        </div>
      )}

      {/* Error Banner */}
      {serverError && (
        <div className="bg-rose-50 border border-rose-300 rounded-xl p-4 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-rose-600 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-rose-800">
            <span className="font-semibold block">Submission Error</span>
            {serverError}
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Ticket Form */}
        <div className="lg:col-span-2">
          <form onSubmit={handleSubmit} className="bg-white rounded-xl border border-cream-300 shadow-soft p-6 sm:p-7 space-y-6">
            {/* Book Association */}
            <div>
              <label htmlFor="book-select" className="block text-xs font-semibold uppercase tracking-wider text-gray-700 mb-1.5">
                Related Book
              </label>
              <div className="relative">
                <select
                  id="book-select"
                  value={selectedBookId}
                  onChange={(e) => setSelectedBookId(e.target.value)}
                  disabled={loadingBooks || isSubmitting}
                  className="w-full rounded-lg border border-cream-300 px-3.5 py-2.5 text-sm bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-brand-700 focus:border-transparent transition"
                >
                  <option value="">— General / Account Level (Not Book-Specific) —</option>
                  {books.map((b) => (
                    <option key={b.id} value={b.id}>
                      {b.title} ({b.isbn || 'Pending ISBN'}) • {b.status}
                    </option>
                  ))}
                </select>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Choose a specific book from your catalog if your inquiry relates to its production, sales, or royalty payouts.
              </p>
            </div>

            {/* Category Selector */}
            <div>
              <label htmlFor="category-select" className="block text-xs font-semibold uppercase tracking-wider text-gray-700 mb-1.5">
                Inquiry Category <span className="text-rose-500">*</span>
              </label>
              <select
                id="category-select"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                disabled={isSubmitting}
                className="w-full rounded-lg border border-cream-300 px-3.5 py-2.5 text-sm bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-brand-700 focus:border-transparent transition"
              >
                {TICKET_CATEGORIES.map((cat) => (
                  <option key={cat.value} value={cat.value}>
                    {cat.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Subject Field */}
            <div>
              <label htmlFor="subject-input" className="block text-xs font-semibold uppercase tracking-wider text-gray-700 mb-1.5">
                Subject <span className="text-rose-500">*</span>
              </label>
              <input
                id="subject-input"
                type="text"
                placeholder="e.g., Discrepancy in Q1 royalty report for 'The Silent Echo'"
                value={subject}
                onChange={(e) => {
                  setSubject(e.target.value);
                  if (validationErrors.subject) {
                    setValidationErrors((prev) => ({ ...prev, subject: '' }));
                  }
                }}
                disabled={isSubmitting}
                className={`w-full rounded-lg border px-3.5 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-brand-700 transition ${
                  validationErrors.subject ? 'border-rose-400 bg-rose-50/30' : 'border-cream-300 bg-white'
                }`}
              />
              {validationErrors.subject && (
                <p className="text-xs text-rose-600 mt-1 font-medium">{validationErrors.subject}</p>
              )}
            </div>

            {/* Description Field */}
            <div>
              <label htmlFor="description-input" className="block text-xs font-semibold uppercase tracking-wider text-gray-700 mb-1.5">
                Detailed Description <span className="text-rose-500">*</span>
              </label>
              <textarea
                id="description-input"
                rows={5}
                placeholder="Please describe your query in detail. Include relevant dates, transaction numbers, or specific page/chapter references if applicable..."
                value={description}
                onChange={(e) => {
                  setDescription(e.target.value);
                  if (validationErrors.description) {
                    setValidationErrors((prev) => ({ ...prev, description: '' }));
                  }
                }}
                disabled={isSubmitting}
                className={`w-full rounded-lg border px-3.5 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-brand-700 transition leading-relaxed ${
                  validationErrors.description ? 'border-rose-400 bg-rose-50/30' : 'border-cream-300 bg-white'
                }`}
              />
              {validationErrors.description && (
                <p className="text-xs text-rose-600 mt-1 font-medium">{validationErrors.description}</p>
              )}
            </div>

            {/* Attachments Section */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-700 mb-1.5">
                Supporting Attachments <span className="text-gray-400 font-normal lowercase">(optional)</span>
              </label>
              
              <div className="border border-dashed border-cream-300 rounded-lg p-4 bg-cream-50/50 hover:bg-cream-50 transition text-center">
                <input
                  type="file"
                  id="ticket-file-input"
                  multiple
                  onChange={handleFileChange}
                  disabled={isSubmitting}
                  className="hidden"
                />
                <label
                  htmlFor="ticket-file-input"
                  className="cursor-pointer inline-flex flex-col items-center justify-center"
                >
                  <Paperclip className="w-6 h-6 text-brand-600 mb-1" />
                  <span className="text-xs font-semibold text-brand-800 hover:underline">
                    Click to attach documents or screenshots
                  </span>
                  <span className="text-[11px] text-gray-500 mt-0.5">
                    PDF, DOCX, PNG, JPG (metadata recorded)
                  </span>
                </label>
              </div>

              {/* Attachment List */}
              {attachments.length > 0 && (
                <ul className="mt-3 space-y-2">
                  {attachments.map((file, idx) => (
                    <li
                      key={idx}
                      className="flex items-center justify-between px-3 py-2 bg-cream-100 rounded-md border border-cream-200 text-xs text-gray-800"
                    >
                      <div className="flex items-center gap-2 overflow-hidden">
                        <Paperclip className="w-3.5 h-3.5 text-brand-700 flex-shrink-0" />
                        <span className="font-medium truncate">{file.filename}</span>
                        {file.size && (
                          <span className="text-gray-500 flex-shrink-0 font-mono text-[11px]">
                            ({formatFileSize(file.size)})
                          </span>
                        )}
                      </div>
                      <button
                        type="button"
                        onClick={() => removeAttachment(idx)}
                        disabled={isSubmitting}
                        className="p-1 text-gray-400 hover:text-rose-600 rounded transition"
                        title="Remove attachment"
                      >
                        <X className="w-3.5 h-3.5" />
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </div>

            {/* Actions */}
            <div className="pt-3 border-t border-cream-200 flex items-center justify-between">
              <Link
                to="/tickets"
                className="text-xs font-semibold text-gray-600 hover:text-gray-900 transition"
              >
                Cancel
              </Link>
              <button
                type="submit"
                disabled={isSubmitting || !!successTicketId}
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-brand-700 hover:bg-brand-800 active:bg-brand-900 text-white text-sm font-semibold shadow-soft disabled:opacity-50 transition"
              >
                {isSubmitting ? (
                  <>
                    <LoadingSpinner size="sm" />
                    <span>Submitting...</span>
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    <span>Submit Query</span>
                  </>
                )}
              </button>
            </div>
          </form>
        </div>

        {/* Sidebar / Guidelines Card */}
        <div className="space-y-4">
          <div className="bg-brand-50/70 border border-brand-200/80 rounded-xl p-5 text-brand-950">
            <div className="flex items-center gap-2 mb-3 text-brand-800 font-semibold text-sm">
              <HelpCircle className="w-4 h-4" />
              <span>Guidelines for Quick Resolution</span>
            </div>
            <ul className="text-xs text-brand-900/90 space-y-2.5 leading-relaxed">
              <li className="flex items-start gap-2">
                <span className="font-bold text-brand-700">•</span>
                <span>
                  <strong>Specific Title:</strong> If your query pertains to a particular manuscript, select it from the dropdown to automatically route it to the respective editor.
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="font-bold text-brand-700">•</span>
                <span>
                  <strong>Royalty Inquiries:</strong> Mention the payout cycle or month and the distributor channel (e.g. Amazon, Flipkart, BookLeaf Direct).
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="font-bold text-brand-700">•</span>
                <span>
                  <strong>Print Proofs:</strong> Mention page numbers, photo captures of physical defects, and delivery order numbers.
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="font-bold text-brand-700">•</span>
                <span>
                  <strong>SLA:</strong> Author queries are typically reviewed by support within 24–48 business hours.
                </span>
              </li>
            </ul>
          </div>

          <div className="bg-white border border-cream-300 rounded-xl p-4 text-xs text-gray-600">
            <span className="font-semibold block text-brand-950 mb-1">Confidential & Secure</span>
            <p>
              Your inquiries and ticket conversation threads are encrypted and strictly isolated to your verified author account.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
