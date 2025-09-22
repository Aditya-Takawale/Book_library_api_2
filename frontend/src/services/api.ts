import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import {
  User,
  Book,
  Author,
  Review,
  Loan,
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  BookCreate,
  BookUpdate,
  AuthorCreate,
  ReviewCreate,
  LoanCreate,
  PaginatedResponse,
  DashboardStats,
  SearchFilters
} from '../types';

class ApiService {
  private api: AxiosInstance;
  private baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8001';

  constructor() {
    this.api = axios.create({
      baseURL: this.baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.api.interceptors.request.use((config) => {
      const token = this.getToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Response interceptor to handle token refresh
    this.api.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        if (error.response?.status === 401) {
          this.clearTokens();
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Token management
  private getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  private setToken(token: string): void {
    localStorage.setItem('access_token', token);
  }

  private setRefreshToken(token: string): void {
    localStorage.setItem('refresh_token', token);
  }

  private clearTokens(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  }

  // Authentication methods
  async login(credentials: LoginRequest): Promise<TokenResponse> {
    try {
      console.log('ApiService: Attempting login request to:', this.baseURL + '/auth/login');
      console.log('ApiService: Login credentials:', { email: credentials.email, password: '[MASKED]' });
      
      // Use regular login (non-encrypted) for now to fix login issues
      const response: AxiosResponse<TokenResponse> = await this.api.post(
        '/auth/login',
        {
          email: credentials.email,
          password: credentials.password
        }
      );

      console.log('ApiService: Received response status:', response.status);
      console.log('ApiService: Received response data:', response.data);

      const { access_token, refresh_token, user } = response.data;
      
      console.log('ApiService: Extracted tokens and user:', { 
        access_token: access_token ? '[TOKEN]' : 'MISSING',
        refresh_token: refresh_token ? '[TOKEN]' : 'MISSING',
        user: user ? user : 'MISSING'
      });
      
      this.setToken(access_token);
      this.setRefreshToken(refresh_token);
      localStorage.setItem('user', JSON.stringify(user));

      console.log('ApiService: Login successful, returning response data');
      return response.data;
    } catch (error) {
      console.error('ApiService: Login failed with error:', error);
      throw error;
    }
  }

  async register(userData: RegisterRequest): Promise<User> {
    const response: AxiosResponse<User> = await this.api.post('/auth/register', userData);
    return response.data;
  }

  async logout(): Promise<void> {
    try {
      await this.api.post('/auth/logout');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      this.clearTokens();
    }
  }

  async getCurrentUser(): Promise<User> {
    const response: AxiosResponse<User> = await this.api.get('/auth/me');
    return response.data;
  }

  // Book methods
  async getBooks(params?: {
    skip?: number;
    limit?: number;
    search?: string;
    genre?: string;
    author?: string;
    available_only?: boolean;
  }): Promise<Book[]> {
    console.log('📚 API getBooks called with params:', params);
    console.log('🔗 Making request to:', `${this.baseURL}/v2/books/`);
    console.log('🔑 Auth token:', this.getToken() ? 'Present' : 'Missing');
    
    try {
      const response: AxiosResponse<Book[]> = await this.api.get('/v2/books/', {
        params,
      });
      console.log('✅ API getBooks response length:', response.data?.length);
      console.log('📊 Response status:', response.status);
      return response.data;
    } catch (error: any) {
      console.error('❌ API getBooks error:', error);
      console.error('❌ Error response:', error.response);
      throw error;
    }
  }

  async getBook(id: number): Promise<Book> {
    const response: AxiosResponse<Book> = await this.api.get(`/v2/books/${id}`);
    return response.data;
  }

  async createBook(bookData: BookCreate): Promise<Book> {
    const response: AxiosResponse<Book> = await this.api.post('/v2/books/', bookData);
    return response.data;
  }

  async updateBook(id: number, bookData: BookUpdate): Promise<Book> {
    const response: AxiosResponse<Book> = await this.api.put(`/v2/books/${id}/`, bookData);
    return response.data;
  }

  async deleteBook(id: number): Promise<void> {
    await this.api.delete(`/v2/books/${id}/`);
  }

  async searchBooks(filters: SearchFilters): Promise<Book[]> {
    const response: AxiosResponse<Book[]> = await this.api.get('/books/search', {
      params: filters,
    });
    return response.data;
  }

  async getPopularBooks(): Promise<Book[]> {
    const response: AxiosResponse<Book[]> = await this.api.get('/books/popular');
    return response.data;
  }

  // Author methods
  async getAuthors(params?: { skip?: number; limit?: number }): Promise<PaginatedResponse<Author>> {
    const response: AxiosResponse<PaginatedResponse<Author>> = await this.api.get('/authors', {
      params,
    });
    return response.data;
  }

  async getAuthor(id: number): Promise<Author> {
    const response: AxiosResponse<Author> = await this.api.get(`/authors/${id}`);
    return response.data;
  }

  async createAuthor(authorData: AuthorCreate): Promise<Author> {
    const response: AxiosResponse<Author> = await this.api.post('/authors', authorData);
    return response.data;
  }

  async updateAuthor(id: number, authorData: Partial<AuthorCreate>): Promise<Author> {
    const response: AxiosResponse<Author> = await this.api.put(`/authors/${id}`, authorData);
    return response.data;
  }

  async deleteAuthor(id: number): Promise<void> {
    await this.api.delete(`/authors/${id}`);
  }

  // Review methods
  async getBookReviews(bookId: number): Promise<Review[]> {
    const response: AxiosResponse<Review[]> = await this.api.get(`/reviews/book/${bookId}`);
    return response.data;
  }

  async getUserReviews(userId?: number): Promise<Review[]> {
    const endpoint = userId ? `/reviews/user/${userId}` : '/reviews/my';
    const response: AxiosResponse<Review[]> = await this.api.get(endpoint);
    return response.data;
  }

  async createReview(reviewData: ReviewCreate): Promise<Review> {
    const response: AxiosResponse<Review> = await this.api.post('/reviews', reviewData);
    return response.data;
  }

  async updateReview(id: number, reviewData: Partial<ReviewCreate>): Promise<Review> {
    const response: AxiosResponse<Review> = await this.api.put(`/reviews/${id}`, reviewData);
    return response.data;
  }

  async deleteReview(id: number): Promise<void> {
    await this.api.delete(`/reviews/${id}`);
  }

  // Loan methods
  async getLoans(params?: { 
    skip?: number; 
    limit?: number; 
    status?: string;
    search?: string;
  }): Promise<PaginatedResponse<Loan>> {
    const response: AxiosResponse<PaginatedResponse<Loan>> = await this.api.get('/loans', {
      params,
    });
    return response.data;
  }

  async getUserLoans(): Promise<Loan[]> {
    const response: AxiosResponse<Loan[]> = await this.api.get('/loans/my');
    return response.data;
  }

  async createLoan(loanData: LoanCreate): Promise<Loan> {
    const response: AxiosResponse<Loan> = await this.api.post('/loans', loanData);
    return response.data;
  }

  async returnBook(loanId: number): Promise<Loan> {
    const response: AxiosResponse<Loan> = await this.api.put(`/loans/${loanId}/member-return`);
    return response.data;
  }

  async renewLoan(loanId: number): Promise<Loan> {
    const response: AxiosResponse<Loan> = await this.api.post(`/loans/${loanId}/renew`);
    return response.data;
  }

  // User management methods (Admin only)
  async getUsers(params?: { skip?: number; limit?: number }): Promise<User[]> {
    console.log('👥 API getUsers called with params:', params);
    console.log('🔗 Making request to:', `${this.baseURL}/auth/users`);
    console.log('🔑 Auth token:', this.getToken() ? 'Present' : 'Missing');
    
    try {
      const response: AxiosResponse<User[]> = await this.api.get('/auth/users', {
        params,
      });
      console.log('✅ API getUsers response length:', response.data?.length);
      console.log('📊 Response status:', response.status);
      return response.data;
    } catch (error: any) {
      console.error('❌ API getUsers error:', error);
      console.error('❌ Error response:', error.response);
      throw error;
    }
  }

  async createUser(userData: RegisterRequest): Promise<User> {
    const response: AxiosResponse<User> = await this.api.post('/users', userData);
    return response.data;
  }

  async updateUser(id: number, userData: Partial<User>): Promise<User> {
    const response: AxiosResponse<User> = await this.api.put(`/users/${id}`, userData);
    return response.data;
  }

  async deleteUser(id: number): Promise<void> {
    await this.api.delete(`/users/${id}`);
  }

  // Dashboard methods
  async getDashboardStats(): Promise<DashboardStats> {
    const response = await this.api.get<DashboardStats>('/users/stats');
    return response.data;
  }

  async getMyLoans(): Promise<Loan[]> {
    const response = await this.api.get<Loan[]>('/loans/user/me');
    return response.data;
  }

  async borrowBook(bookId: number): Promise<Loan> {
    const response = await this.api.post<Loan>('/borrow', { book_id: bookId });
    return response.data;
  }

  async getLoan(id: number): Promise<Loan> {
    const response = await this.api.get<Loan>(`/loans/${id}`);
    return response.data;
  }

  async updateLoan(id: number, loanData: Partial<LoanCreate>): Promise<Loan> {
    const response = await this.api.put<Loan>(`/loans/${id}`, loanData);
    return response.data;
  }

  async deleteLoan(id: number): Promise<void> {
    await this.api.delete(`/loans/${id}`);
  }

  // Health check
  async healthCheck(): Promise<{ status: string }> {
    const response: AxiosResponse<{ status: string }> = await this.api.get('/health');
    return response.data;
  }
}

// Create singleton instance
export const apiService = new ApiService();
export default apiService;
