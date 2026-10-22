export interface AuthorProfile {
  id: string;
  author_id: string;
  name: string;
  email: string;
  phone?: string | null;
  city?: string | null;
  joined_date: string;
  total_books: number;
  total_copies_sold: number;
  total_royalties_earned: number;
  total_royalties_paid: number;
  total_royalties_pending: number;
}
