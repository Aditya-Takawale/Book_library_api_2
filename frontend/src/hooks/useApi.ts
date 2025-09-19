import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiService from '../services/api';
import {
  Book,
  Author,
  Review,
  Loan,
  User,
  BookCreate,
  BookUpdate,
  AuthorCreate,
  ReviewCreate,
  LoanCreate,
  SearchFilters,
  DashboardStats,
} from '../types';

// Query Keys
export const queryKeys = {
  books: ['books'] as const,
  book: (id: number) => ['books', id] as const,
  bookSearch: (filters: SearchFilters) => ['books', 'search', filters] as const,
  popularBooks: ['books', 'popular'] as const,
  
  authors: ['authors'] as const,
  author: (id: number) => ['authors', id] as const,
  
  reviews: ['reviews'] as const,
  bookReviews: (bookId: number) => ['reviews', 'book', bookId] as const,
  userReviews: (userId?: number) => ['reviews', 'user', userId] as const,
  
  loans: ['loans'] as const,
  userLoans: ['loans', 'user'] as const,
  
  users: ['users'] as const,
  user: (id: number) => ['users', id] as const,
  currentUser: ['users', 'me'] as const,
  
  dashboard: ['dashboard'] as const,
};

// Book Hooks
export const useBooks = (params?: {
  skip?: number;
  limit?: number;
  search?: string;
  genre?: string;
  author?: string;
}) => {
  return useQuery({
    queryKey: [...queryKeys.books, params],
    queryFn: () => apiService.getBooks(params),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const useBook = (id: number) => {
  return useQuery({
    queryKey: queryKeys.book(id),
    queryFn: () => apiService.getBook(id),
    enabled: !!id,
  });
};

export const useSearchBooks = (filters: SearchFilters) => {
  return useQuery({
    queryKey: queryKeys.bookSearch(filters),
    queryFn: () => apiService.searchBooks(filters),
    enabled: !!(filters.query || filters.genre || filters.author),
  });
};

export const usePopularBooks = () => {
  return useQuery({
    queryKey: queryKeys.popularBooks,
    queryFn: () => apiService.getPopularBooks(),
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
};

export const useCreateBook = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (bookData: BookCreate) => apiService.createBook(bookData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.books });
    },
  });
};

export const useUpdateBook = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: BookUpdate }) =>
      apiService.updateBook(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.book(id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.books });
    },
  });
};

export const useDeleteBook = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: number) => apiService.deleteBook(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.books });
    },
  });
};

// Author Hooks
export const useAuthors = (params?: { skip?: number; limit?: number }) => {
  return useQuery({
    queryKey: [...queryKeys.authors, params],
    queryFn: () => apiService.getAuthors(params),
  });
};

export const useAuthor = (id: number) => {
  return useQuery({
    queryKey: queryKeys.author(id),
    queryFn: () => apiService.getAuthor(id),
    enabled: !!id,
  });
};

export const useCreateAuthor = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (authorData: AuthorCreate) => apiService.createAuthor(authorData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.authors });
    },
  });
};

export const useUpdateAuthor = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<AuthorCreate> }) =>
      apiService.updateAuthor(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.author(id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.authors });
    },
  });
};

export const useDeleteAuthor = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: number) => apiService.deleteAuthor(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.authors });
    },
  });
};

// Review Hooks
export const useBookReviews = (bookId: number) => {
  return useQuery({
    queryKey: queryKeys.bookReviews(bookId),
    queryFn: () => apiService.getBookReviews(bookId),
    enabled: !!bookId,
  });
};

export const useUserReviews = (userId?: number) => {
  return useQuery({
    queryKey: queryKeys.userReviews(userId),
    queryFn: () => apiService.getUserReviews(userId),
  });
};

export const useCreateReview = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (reviewData: ReviewCreate) => apiService.createReview(reviewData),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ 
        queryKey: queryKeys.bookReviews(variables.book_id) 
      });
      queryClient.invalidateQueries({ queryKey: queryKeys.userReviews() });
    },
  });
};

export const useUpdateReview = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<ReviewCreate> }) =>
      apiService.updateReview(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.reviews });
    },
  });
};

export const useDeleteReview = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: number) => apiService.deleteReview(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.reviews });
    },
  });
};

// Loan Hooks
export const useLoans = (params?: { 
  skip?: number; 
  limit?: number; 
  status?: string 
}) => {
  return useQuery({
    queryKey: [...queryKeys.loans, params],
    queryFn: () => apiService.getLoans(params),
  });
};

export const useUserLoans = () => {
  return useQuery({
    queryKey: queryKeys.userLoans,
    queryFn: () => apiService.getUserLoans(),
  });
};

export const useCreateLoan = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (loanData: LoanCreate) => apiService.createLoan(loanData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.loans });
      queryClient.invalidateQueries({ queryKey: queryKeys.userLoans });
      queryClient.invalidateQueries({ queryKey: queryKeys.books });
    },
  });
};

export const useReturnBook = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (loanId: number) => apiService.returnBook(loanId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.loans });
      queryClient.invalidateQueries({ queryKey: queryKeys.userLoans });
      queryClient.invalidateQueries({ queryKey: queryKeys.books });
    },
  });
};

export const useRenewLoan = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (loanId: number) => apiService.renewLoan(loanId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.loans });
      queryClient.invalidateQueries({ queryKey: queryKeys.userLoans });
    },
  });
};

// User Hooks
export const useUsers = (params?: { skip?: number; limit?: number }) => {
  return useQuery({
    queryKey: [...queryKeys.users, params],
    queryFn: () => apiService.getUsers(params),
  });
};

export const useCurrentUser = () => {
  return useQuery({
    queryKey: queryKeys.currentUser,
    queryFn: () => apiService.getCurrentUser(),
    retry: false,
  });
};

export const useUpdateUser = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<User> }) =>
      apiService.updateUser(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.user(id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.users });
      queryClient.invalidateQueries({ queryKey: queryKeys.currentUser });
    },
  });
};

export const useDeleteUser = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: number) => apiService.deleteUser(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.users });
    },
  });
};

// Dashboard Hooks
export const useDashboardStats = () => {
  return useQuery({
    queryKey: queryKeys.dashboard,
    queryFn: () => apiService.getDashboardStats(),
    refetchInterval: 30000, // Refetch every 30 seconds
  });
};
