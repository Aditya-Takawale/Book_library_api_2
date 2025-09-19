import React, { useState, useEffect, useMemo } from 'react';
import { useLocation } from 'react-router-dom';
import {
  Box,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  CircularProgress,
  Pagination,
  Avatar
} from '@mui/material';
import {
  Edit,
  Delete,
  Add
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useSnackbar } from 'notistack';
import apiService from '../../services/api';
import { Book, BookCreate, BookUpdate } from '../../types';

const BookManagement: React.FC = () => {
  const location = useLocation();
  const [page, setPage] = useState(1);
  const [limit] = useState(10);
  const [editBook, setEditBook] = useState<Book | null>(null);
  const [createBook, setCreateBook] = useState<BookCreate | null>(null);
  const [deleteBook, setDeleteBook] = useState<Book | null>(null);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  
  const { enqueueSnackbar } = useSnackbar();
  const queryClient = useQueryClient();

  const handleCreateBook = () => {
    setCreateBook({
      title: '',
      author_ids: [],
      isbn: '',
      page_count: 100,
      publication_year: new Date().getFullYear(),
      genre: '',
      total_copies: 1,
      description: '',
      cover_image: ''
    });
    setIsCreateDialogOpen(true);
  };

  useEffect(() => {
    if (location.state?.openCreateDialog) {
      handleCreateBook();
    }
  }, [location.state]);

  // Fetch all books
  const { data: books, isLoading, error } = useQuery({
    queryKey: ['books'],
    queryFn: () => apiService.getBooks({ skip: 0, limit: 1000 }), // Fetch all books
  });

  // Calculate books for current page
  const booksList = useMemo(() => {
    if (!books) return [];
    const startIndex = (page - 1) * limit;
    const endIndex = startIndex + limit;
    return books.slice(startIndex, endIndex);
  }, [books, page, limit]);

  // Calculate total pages
  const totalPages = Math.ceil((books?.length || 0) / limit);

  // Create book mutation
  const createBookMutation = useMutation({
    mutationFn: (bookData: BookCreate) => apiService.createBook(bookData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['books'] });
      enqueueSnackbar('Book created successfully', { variant: 'success' });
      setIsCreateDialogOpen(false);
      setCreateBook(null);
    },
    onError: (error: any) => {
      enqueueSnackbar(`Failed to create book: ${error.message}`, { variant: 'error' });
    },
  });

  // Update book mutation
  const updateBookMutation = useMutation({
    mutationFn: ({ id, bookData }: { id: number; bookData: BookUpdate }) =>
      apiService.updateBook(id, bookData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['books'] });
      enqueueSnackbar('Book updated successfully', { variant: 'success' });
      setIsEditDialogOpen(false);
      setEditBook(null);
    },
    onError: (error: any) => {
      enqueueSnackbar(`Failed to update book: ${error.message}`, { variant: 'error' });
    },
  });

  // Delete book mutation
  const deleteBookMutation = useMutation({
    mutationFn: (id: number) => apiService.deleteBook(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['books'] });
      enqueueSnackbar('Book deleted successfully', { variant: 'success' });
      setIsDeleteDialogOpen(false);
      setDeleteBook(null);
    },
    onError: (error: any) => {
      enqueueSnackbar(`Failed to delete book: ${error.message}`, { variant: 'error' });
    },
  });

  const handleEditBook = (book: Book) => {
    setEditBook({ ...book });
    setIsEditDialogOpen(true);
  };

  const handleDeleteBook = (book: Book) => {
    setDeleteBook(book);
    setIsDeleteDialogOpen(true);
  };

  const handleSaveCreateBook = () => {
    if (!createBook) return;
    createBookMutation.mutate(createBook);
  };

  const handleSaveEditBook = () => {
    if (!editBook) return;
    
    const updateData: BookUpdate = {
      title: editBook.title,
      author: editBook.authors?.[0]?.full_name || '',
      isbn: editBook.isbn,
      published_date: editBook.publication_year?.toString(),
      genre: editBook.genre,
      total_copies: editBook.total_copies,
      description: editBook.description,
      cover_image_url: editBook.cover_image
    };
    
    updateBookMutation.mutate({
      id: editBook.id,
      bookData: updateData
    });
  };

  const handleConfirmDelete = () => {
    if (!deleteBook) return;
    deleteBookMutation.mutate(deleteBook.id);
  };

  const getAvailabilityColor = (isAvailable: boolean) => {
    return isAvailable ? 'success' : 'error';
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error">
        Failed to load books. Please try again later.
      </Alert>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Book Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={handleCreateBook}
          sx={{ ml: 'auto' }}
        >
          Add Book
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Cover</TableCell>
              <TableCell>Title</TableCell>
              <TableCell>Author(s)</TableCell>
              <TableCell>Genre</TableCell>
              <TableCell>ISBN</TableCell>
              <TableCell>Copies</TableCell>
              <TableCell>Available</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {booksList.map((book) => (
              <TableRow key={book.id} hover>
                <TableCell>
                  <Avatar
                    src={book.cover_image}
                    alt={book.title}
                    variant="rounded"
                    sx={{ width: 40, height: 56 }}
                  >
                    📚
                  </Avatar>
                </TableCell>
                <TableCell>
                  <Typography variant="subtitle2" noWrap sx={{ maxWidth: 200 }}>
                    {book.title}
                  </Typography>
                </TableCell>
                <TableCell>
                  {book.authors?.map(author => author.full_name).join(', ') || '-'}
                </TableCell>
                <TableCell>{book.genre}</TableCell>
                <TableCell>{book.isbn || '-'}</TableCell>
                <TableCell>
                  {book.available_copies}/{book.total_copies}
                </TableCell>
                <TableCell>
                  <Chip
                    label={book.is_available ? 'Available' : 'Not Available'}
                    color={getAvailabilityColor(book.is_available)}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Chip
                    label={`${book.total_reviews || 0} reviews`}
                    color="info"
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <IconButton
                    size="small"
                    onClick={() => handleEditBook(book)}
                    color="primary"
                  >
                    <Edit />
                  </IconButton>
                  <IconButton
                    size="small"
                    onClick={() => handleDeleteBook(book)}
                    color="error"
                  >
                    <Delete />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {totalPages > 1 && (
        <Box display="flex" justifyContent="center" mt={3}>
          <Pagination
            count={totalPages}
            page={page}
            onChange={(_, newPage) => setPage(newPage)}
            color="primary"
          />
        </Box>
      )}

      {/* Create Book Dialog */}
      <Dialog open={isCreateDialogOpen} onClose={() => setIsCreateDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Add New Book</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2, display: 'grid', gap: 2 }}>
            <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
              <TextField
                fullWidth
                label="Title"
                value={createBook?.title || ''}
                onChange={(e) => setCreateBook(prev => prev ? { ...prev, title: e.target.value } : null)}
              />
              <TextField
                fullWidth
                label="Author IDs (comma-separated)"
                value={createBook?.author_ids?.join(', ') || ''}
                onChange={(e) => {
                  const ids = e.target.value.split(',').map(id => parseInt(id.trim())).filter(id => !isNaN(id));
                  setCreateBook(prev => prev ? { ...prev, author_ids: ids } : null);
                }}
                helperText="Enter author IDs separated by commas (e.g., 1, 2, 3)"
              />
            </Box>
            <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 2 }}>
              <TextField
                fullWidth
                label="ISBN"
                value={createBook?.isbn || ''}
                onChange={(e) => setCreateBook(prev => prev ? { ...prev, isbn: e.target.value } : null)}
              />
              <TextField
                fullWidth
                label="Publication Year"
                type="number"
                value={createBook?.publication_year || new Date().getFullYear()}
                onChange={(e) => setCreateBook(prev => prev ? { ...prev, publication_year: parseInt(e.target.value) } : null)}
              />
              <TextField
                fullWidth
                label="Page Count"
                type="number"
                value={createBook?.page_count || 100}
                onChange={(e) => setCreateBook(prev => prev ? { ...prev, page_count: parseInt(e.target.value) } : null)}
              />
            </Box>
            <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
              <TextField
                fullWidth
                label="Genre"
                value={createBook?.genre || ''}
                onChange={(e) => setCreateBook(prev => prev ? { ...prev, genre: e.target.value } : null)}
              />
              <TextField
                fullWidth
                label="Total Copies"
                type="number"
                value={createBook?.total_copies || 1}
                onChange={(e) => setCreateBook(prev => prev ? { ...prev, total_copies: parseInt(e.target.value) } : null)}
              />
            </Box>
            <TextField
              fullWidth
              label="Description"
              multiline
              rows={3}
              value={createBook?.description || ''}
              onChange={(e) => setCreateBook(prev => prev ? { ...prev, description: e.target.value } : null)}
            />
            <TextField
              fullWidth
              label="Cover Image URL"
              value={createBook?.cover_image || ''}
              onChange={(e) => setCreateBook(prev => prev ? { ...prev, cover_image: e.target.value } : null)}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsCreateDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleSaveCreateBook}
            variant="contained"
            disabled={createBookMutation.isPending}
          >
            {createBookMutation.isPending ? 'Creating...' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit Book Dialog */}
      <Dialog open={isEditDialogOpen} onClose={() => setIsEditDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Edit Book</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2, display: 'grid', gap: 2 }}>
            <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
              <TextField
                fullWidth
                label="Title"
                value={editBook?.title || ''}
                onChange={(e) => setEditBook(prev => prev ? { ...prev, title: e.target.value } : null)}
              />
              <TextField
                fullWidth
                label="Author"
                value={editBook?.authors?.[0]?.full_name || ''}
                onChange={(e) => {
                  const newAuthors = [...(editBook?.authors || [])];
                  if (newAuthors.length > 0) {
                    newAuthors[0] = { ...newAuthors[0], full_name: e.target.value };
                  }
                  setEditBook(prev => prev ? { ...prev, authors: newAuthors } : null);
                }}
              />
            </Box>
            <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
              <TextField
                fullWidth
                label="ISBN"
                value={editBook?.isbn || ''}
                onChange={(e) => setEditBook(prev => prev ? { ...prev, isbn: e.target.value } : null)}
              />
              <TextField
                fullWidth
                label="Publication Year"
                value={editBook?.publication_year || ''}
                onChange={(e) => setEditBook(prev => prev ? { ...prev, publication_year: parseInt(e.target.value) } : null)}
              />
            </Box>
            <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
              <TextField
                fullWidth
                label="Genre"
                value={editBook?.genre || ''}
                onChange={(e) => setEditBook(prev => prev ? { ...prev, genre: e.target.value } : null)}
              />
              <TextField
                fullWidth
                label="Total Copies"
                type="number"
                value={editBook?.total_copies || 1}
                onChange={(e) => setEditBook(prev => prev ? { ...prev, total_copies: parseInt(e.target.value) } : null)}
              />
            </Box>
            <TextField
              fullWidth
              label="Description"
              multiline
              rows={3}
              value={editBook?.description || ''}
              onChange={(e) => setEditBook(prev => prev ? { ...prev, description: e.target.value } : null)}
            />
            <TextField
              fullWidth
              label="Cover Image URL"
              value={editBook?.cover_image || ''}
              onChange={(e) => setEditBook(prev => prev ? { ...prev, cover_image: e.target.value } : null)}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsEditDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleSaveEditBook}
            variant="contained"
            disabled={updateBookMutation.isPending}
          >
            {updateBookMutation.isPending ? 'Saving...' : 'Save'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Book Dialog */}
      <Dialog open={isDeleteDialogOpen} onClose={() => setIsDeleteDialogOpen(false)}>
        <DialogTitle>Delete Book</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete "{deleteBook?.title}"? This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsDeleteDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleConfirmDelete}
            color="error"
            variant="contained"
            disabled={deleteBookMutation.isPending}
          >
            {deleteBookMutation.isPending ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default BookManagement;
