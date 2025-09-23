import React from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  CircularProgress,
  Alert,
} from '@mui/material';
import { format } from 'date-fns';
import apiService from '../../services/api';
import { Loan, LoanStatus } from '../../types';

const MyLoans: React.FC = () => {
  const { data: loans, isLoading, error } = useQuery<Loan[], Error>({
    queryKey: ['myLoans'],
    queryFn: () => apiService.getMyLoans(),
  });

  const getStatusColor = (status: LoanStatus): 'success' | 'warning' | 'error' | 'info' => {
    switch (status) {
      case LoanStatus.ACTIVE: return 'info';
      case LoanStatus.RETURNED: return 'success';
      case LoanStatus.OVERDUE: return 'error';
      default: return 'info';
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold', color: 'primary.main' }}>
        My Loans
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Here are the books you have borrowed.
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error.message || 'An unexpected error occurred.'}
        </Alert>
      )}

      <Card>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow sx={{ backgroundColor: 'primary.light' }}>
                <TableCell sx={{ fontWeight: 'bold' }}>Book Title</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Loan Date</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Due Date</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Return Date</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Status</TableCell>
                <TableCell sx={{ fontWeight: 'bold' }}>Fine</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {isLoading ? (
                <TableRow>
                  <TableCell colSpan={6} align="center" sx={{ py: 4 }}>
                    <CircularProgress />
                  </TableCell>
                </TableRow>
              ) : loans && loans.length > 0 ? (
                loans.map((loan) => (
                  <TableRow key={loan.id} hover>
                    <TableCell>{loan.book?.title || 'N/A'}</TableCell>
                    <TableCell>{format(new Date(loan.loan_date), 'PPP')}</TableCell>
                    <TableCell>{format(new Date(loan.due_date), 'PPP')}</TableCell>
                    <TableCell>{loan.return_date ? format(new Date(loan.return_date), 'PPP') : '-'}</TableCell>
                    <TableCell>
                      <Chip
                        label={loan.status}
                        color={getStatusColor(loan.status)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {loan.fine_amount ? `$${Number(loan.fine_amount).toFixed(2)}` : '$0.00'}
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={6} align="center" sx={{ py: 4 }}>
                    <Typography color="text.secondary">You have no borrowed books.</Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Card>
    </Box>
  );
};

export default MyLoans;
