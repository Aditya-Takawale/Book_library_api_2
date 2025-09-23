import React, { useState } from 'react';
import { useQuery, useQueryClient, useMutation } from '@tanstack/react-query';
import {
  Box,
  Typography,
  Card,
  CardContent,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Avatar,
  Pagination,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tooltip,
  IconButton,
  Stack
} from '@mui/material';
import {
  Search as SearchIcon,
  FilterList as FilterIcon,
  Refresh as RefreshIcon,
  GetApp as DownloadIcon,
  CheckCircle as CheckIcon,
  Warning as WarningIcon,
  CalendarToday as CalendarIcon,
  Book as BookIcon,
  Person as PersonIcon,
  AssignmentReturn as ReturnIcon
} from '@mui/icons-material';
import apiService from '../../services/api';
import { Loan, LoanStatus, PaginatedResponse, User, Book } from '../../types';

// Define a more detailed Loan type for the frontend
interface LoanWithDetails extends Loan {
  user: User;
  book: Book;
}

// Simple date formatting functions to replace date-fns
const formatDate = (dateString: string): string => {
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) {
      return "Invalid date";
    }
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
  } catch {
    return dateString;
  }
};

const isOverdue = (dateString: string): boolean => {
  try {
    const date = new Date(dateString);
    return !isNaN(date.getTime()) && date < new Date();
  } catch {
    return false;
  }
};

interface LoanWithDetails extends Loan {
  user: User;
  book: Book;
}

