// User Types
export interface User {
  id: number;
  email: string;
  username: string;
  first_name?: string;
  last_name?: string;
  role: UserRole;
  is_active: boolean;
  email_verified?: boolean;
  created_at: string;
  current_session_id?: string;
  permissions?: string[];
}

export enum UserRole {
  ADMIN = 'Admin',
  LIBRARIAN = 'Librarian',
  MEMBER = 'Member',
  GUEST = 'Guest'
}

export enum UserStatus {
  ACTIVE = 'Active',
  SUSPENDED = 'Suspended',
  PENDING = 'Pending',
  DELETED = 'Deleted'
}

// Author Types
export interface Author {
  id: number;
  first_name: string;
  last_name: string;
  full_name?: string;
  biography?: string;
  birth_date?: string;
  death_date?: string;
  nationality?: string;
  created_at: string;
  updated_at: string;
}

export interface AuthorSummary {
  id: number;
  first_name: string;
  last_name: string;
  full_name: string;
}

// Book Types
export interface Book {
  id: number;
  title: string;
  isbn?: string;
  genre: string;
  page_count: number;
  publication_year: number;
  publisher?: string;
  language?: string;
  description?: string;
  cover_image?: string;
  total_copies: number;
  available_copies: number;
  is_available: boolean;
  authors: AuthorSummary[];
  popularity_score: number;
  average_rating?: number;
  total_reviews?: number;
  created_at: string;
  updated_at: string;
}

export interface BookCreate {
  title: string;
  author_ids: number[];
  isbn: string;
  page_count: number;
  publication_year: number;
  genre: string;
  total_copies: number;
  description?: string;
  cover_image?: string;
  publisher?: string;
  language?: string;
}

export interface BookUpdate {
  title?: string;
  author?: string;
  isbn?: string;
  published_date?: string;
  genre?: string;
  total_copies?: number;
  description?: string;
  cover_image_url?: string;
}

// Author Types
export interface Author {
  id: number;
  name: string;
  biography?: string;
  birth_date?: string;
  nationality?: string;
  books_count: number;
  created_at: string;
  updated_at: string;
}

export interface AuthorCreate {
  name: string;
  biography?: string;
  birth_date?: string;
  nationality?: string;
}

// Review Types
export interface Review {
  id: number;
  book_id: number;
  user_id: number;
  rating: number;
  comment?: string;
  created_at: string;
  updated_at: string;
  book?: Book;
  user?: User;
}

export interface ReviewCreate {
  book_id: number;
  rating: number;
  comment?: string;
}

// Loan Types
export interface Loan {
  id: number;
  user_id: number;
  book_id: number;
  loan_date: string;
  due_date: string;
  return_date?: string;
  status: LoanStatus;
  fine_amount?: number;
  created_at: string;
  updated_at: string;
  book_title?: string;
  user_email?: string;
  book?: Book;
  user?: User;
}

export enum LoanStatus {
  ACTIVE = 'Active',
  RETURNED = 'Returned',
  OVERDUE = 'Overdue',
  RESERVED = 'Reserved'
}

export interface LoanCreate {
  book_id: number;
  loan_days?: number;
}

// Authentication Types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
  first_name?: string;
  last_name?: string;
  role?: UserRole;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  session_id: string;
  user: User;
}

// API Response Types
export interface ApiResponse<T> {
  data?: T;
  message?: string;
  error?: string;
  status?: number;
}

export interface PaginatedResponse<T> {
  total: number;
  loans: T[];
}

// UI State Types
export interface AppState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  theme: 'light' | 'dark';
}

// Navigation Types
export interface NavigationItem {
  label: string;
  path: string;
  icon: string;
  roles?: UserRole[];
}

// Search and Filter Types
export interface SearchFilters {
  query?: string;
  genre?: string;
  author?: string;
  availability?: 'all' | 'available' | 'borrowed';
  rating?: number;
  sort_by?: 'title' | 'author' | 'rating' | 'popularity' | 'created_at';
  sort_order?: 'asc' | 'desc';
}

// Dashboard Types
export interface DashboardStats {
  total_books: number;
  total_users: number;
  active_loans: number;
  overdue_loans: number;
  popular_books: Book[];
  recent_activities: Activity[];
}

export interface Activity {
  id: string;
  type: 'loan' | 'return' | 'review' | 'registration';
  description: string;
  timestamp: string;
  user?: User;
  book?: Book;
}

// Form Types
export interface FormFieldProps {
  name: string;
  label: string;
  type?: string;
  required?: boolean;
  multiline?: boolean;
  rows?: number;
  options?: Array<{ value: string; label: string }>;
}

export interface ModalProps {
  open: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}

// Table Types
export interface TableColumn<T> {
  field: keyof T;
  headerName: string;
  width?: number;
  sortable?: boolean;
  filterable?: boolean;
  renderCell?: (params: any) => React.ReactNode;
}

// Error Types
export interface ApiError {
  message: string;
  code?: string;
  field?: string;
  details?: any;
}

// Theme Types
export interface ThemeConfig {
  primary: string;
  secondary: string;
  background: string;
  surface: string;
  text: string;
  border: string;
}
