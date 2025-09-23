import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Chip,
  CircularProgress,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Avatar,
  Divider,
  LinearProgress,
  Tabs,
  Tab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  useTheme
} from '@mui/material';
import {
  Book as BookIcon,
  Schedule as ScheduleIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Autorenew as RenewIcon,
  AccessTime as AccessTimeIcon,
  KeyboardReturn as ReturnIcon
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { apiService } from '../../services/api';
import { Loan, LoanStatus } from '../../types';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`loans-tabpanel-${index}`}
      aria-labelledby={`loans-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

const MyLoansPage: React.FC = () => {
  const theme = useTheme();
  const [loans, setLoans] = useState<Loan[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [tabValue, setTabValue] = useState(0);
  const [renewDialog, setRenewDialog] = useState<{ open: boolean; loan: Loan | null }>({
    open: false,
    loan: null
  });

  useEffect(() => {
    fetchLoans();
  }, []);

  const fetchLoans = async () => {
    try {
      setLoading(true);
      const response = await apiService.getUserLoans();
      setLoans(response);
      setError('');
    } catch (err: any) {
      setError(err.message || 'Failed to fetch loans');
    } finally {
      setLoading(false);
    }
  };

  const handleRenewLoan = async (loanId: number, newDueDate: string) => {
    try {
      await apiService.renewLoan(loanId);
      setRenewDialog({ open: false, loan: null });
      await fetchLoans(); // Refresh loans
      setError(''); // Clear any previous errors
    } catch (err: any) {
      setError(err.message || 'Failed to renew loan');
    }
  };

  const handleReturnBook = async (loanId: number) => {
    try {
      setError(''); // Clear any previous errors
      await apiService.returnBook(loanId);
      await fetchLoans(); // Refresh loans to get updated data
      
      // Show success message
      console.log(`Book returned successfully. Loan ID: ${loanId}`);
    } catch (err: any) {
      console.error('Return book error:', err);
      
      // If the book is already returned, just refresh the loans to update the UI
      if (err.message?.includes('Book already returned')) {
        await fetchLoans();
        setError(''); // Don't show error for already returned books
      } else {
        setError(err.message || 'Failed to return book');
      }
    }
  };

  const isOverdue = (loan: Loan): boolean => {
    if (loan.status === LoanStatus.RETURNED) return false;
    return loan.status === LoanStatus.OVERDUE || new Date(loan.due_date) < new Date();
  };

  const getDaysUntilDue = (loan: Loan): number => {
    const today = new Date();
    const dueDate = new Date(loan.due_date);
    const diffTime = dueDate.getTime() - today.getTime();
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  };

  const getStatusColor = (loan: Loan) => {
    if (loan.status === LoanStatus.RETURNED) return 'success';
    if (isOverdue(loan)) return 'error';
    const daysUntilDue = getDaysUntilDue(loan);
    if (daysUntilDue <= 3) return 'warning';
    return 'info';
  };

  const getStatusText = (loan: Loan) => {
    if (loan.status === LoanStatus.RETURNED) return 'Returned';
    if (isOverdue(loan)) return 'Overdue';
    const daysUntilDue = getDaysUntilDue(loan);
    if (daysUntilDue <= 0) return 'Due Today';
    if (daysUntilDue <= 3) return `Due in ${daysUntilDue} days`;
    return `Due in ${daysUntilDue} days`;
  };

  const activeLoans = loans.filter(loan => loan.status !== LoanStatus.RETURNED);
  const returnedLoans = loans.filter(loan => loan.status === LoanStatus.RETURNED);
  const overdueLoans = loans.filter(loan => loan.status !== LoanStatus.RETURNED && isOverdue(loan));

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

  if (loading) {
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
        📖 My Loans
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Loan Statistics */}
      <Box sx={{ 
        display: 'grid', 
        gridTemplateColumns: { 
          xs: '1fr', 
          sm: '1fr 1fr', 
          md: '1fr 1fr 1fr 1fr' 
        }, 
        gap: 3, 
        mb: 4 
      }}>
        <Box>
          <Card sx={{ textAlign: 'center', p: 2 }}>
            <BookIcon sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
            <Typography variant="h4" fontWeight="bold">
              {activeLoans.length}
            </Typography>
            <Typography color="text.secondary">Active Loans</Typography>
          </Card>
        </Box>
        <Box>
          <Card sx={{ textAlign: 'center', p: 2 }}>
            <WarningIcon sx={{ fontSize: 40, color: 'warning.main', mb: 1 }} />
            <Typography variant="h4" fontWeight="bold">
              {overdueLoans.length}
            </Typography>
            <Typography color="text.secondary">Overdue</Typography>
          </Card>
        </Box>
        <Box>
          <Card sx={{ textAlign: 'center', p: 2 }}>
            <CheckCircleIcon sx={{ fontSize: 40, color: 'success.main', mb: 1 }} />
            <Typography variant="h4" fontWeight="bold">
              {returnedLoans.length}
            </Typography>
            <Typography color="text.secondary">Returned</Typography>
          </Card>
        </Box>
        <Box>
          <Card sx={{ textAlign: 'center', p: 2 }}>
            <AccessTimeIcon sx={{ fontSize: 40, color: 'info.main', mb: 1 }} />
            <Typography variant="h4" fontWeight="bold">
              {loans.length}
            </Typography>
            <Typography color="text.secondary">Total Loans</Typography>
          </Card>
        </Box>
      </Box>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs
          value={tabValue}
          onChange={(_, newValue) => setTabValue(newValue)}
          aria-label="loan tabs"
        >
          <Tab label={`Active (${activeLoans.length})`} />
          <Tab label={`Returned (${returnedLoans.length})`} />
          <Tab label={`Overdue (${overdueLoans.length})`} />
        </Tabs>
      </Box>

      {/* Active Loans */}
      <TabPanel value={tabValue} index={0}>
        {activeLoans.length === 0 ? (
          <Box textAlign="center" py={8}>
            <BookIcon sx={{ fontSize: 80, color: 'text.disabled', mb: 2 }} />
            <Typography variant="h6" color="text.secondary">
              No active loans
            </Typography>
            <Typography color="text.secondary">
              Visit the library to borrow some books!
            </Typography>
          </Box>
        ) : (
          <motion.div variants={containerVariants} initial="hidden" animate="visible">
            <Box sx={{ 
              display: 'grid', 
              gridTemplateColumns: { 
                xs: '1fr', 
                md: '1fr 1fr' 
              }, 
              gap: 3 
            }}>
              {activeLoans.map((loan) => (
                <Box key={loan.id}>
                  <motion.div variants={cardVariants}>
                    <Card
                      sx={{
                        borderRadius: 2,
                        boxShadow: theme.shadows[2],
                        transition: 'all 0.3s ease',
                        border: isOverdue(loan) ? '2px solid' : '1px solid',
                        borderColor: isOverdue(loan) ? 'error.main' : 'divider',
                        '&:hover': {
                          transform: 'translateY(-2px)',
                          boxShadow: theme.shadows[8],
                        },
                      }}
                    >
                      <CardContent>
                        <Box display="flex" alignItems="center" mb={2}>
                          <Avatar
                            sx={{
                              bgcolor: `${getStatusColor(loan)}.main`,
                              mr: 2,
                              width: 50,
                              height: 50,
                            }}
                          >
                            <BookIcon />
                          </Avatar>
                          <Box flexGrow={1}>
                            <Typography variant="h6" fontWeight="bold">
                              {loan.book?.title || 'Unknown Book'}
                            </Typography>
                            <Typography color="text.secondary">
                              {loan.book?.authors?.[0]?.full_name || 'Unknown Author'}
                            </Typography>
                          </Box>
                          <Chip
                            label={getStatusText(loan)}
                            color={getStatusColor(loan)}
                            size="small"
                          />
                        </Box>

                        <Divider sx={{ my: 2 }} />

                        <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
                          <Box>
                            <Typography variant="body2" color="text.secondary">
                              Borrowed
                            </Typography>
                            <Typography variant="body2" fontWeight="bold">
                              {new Date(loan.loan_date).toLocaleDateString()}
                            </Typography>
                          </Box>
                          <Box>
                            <Typography variant="body2" color="text.secondary">
                              Due Date
                            </Typography>
                            <Typography 
                              variant="body2" 
                              fontWeight="bold"
                              color={isOverdue(loan) ? 'error.main' : 'text.primary'}
                            >
                              {new Date(loan.due_date).toLocaleDateString()}
                            </Typography>
                          </Box>
                        </Box>

                        {/* Progress bar for due date */}
                        {!isOverdue(loan) && (
                          <Box mt={2}>
                            <Box display="flex" justifyContent="space-between" mb={1}>
                              <Typography variant="body2" color="text.secondary">
                                Time Remaining
                              </Typography>
                              <Typography variant="body2" color="text.secondary">
                                {getDaysUntilDue(loan)} days
                              </Typography>
                            </Box>
                            <LinearProgress
                              variant="determinate"
                              value={Math.max(0, Math.min(100, (getDaysUntilDue(loan) / 14) * 100))}
                              color={getDaysUntilDue(loan) <= 3 ? 'warning' : 'primary'}
                              sx={{ height: 6, borderRadius: 3 }}
                            />
                          </Box>
                        )}

                        <Box display="flex" justifyContent="flex-end" gap={1} mt={2}>
                          <Button
                            startIcon={<ReturnIcon />}
                            variant="contained"
                            size="small"
                            color="success"
                            onClick={() => handleReturnBook(loan.id)}
                            disabled={loan.status === LoanStatus.RETURNED}
                            sx={{ borderRadius: 2 }}
                          >
                            Return
                          </Button>
                          <Button
                            startIcon={<RenewIcon />}
                            variant="outlined"
                            size="small"
                            onClick={() => setRenewDialog({ open: true, loan })}
                            disabled={isOverdue(loan) || loan.status === LoanStatus.RETURNED}
                            sx={{ borderRadius: 2 }}
                          >
                            Renew
                          </Button>
                        </Box>
                      </CardContent>
                    </Card>
                  </motion.div>
                </Box>
              ))}
            </Box>
          </motion.div>
        )}
      </TabPanel>

      {/* Returned Loans */}
      <TabPanel value={tabValue} index={1}>
        {returnedLoans.length === 0 ? (
          <Box textAlign="center" py={8}>
            <CheckCircleIcon sx={{ fontSize: 80, color: 'text.disabled', mb: 2 }} />
            <Typography variant="h6" color="text.secondary">
              No returned loans
            </Typography>
          </Box>
        ) : (
          <TableContainer component={Paper} sx={{ borderRadius: 2 }}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Book</TableCell>
                  <TableCell>Borrowed</TableCell>
                  <TableCell>Due Date</TableCell>
                  <TableCell>Returned</TableCell>
                  <TableCell>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {returnedLoans.map((loan) => (
                  <TableRow key={loan.id}>
                    <TableCell>
                      <Box>
                        <Typography fontWeight="bold">
                          {loan.book?.title || 'Unknown Book'}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {loan.book?.authors?.[0]?.full_name || 'Unknown Author'}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      {new Date(loan.loan_date).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      {new Date(loan.due_date).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      {loan.return_date ? new Date(loan.return_date).toLocaleDateString() : '-'}
                    </TableCell>
                    <TableCell>
                      <Chip label="Returned" color="success" size="small" />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </TabPanel>

      {/* Overdue Loans */}
      <TabPanel value={tabValue} index={2}>
        {overdueLoans.length === 0 ? (
          <Box textAlign="center" py={8}>
            <CheckCircleIcon sx={{ fontSize: 80, color: 'success.main', mb: 2 }} />
            <Typography variant="h6" color="success.main">
              No overdue loans
            </Typography>
            <Typography color="text.secondary">
              Great job keeping up with your due dates!
            </Typography>
          </Box>
        ) : (
          <Alert severity="error" sx={{ mb: 3 }}>
            You have {overdueLoans.length} overdue book(s). Please return them as soon as possible.
          </Alert>
        )}
      </TabPanel>

      {/* Renew Dialog */}
      <Dialog
        open={renewDialog.open}
        onClose={() => setRenewDialog({ open: false, loan: null })}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Renew Loan</DialogTitle>
        <DialogContent>
          {renewDialog.loan && (
            <Box>
              <Typography variant="h6" gutterBottom>
                {renewDialog.loan.book?.title}
              </Typography>
              <Typography color="text.secondary" gutterBottom>
                Current due date: {new Date(renewDialog.loan.due_date).toLocaleDateString()}
              </Typography>
              <TextField
                fullWidth
                label="New Due Date"
                type="date"
                defaultValue={new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]}
                sx={{ mt: 2 }}
                InputLabelProps={{ shrink: true }}
              />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRenewDialog({ open: false, loan: null })}>
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={() => {
              if (renewDialog.loan) {
                const newDate = new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString();
                handleRenewLoan(renewDialog.loan.id, newDate);
              }
            }}
          >
            Renew
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default MyLoansPage;
