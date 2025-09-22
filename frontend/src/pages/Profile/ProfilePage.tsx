import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Grid,
  Avatar,
  Divider,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip,
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  CircularProgress,
  Alert,
  useTheme
} from '@mui/material';
import {
  Person as PersonIcon,
  Email as EmailIcon,
  Edit as EditIcon,
  Security as SecurityIcon,
  History as HistoryIcon,
  Book as BookIcon,
  Assignment as AssignmentIcon,
  Verified as VerifiedIcon,
  CalendarToday as CalendarIcon
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useAuth } from '../../contexts/AuthContext';
import { apiService } from '../../services/api';
import { User, Loan } from '../../types';

const ProfilePage: React.FC = () => {
  const theme = useTheme();
  const { user: currentUser } = useAuth();
  const [user, setUser] = useState<User | null>(currentUser);
  const [loans, setLoans] = useState<Loan[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [editDialog, setEditDialog] = useState(false);
  const [editForm, setEditForm] = useState({
    first_name: '',
    last_name: '',
    username: ''
  });

  useEffect(() => {
    if (currentUser) {
      setUser(currentUser);
      setEditForm({
        first_name: currentUser.first_name || '',
        last_name: currentUser.last_name || '',
        username: currentUser.username || ''
      });
      fetchUserLoans();
    }
  }, [currentUser]);

  const fetchUserLoans = async () => {
    try {
      setLoading(true);
      const response = await apiService.getUserLoans();
      setLoans(response);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch loans');
    } finally {
      setLoading(false);
    }
  };

  const handleEditProfile = async () => {
    try {
      // TODO: Implement update profile functionality
      console.log('Updating profile:', editForm);
      setEditDialog(false);
    } catch (err: any) {
      setError(err.message || 'Failed to update profile');
    }
  };

  const getInitials = (user: User): string => {
    if (user.first_name && user.last_name) {
      return `${user.first_name[0]}${user.last_name[0]}`.toUpperCase();
    }
    if (user.username) {
      return user.username.substring(0, 2).toUpperCase();
    }
    return user.email.substring(0, 2).toUpperCase();
  };

  const getFullName = (user: User): string => {
    if (user.first_name && user.last_name) {
      return `${user.first_name} ${user.last_name}`;
    }
    return user.username || user.email;
  };

  const getRoleColor = (role: string) => {
    switch (role.toLowerCase()) {
      case 'admin': return 'error';
      case 'librarian': return 'warning';
      case 'member': return 'primary';
      default: return 'default';
    }
  };

  const activeLoans = loans.filter(loan => !loan.return_date);
  const completedLoans = loans.filter(loan => loan.return_date);

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

  if (!user) {
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
        👤 Profile
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        <Box sx={{ 
          display: 'grid', 
          gridTemplateColumns: { xs: '1fr', md: '1fr 2fr' }, 
          gap: 3 
        }}>
          {/* Profile Information */}
          <Box>
            <motion.div variants={cardVariants}>
              <Card sx={{ borderRadius: 2, boxShadow: theme.shadows[2] }}>
                <CardContent sx={{ textAlign: 'center', p: 4 }}>
                  <Avatar
                    sx={{
                      width: 120,
                      height: 120,
                      fontSize: '3rem',
                      bgcolor: 'primary.main',
                      mb: 2,
                      mx: 'auto',
                    }}
                  >
                    {getInitials(user)}
                  </Avatar>
                  
                  <Typography variant="h5" gutterBottom fontWeight="bold">
                    {getFullName(user)}
                  </Typography>
                  
                  <Box display="flex" justifyContent="center" mb={2}>
                    <Chip
                      label={user.role.toUpperCase()}
                      color={getRoleColor(user.role) as any}
                      icon={<AssignmentIcon />}
                    />
                  </Box>

                  <Box display="flex" alignItems="center" justifyContent="center" mb={2}>
                    <EmailIcon sx={{ mr: 1, color: 'text.secondary' }} />
                    <Typography color="text.secondary">
                      {user.email}
                    </Typography>
                  </Box>

                  {user.email_verified && (
                    <Box display="flex" alignItems="center" justifyContent="center" mb={2}>
                      <VerifiedIcon sx={{ mr: 1, color: 'success.main' }} />
                      <Typography color="success.main" variant="body2">
                        Email Verified
                      </Typography>
                    </Box>
                  )}

                  <Box display="flex" alignItems="center" justifyContent="center" mb={3}>
                    <CalendarIcon sx={{ mr: 1, color: 'text.secondary' }} />
                    <Typography color="text.secondary" variant="body2">
                      Member since {new Date(user.created_at).toLocaleDateString()}
                    </Typography>
                  </Box>

                  <Button
                    variant="contained"
                    startIcon={<EditIcon />}
                    onClick={() => setEditDialog(true)}
                    fullWidth
                    sx={{ borderRadius: 2 }}
                  >
                    Edit Profile
                  </Button>
                </CardContent>
              </Card>
            </motion.div>
          </Box>

          {/* Activity Overview */}
          <Box>
            <motion.div variants={cardVariants}>
              <Card sx={{ borderRadius: 2, boxShadow: theme.shadows[2], mb: 3 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom fontWeight="bold">
                    📊 Activity Overview
                  </Typography>
                  
                  <Box sx={{ 
                    display: 'grid', 
                    gridTemplateColumns: { xs: 'repeat(2, 1fr)', sm: 'repeat(4, 1fr)' }, 
                    gap: 3 
                  }}>
                    <Box>
                      <Box textAlign="center" p={2}>
                        <BookIcon sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
                        <Typography variant="h4" fontWeight="bold">
                          {activeLoans.length}
                        </Typography>
                        <Typography color="text.secondary" variant="body2">
                          Active Loans
                        </Typography>
                      </Box>
                    </Box>
                    <Box>
                      <Box textAlign="center" p={2}>
                        <HistoryIcon sx={{ fontSize: 40, color: 'success.main', mb: 1 }} />
                        <Typography variant="h4" fontWeight="bold">
                          {completedLoans.length}
                        </Typography>
                        <Typography color="text.secondary" variant="body2">
                          Books Read
                        </Typography>
                      </Box>
                    </Box>
                    <Box>
                      <Box textAlign="center" p={2}>
                        <AssignmentIcon sx={{ fontSize: 40, color: 'info.main', mb: 1 }} />
                        <Typography variant="h4" fontWeight="bold">
                          {loans.length}
                        </Typography>
                        <Typography color="text.secondary" variant="body2">
                          Total Loans
                        </Typography>
                      </Box>
                    </Box>
                    <Box>
                      <Box textAlign="center" p={2}>
                        <SecurityIcon sx={{ fontSize: 40, color: 'warning.main', mb: 1 }} />
                        <Typography variant="h4" fontWeight="bold">
                          {user.is_active ? 'Active' : 'Inactive'}
                        </Typography>
                        <Typography color="text.secondary" variant="body2">
                          Account Status
                        </Typography>
                      </Box>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </motion.div>

            {/* Recent Activity */}
            <motion.div variants={cardVariants}>
              <Card sx={{ borderRadius: 2, boxShadow: theme.shadows[2] }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom fontWeight="bold">
                    📚 Recent Loans
                  </Typography>
                  
                  {loading ? (
                    <Box display="flex" justifyContent="center" py={4}>
                      <CircularProgress size={24} />
                    </Box>
                  ) : loans.length === 0 ? (
                    <Box textAlign="center" py={4}>
                      <BookIcon sx={{ fontSize: 60, color: 'text.disabled', mb: 2 }} />
                      <Typography color="text.secondary">
                        No loan history available
                      </Typography>
                    </Box>
                  ) : (
                    <List>
                      {loans.slice(0, 5).map((loan, index) => (
                        <React.Fragment key={loan.id}>
                          <ListItem>
                            <ListItemIcon>
                              <BookIcon color={loan.return_date ? 'success' : 'primary'} />
                            </ListItemIcon>
                            <ListItemText
                              primary={loan.book_title || 'Unknown Book'}
                              secondary={
                                <Box>
                                  <Typography variant="body2" color="text.secondary">
                                    {loan.book?.authors?.[0]?.full_name || 'Unknown Author'}
                                  </Typography>
                                  <Typography variant="body2" color="text.secondary">
                                    Borrowed: {new Date(loan.loan_date).toLocaleDateString()}
                                    {loan.return_date && 
                                      ` • Returned: ${new Date(loan.return_date).toLocaleDateString()}`
                                    }
                                  </Typography>
                                </Box>
                              }
                            />
                            <Chip
                              label={loan.return_date ? 'Returned' : 'Active'}
                              color={loan.return_date ? 'success' : 'primary'}
                              size="small"
                            />
                          </ListItem>
                          {index < Math.min(loans.length, 5) - 1 && <Divider />}
                        </React.Fragment>
                      ))}
                    </List>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          </Box>
        </Box>
      </motion.div>

      {/* Edit Profile Dialog */}
      <Dialog
        open={editDialog}
        onClose={() => setEditDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Edit Profile</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <TextField
              fullWidth
              label="First Name"
              value={editForm.first_name}
              onChange={(e) => setEditForm({ ...editForm, first_name: e.target.value })}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Last Name"
              value={editForm.last_name}
              onChange={(e) => setEditForm({ ...editForm, last_name: e.target.value })}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Username"
              value={editForm.username}
              onChange={(e) => setEditForm({ ...editForm, username: e.target.value })}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Email"
              value={user.email}
              disabled
              helperText="Email cannot be changed"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialog(false)}>
            Cancel
          </Button>
          <Button variant="contained" onClick={handleEditProfile}>
            Save Changes
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ProfilePage;