const LoanManagement: React.FC = () => {
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [searchTerm, setSearchTerm] = useState('');
  const [returnDialogOpen, setReturnDialogOpen] = useState(false);
  const [selectedLoan, setSelectedLoan] = useState<LoanWithDetails | null>(null);

  const itemsPerPage = 10;

  const { data, isLoading, error, isFetching } = useQuery<PaginatedResponse<LoanWithDetails>, Error>({
    queryKey: ['adminLoans', page, itemsPerPage, statusFilter, searchTerm],
    queryFn: () => apiService.getLoans({ 
      skip: (page - 1) * itemsPerPage, 
      limit: itemsPerPage,
      status: statusFilter || undefined,
      search: searchTerm || undefined,
    }) as Promise<PaginatedResponse<LoanWithDetails>>,
    placeholderData: (previousData) => previousData,
  });

  const returnMutation = useMutation({
    mutationFn: (loanId: number) => apiService.returnBook(loanId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['adminLoans'] });
      setReturnDialogOpen(false);
      setSelectedLoan(null);
    },
    onError: (err: any) => {
      console.error('❌ Error returning book:', err);
      // You can use a snackbar here to show the error
    },
  });

  const handleReturnBook = () => {
    if (selectedLoan) {
      returnMutation.mutate(selectedLoan.id);
    }
  };

  const getStatusColor = (status: LoanStatus): 'success' | 'warning' | 'error' | 'info' => {
    switch (status) {
      case LoanStatus.ACTIVE: return 'info';
      case LoanStatus.RETURNED: return 'success';
      case LoanStatus.OVERDUE: return 'error';
      case LoanStatus.RENEWED: return 'warning';
      case LoanStatus.LOST: return 'error';
      case LoanStatus.DAMAGED: return 'warning';
      default: return 'info';
    }
  };

  const getStatusIcon = (status: LoanStatus) => {
    switch (status) {
      case LoanStatus.ACTIVE: return <BookIcon fontSize="small" />;
      case LoanStatus.RETURNED: return <CheckIcon fontSize="small" />;
      case LoanStatus.OVERDUE: return <WarningIcon fontSize="small" />;
      case LoanStatus.RENEWED: return <CalendarIcon fontSize="small" />;
      case LoanStatus.LOST: return <WarningIcon fontSize="small" />;
      case LoanStatus.DAMAGED: return <WarningIcon fontSize="small" />;
      default: return <BookIcon fontSize="small" />;
    }
  };

  const isOverdueDate = (loan: Loan): boolean => {
    if (loan.status === LoanStatus.RETURNED) return false;
    return isOverdue(loan.due_date);
  };

  const handleExportLoans = () => {
    // TODO: Implement CSV export functionality
    console.log('📊 Exporting loans data...');
  };

  const loans = data?.loans ?? [];
  const totalItems = data?.total ?? 0;
  const totalPages = Math.ceil(totalItems / itemsPerPage);

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold', color: 'primary.main' }}>
            📋 Loan Management
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Manage book loans, returns, and track overdue items. Total: {totalItems}
          </Typography>
        </Box>
        {(isLoading || isFetching) && <CircularProgress size={24} />}
      </Box>

      {/* Controls */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ 
            display: 'grid', 
            gridTemplateColumns: { xs: '1fr', md: '2fr 1.5fr 2.5fr' },
            gap: 2,
            alignItems: 'center'
          }}>
            <TextField
              fullWidth
              placeholder="Search by user, email, book title, or ISBN..."
              value={searchTerm}
              onChange={(e) => {
                setSearchTerm(e.target.value);
                setPage(1); // Reset to first page on search
              }}
              InputProps={{
                startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />,
              }}
            />
            <FormControl fullWidth>
              <InputLabel>Status Filter</InputLabel>
              <Select
                value={statusFilter}
                label="Status Filter"
                onChange={(e) => {
                  setStatusFilter(e.target.value);
                  setPage(1); // Reset to first page on filter change
                }}
                startAdornment={<FilterIcon sx={{ mr: 1, color: 'text.secondary' }} />}
              >
                <MenuItem value="">All Statuses</MenuItem>
                <MenuItem value={LoanStatus.ACTIVE}>Active</MenuItem>
                <MenuItem value={LoanStatus.OVERDUE}>Overdue</MenuItem>
                <MenuItem value={LoanStatus.RETURNED}>Returned</MenuItem>
                <MenuItem value={LoanStatus.RENEWED}>Renewed</MenuItem>
                <MenuItem value={LoanStatus.LOST}>Lost</MenuItem>
                <MenuItem value={LoanStatus.DAMAGED}>Damaged</MenuItem>
              </Select>
            </FormControl>
            <Stack direction="row" spacing={2}>
              <Button
                variant="outlined"
                startIcon={<RefreshIcon />}
                onClick={() => queryClient.invalidateQueries({ queryKey: ['adminLoans'] })}
                disabled={isLoading || isFetching}
              >
                Refresh
              </Button>
              <Button
                variant="outlined"
                startIcon={<DownloadIcon />}
                onClick={handleExportLoans}
              >
                Export CSV
              </Button>
            </Stack>
          </Box>
        </CardContent>
      </Card>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error.message || 'An unexpected error occurred.'}
        </Alert>
      )}

      {/* Loans Table */}
      <Card>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow sx={{ backgroundColor: 'primary.main' }}>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Loan ID</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>User</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Book</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Loan Date</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Due Date</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Return Date</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Status</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Fine</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {isLoading ? (
                <TableRow>
                  <TableCell colSpan={9} align="center" sx={{ py: 4 }}>
                    <CircularProgress />
                  </TableCell>
                </TableRow>
              ) : loans.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={9} align="center" sx={{ py: 4 }}>
                    <Typography variant="h6" color="text.secondary">
                      📚 No loans found
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {searchTerm || statusFilter 
                        ? 'Try adjusting your search or filter criteria'
                        : 'No loan records available'}
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                loans.map((loan) => {
                  const overdueStatus = isOverdueDate(loan);
                  return (
                    <TableRow 
                      key={loan.id}
                      sx={{ 
                        '&:hover': { backgroundColor: 'action.hover' },
                        backgroundColor: overdueStatus && loan.status === LoanStatus.ACTIVE 
                          ? 'error.light' 
                          : 'inherit'
                      }}
                    >
                      <TableCell>
                        <Typography variant="body2" fontWeight="bold">
                          #{loan.id}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Avatar sx={{ width: 32, height: 32 }}>
                            <PersonIcon />
                          </Avatar>
                          <Box>
                            <Typography variant="body2" fontWeight="medium">
                              {loan.user?.username || 'Unknown User'}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {loan.user?.email}
                            </Typography>
                          </Box>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Avatar sx={{ width: 32, height: 32 }}>
                            <BookIcon />
                          </Avatar>
                          <Box>
                            <Typography variant="body2" fontWeight="medium">
                              {loan.book_title || 'Unknown Book'}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {loan.book?.isbn && `ISBN: ${loan.book.isbn}`}
                            </Typography>
                          </Box>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {formatDate(loan.loan_date)}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography 
                          variant="body2"
                          color={overdueStatus && loan.status === LoanStatus.ACTIVE ? 'error' : 'inherit'}
                          fontWeight={overdueStatus && loan.status === LoanStatus.ACTIVE ? 'bold' : 'normal'}
                        >
                          {formatDate(loan.due_date)}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {loan.return_date 
                            ? formatDate(loan.return_date)
                            : '-'
                          }
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          icon={getStatusIcon(loan.status)}
                          label={loan.status.charAt(0).toUpperCase() + loan.status.slice(1)}
                          color={getStatusColor(loan.status)}
                          size="small"
                          variant="filled"
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" color={loan.fine_amount ? 'error' : 'text.secondary'}>
                          {loan.fine_amount ? `$${Number(loan.fine_amount).toFixed(2)}` : '$0.00'}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        {loan.status === LoanStatus.ACTIVE && (
                          <Tooltip title="Return Book">
                            <IconButton
                              size="small"
                              color="primary"
                              onClick={() => {
                                setSelectedLoan(loan);
                                setReturnDialogOpen(true);
                              }}
                            >
                              <ReturnIcon />
                            </IconButton>
                          </Tooltip>
                        )}
                      </TableCell>
                    </TableRow>
                  );
                })
              )}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Pagination */}
        {totalPages > 1 && (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
            <Pagination
              count={totalPages}
              page={page}
              onChange={(_, newPage) => setPage(newPage)}
              color="primary"
              showFirstButton
              showLastButton
              disabled={isFetching}
            />
          </Box>
        )}
      </Card>

      {/* Return Book Dialog */}
      <Dialog open={returnDialogOpen} onClose={() => setReturnDialogOpen(false)}>
        <DialogTitle>Return Book</DialogTitle>
        <DialogContent>
          <Typography variant="body1" gutterBottom>
            Are you sure you want to mark this book as returned?
          </Typography>
          {selectedLoan && (
            <Box sx={{ mt: 2, p: 2, backgroundColor: 'grey.100', borderRadius: 1 }}>
              <Typography variant="subtitle2" gutterBottom>
                <strong>Book:</strong> {selectedLoan.book_title || 'Unknown Book'}
              </Typography>
              <Typography variant="subtitle2" gutterBottom>
                <strong>User:</strong> {selectedLoan.user?.username} ({selectedLoan.user?.email})
              </Typography>
              <Typography variant="subtitle2" gutterBottom>
                <strong>Due Date:</strong> {formatDate(selectedLoan.due_date)}
              </Typography>
              {isOverdueDate(selectedLoan) && (
                <Typography variant="subtitle2" color="error" gutterBottom>
                  <strong>⚠️ This book is overdue!</strong>
                </Typography>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setReturnDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleReturnBook}
            variant="contained"
            disabled={returnMutation.isPending}
            startIcon={returnMutation.isPending ? <CircularProgress size={16} /> : <ReturnIcon />}
          >
            {returnMutation.isPending ? 'Processing...' : 'Return Book'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default LoanManagement;
