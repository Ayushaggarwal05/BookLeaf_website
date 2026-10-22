export interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'author' | 'admin';
  author_id?: string | null;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  role: 'author' | 'admin';
  user_id: string;
  email: string;
  name: string;
  author_id?: string | null;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}
