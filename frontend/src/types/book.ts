export interface Book {
  id: string;
  book_id: string;
  author_id: string;
  title: string;
  isbn: string;
  genre: string;
  publication_date: string | null;
  status: string;
  mrp: number | null;
  author_royalty_per_copy: number | null;
  total_copies_sold: number;
  total_royalty_earned: number;
  royalty_paid: number;
  royalty_pending: number;
  last_royalty_payout_date: string | null;
  print_partner: string | null;
  available_on: string[];
  created_at: string;
  updated_at: string;
}

export interface BookRoyaltyItem {
  book_id: string;
  title: string;
  isbn: string;
  genre: string;
  status: string;
  mrp: number | null;
  royalty_per_copy: number | null;
  total_copies_sold: number;
  total_royalty_earned: number;
  royalty_paid: number;
  royalty_pending: number;
  last_payout_date: string | null;
}

export interface AuthorRoyaltySummary {
  author_id: string;
  total_books: number;
  total_copies_sold: number;
  total_royalty_earned: number;
  total_royalty_paid: number;
  total_royalty_pending: number;
  books: BookRoyaltyItem[];
}
