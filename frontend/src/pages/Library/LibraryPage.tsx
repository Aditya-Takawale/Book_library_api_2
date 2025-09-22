import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  CardActions,
  Button,
  Grid,
  Chip,
  TextField,
  InputAdornment,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  CircularProgress,
  Alert,
  Pagination,
  Avatar,
  Divider,
  Rating,
  useTheme
} from '@mui/material';
import {
  Search as SearchIcon,
  Book as BookIcon,
  Person as PersonIcon,
  CalendarToday as CalendarIcon,
  Category as CategoryIcon
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useSnackbar } from 'notistack';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiService } from '../../services/api';
import { Book } from '../../types';

const LibraryPage: React.FC = () => {
  const theme = useTheme();
  const { enqueueSnackbar } = useSnackbar();
  const queryClient = useQueryClient();
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [searchTerm, setSearchTerm] = useState('');
  const [genre, setGenre] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [availableOnly, setAvailableOnly] = useState(false);

  const itemsPerPage = 12;

  // Mutation for borrowing books
  const borrowMutation = useMutation({
    mutationFn: (bookId: number) => apiService.borrowBook(bookId),
    onSuccess: (loan) => {
      enqueueSnackbar(`Successfully borrowed book! Due date: ${new Date(loan.due_date).toLocaleDateString()}`, { 
        variant: 'success' 
      });
      // Refresh the books list to update available copies
      fetchBooks();
      // Invalidate any loan-related queries
      queryClient.invalidateQueries({ queryKey: ['myLoans'] });
    },
    onError: (error: any) => {
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to borrow book';
      enqueueSnackbar(errorMessage, { variant: 'error' });
    },
  });

  useEffect(() => {
    fetchBooks();
  }, [currentPage, searchTerm, genre, availableOnly]);

  const fetchBooks = async () => {
    try {
      setLoading(true);
      console.log('LibraryPage: Fetching books with params:', {
        skip: (currentPage - 1) * itemsPerPage,
        limit: itemsPerPage,
        search: searchTerm || undefined,
        genre: genre || undefined,
        available_only: availableOnly
      });
      
      const response = await apiService.getBooks({
        skip: (currentPage - 1) * itemsPerPage,
        limit: itemsPerPage,
        search: searchTerm || undefined,
        genre: genre || undefined,
        available_only: availableOnly
      });

      console.log('LibraryPage: Received books:', response?.length, 'books');
      setBooks(response);
      // For now, we'll calculate pages based on results
      // In a real implementation, the API should return total count
      setTotalPages(Math.max(1, Math.ceil(response.length / itemsPerPage)));
      setError('');
    } catch (err: any) {
      console.error('LibraryPage: Error fetching books:', err);
      setError(err.message || 'Failed to fetch books');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (value: string) => {
    setSearchTerm(value);
    setCurrentPage(1);
  };

  const handleGenreChange = (value: string) => {
    setGenre(value);
    setCurrentPage(1);
  };

  const handleBorrowBook = async (bookId: number) => {
    borrowMutation.mutate(bookId);
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const cardVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.5 },
    },
  };

  if (loading && books.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography
        variant="h4"
        gutterBottom
        sx={{
          background: 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          fontWeight: 'bold',
          mb: 3,
        }}
      >
        📚 Library
      </Typography>

      {/* Search and Filters */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ 
          display: 'flex', 
          flexWrap: 'wrap', 
          gap: 2, 
          alignItems: 'center',
          flexDirection: { xs: 'column', md: 'row' }
        }}>
          <Box sx={{ flex: { xs: '1 1 100%', md: '1 1 50%' } }}>
            <TextField
              fullWidth
              placeholder="Search books by title or description..."
              value={searchTerm}
              onChange={(e) => handleSearch(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 2,
                },
              }}
            />
          </Box>
          <Box sx={{ flex: { xs: '1 1 100%', md: '1 1 25%' } }}>
            <FormControl fullWidth>
              <InputLabel>Genre</InputLabel>
              <Select
                value={genre}
                label="Genre"
                onChange={(e) => handleGenreChange(e.target.value)}
                sx={{ borderRadius: 2 }}
              >
                <MenuItem value="">All Genres</MenuItem>
                <MenuItem value="Fiction">Fiction</MenuItem>
                <MenuItem value="Non-Fiction">Non-Fiction</MenuItem>
                <MenuItem value="Science">Science</MenuItem>
                <MenuItem value="History">History</MenuItem>
                <MenuItem value="Biography">Biography</MenuItem>
                <MenuItem value="Technology">Technology</MenuItem>
              </Select>
            </FormControl>
          </Box>
          <Box sx={{ flex: { xs: '1 1 100%', md: '1 1 25%' } }}>
            <Button
              fullWidth
              variant={availableOnly ? 'contained' : 'outlined'}
              onClick={() => setAvailableOnly(!availableOnly)}
              sx={{ height: '56px', borderRadius: 2 }}
            >
              Available Only
            </Button>
          </Box>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Books Grid */}
      {books.length === 0 && !loading ? (
        <Box textAlign="center" py={8}>
          <BookIcon sx={{ fontSize: 80, color: 'text.disabled', mb: 2 }} />
          <Typography variant="h6" color="text.secondary">
            No books found
          </Typography>
          <Typography color="text.secondary">
            {searchTerm || genre
              ? 'Try adjusting your search criteria'
              : 'The library is empty. Please contact an administrator to add books.'}
          </Typography>
        </Box>
      ) : (
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          <Box sx={{
            display: 'grid',
            gridTemplateColumns: {
              xs: '1fr',
              sm: 'repeat(2, 1fr)',
              md: 'repeat(3, 1fr)',
              lg: 'repeat(4, 1fr)'
            },
            gap: 3
          }}>
            {books.map((book) => (
              <Box key={book.id}>
                <motion.div variants={cardVariants}>
                  <Card
                    sx={{
                      height: '100%',
                      display: 'flex',
                      flexDirection: 'column',
                      borderRadius: 2,
                      boxShadow: theme.shadows[2],
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        transform: 'translateY(-4px)',
                        boxShadow: theme.shadows[8],
                      },
                    }}
                  >
                    {/* Book Cover Placeholder */}
                    <Box
                      sx={{
                        height: 200,
                        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        position: 'relative',
                      }}
                    >
                      <BookIcon sx={{ fontSize: 60, color: 'white', opacity: 0.8 }} />
                      {book.available_copies !== undefined && book.available_copies <= 0 && (
                        <Chip
                          label="Not Available"
                          color="error"
                          size="small"
                          sx={{
                            position: 'absolute',
                            top: 8,
                            right: 8,
                          }}
                        />
                      )}
                    </Box>

                    <CardContent sx={{ flexGrow: 1, p: 2 }}>
                      <Typography
                        variant="h6"
                        component="h3"
                        gutterBottom
                        sx={{
                          fontWeight: 'bold',
                          lineHeight: 1.2,
                          display: '-webkit-box',
                          WebkitLineClamp: 2,
                          WebkitBoxOrient: 'vertical',
                          overflow: 'hidden',
                        }}
                      >
                        {book.title}
                      </Typography>

                      {book.authors && book.authors.length > 0 && (
                        <Box display="flex" alignItems="center" mb={1}>
                          <PersonIcon sx={{ fontSize: 16, mr: 0.5, color: 'text.secondary' }} />
                          <Typography variant="body2" color="text.secondary">
                            {book.authors.map(author => author.full_name).join(', ')}
                          </Typography>
                        </Box>
                      )}

                      {book.publication_year && (
                        <Box display="flex" alignItems="center" mb={1}>
                          <CalendarIcon sx={{ fontSize: 16, mr: 0.5, color: 'text.secondary' }} />
                          <Typography variant="body2" color="text.secondary">
                            {book.publication_year}
                          </Typography>
                        </Box>
                      )}

                      {book.genre && (
                        <Box display="flex" alignItems="center" mb={2}>
                          <CategoryIcon sx={{ fontSize: 16, mr: 0.5, color: 'text.secondary' }} />
                          <Chip
                            label={book.genre}
                            size="small"
                            variant="outlined"
                            sx={{ fontSize: '0.75rem' }}
                          />
                        </Box>
                      )}

                      {book.description && (
                        <Typography
                          variant="body2"
                          color="text.secondary"
                          sx={{
                            display: '-webkit-box',
                            WebkitLineClamp: 3,
                            WebkitBoxOrient: 'vertical',
                            overflow: 'hidden',
                            mb: 2,
                          }}
                        >
                          {book.description}
                        </Typography>
                      )}

                      {book.average_rating !== undefined && (
                        <Box display="flex" alignItems="center" gap={1}>
                          <Rating
                            value={book.average_rating}
                            readOnly
                            precision={0.1}
                            size="small"
                          />
                          <Typography variant="body2" color="text.secondary">
                            ({book.average_rating.toFixed(1)})
                          </Typography>
                        </Box>
                      )}
                    </CardContent>

                    <Divider />

                    <CardActions sx={{ p: 2, justifyContent: 'space-between' }}>
                      <Box>
                        {book.available_copies !== undefined && (
                          <Typography variant="body2" color="text.secondary">
                            {book.available_copies} available
                          </Typography>
                        )}
                      </Box>
                      <Button
                        variant="contained"
                        size="small"
                        onClick={() => handleBorrowBook(book.id)}
                        disabled={
                          (book.available_copies !== undefined && book.available_copies <= 0) ||
                          borrowMutation.isPending
                        }
                        sx={{
                          borderRadius: 2,
                          textTransform: 'none',
                        }}
                      >
                        {borrowMutation.isPending
                          ? 'Borrowing...'
                          : book.available_copies !== undefined && book.available_copies <= 0
                          ? 'Not Available'
                          : 'Borrow'}
                      </Button>
                    </CardActions>
                  </Card>
                </motion.div>
              </Box>
            ))}
          </Box>
        </motion.div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <Box display="flex" justifyContent="center" mt={4}>
          <Pagination
            count={totalPages}
            page={currentPage}
            onChange={(_, page) => setCurrentPage(page)}
            color="primary"
            size="large"
          />
        </Box>
      )}

      {loading && books.length > 0 && (
        <Box display="flex" justifyContent="center" mt={2}>
          <CircularProgress size={24} />
        </Box>
      )}
    </Box>
  );
};

export default LibraryPage;
