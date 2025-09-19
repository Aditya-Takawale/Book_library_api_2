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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
  Pagination
} from '@mui/material';
import {
  Edit,
  Delete,
  PersonAdd,
  Visibility
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useSnackbar } from 'notistack';
import apiService from '../../services/api';
import { User, UserRole, UserStatus, RegisterRequest } from '../../types';

const UserManagement: React.FC = () => {
  const location = useLocation();
  const [page, setPage] = useState(1);
  const [limit] = useState(10);
  const [editUser, setEditUser] = useState<User | null>(null);
  const [deleteUser, setDeleteUser] = useState<User | null>(null);
  const [createUser, setCreateUser] = useState<RegisterRequest | null>(null);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  
  const { enqueueSnackbar } = useSnackbar();
  const queryClient = useQueryClient();

  const handleCreate = () => {
    setCreateUser({
      username: '',
      email: '',
      password: '',
      first_name: '',
      last_name: '',
      role: UserRole.MEMBER,
    });
    setIsCreateDialogOpen(true);
  };

  useEffect(() => {
    if (location.state?.openCreateDialog) {
      handleCreate();
    }
  }, [location.state]);

  // Fetch users
  const { data: users, isLoading, error } = useQuery({
    queryKey: ['users'],
    queryFn: () => apiService.getUsers({ skip: 0, limit: 1000 }), // Fetch all users
  });

  // Calculate users for current page
  const usersList = React.useMemo(() => {
    if (!users) return [];
    const startIndex = (page - 1) * limit;
    const endIndex = startIndex + limit;
    return users.slice(startIndex, endIndex);
  }, [users, page, limit]);

  // Calculate total pages
  const totalPages = Math.ceil((users?.length || 0) / limit);

  // Update user mutation
  const updateUserMutation = useMutation({
    mutationFn: ({ id, userData }: { id: number; userData: Partial<User> }) =>
      apiService.updateUser(id, userData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      enqueueSnackbar('User updated successfully', { variant: 'success' });
      setIsEditDialogOpen(false);
      setEditUser(null);
    },
    onError: (error: any) => {
      enqueueSnackbar(`Failed to update user: ${error.message}`, { variant: 'error' });
    },
  });

  // Delete user mutation
  const deleteUserMutation = useMutation({
    mutationFn: (id: number) => apiService.deleteUser(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      enqueueSnackbar('User deleted successfully', { variant: 'success' });
      setIsDeleteDialogOpen(false);
      setDeleteUser(null);
    },
    onError: (error: any) => {
      enqueueSnackbar(`Failed to delete user: ${error.message}`, { variant: 'error' });
    },
  });

  // Create user mutation
  const createUserMutation = useMutation({
    mutationFn: (userData: RegisterRequest) => apiService.createUser(userData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      enqueueSnackbar('User created successfully', { variant: 'success' });
      setIsCreateDialogOpen(false);
      setCreateUser(null);
    },
    onError: (error: any) => {
      enqueueSnackbar(`Failed to create user: ${error.message}`, { variant: 'error' });
    },
  });

  const handleEditUser = (user: User) => {
    setEditUser({ ...user });
    setIsEditDialogOpen(true);
  };

  const handleDeleteUser = (user: User) => {
    setDeleteUser(user);
    setIsDeleteDialogOpen(true);
  };

  const handleSaveCreateUser = () => {
    if (!createUser) return;
    
    // Basic validation
    if (!createUser.username || !createUser.email || !createUser.password) {
      enqueueSnackbar('Please fill in all required fields', { variant: 'error' });
      return;
    }
    
    createUserMutation.mutate(createUser);
  };

  const handleSaveUser = () => {
    if (!editUser) return;
    
    updateUserMutation.mutate({
      id: editUser.id,
      userData: {
        role: editUser.role,
        is_active: editUser.is_active,
        first_name: editUser.first_name,
        last_name: editUser.last_name
      }
    });
  };

  const handleConfirmDelete = () => {
    if (!deleteUser) return;
    deleteUserMutation.mutate(deleteUser.id);
  };

  const getRoleColor = (role: UserRole) => {
    switch (role) {
      case UserRole.ADMIN:
        return 'error';
      case UserRole.LIBRARIAN:
        return 'warning';
      case UserRole.MEMBER:
        return 'primary';
      case UserRole.GUEST:
        return 'default';
      default:
        return 'default';
    }
  };

  const getStatusColor = (isActive: boolean) => {
    return isActive ? 'success' : 'error';
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
        Failed to load users. Please try again later.
      </Alert>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          User Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<PersonAdd />}
          onClick={handleCreate}
          sx={{ ml: 'auto' }}
        >
          Add User
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Email</TableCell>
              <TableCell>Username</TableCell>
              <TableCell>Name</TableCell>
              <TableCell>Role</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Created</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {usersList.map((user) => (
              <TableRow key={user.id} hover>
                <TableCell>{user.id}</TableCell>
                <TableCell>{user.email}</TableCell>
                <TableCell>{user.username}</TableCell>
                <TableCell>
                  {user.first_name && user.last_name
                    ? `${user.first_name} ${user.last_name}`
                    : '-'}
                </TableCell>
                <TableCell>
                  <Chip
                    label={user.role}
                    color={getRoleColor(user.role)}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Chip
                    label={user.is_active ? 'Active' : 'Inactive'}
                    color={getStatusColor(user.is_active)}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  {new Date(user.created_at).toLocaleDateString()}
                </TableCell>
                <TableCell>
                  <IconButton
                    size="small"
                    onClick={() => handleEditUser(user)}
                    color="primary"
                  >
                    <Edit />
                  </IconButton>
                  <IconButton
                    size="small"
                    onClick={() => handleDeleteUser(user)}
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

      {/* Edit User Dialog */}
      <Dialog open={isEditDialogOpen} onClose={() => setIsEditDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Edit User</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <TextField
              fullWidth
              label="First Name"
              value={editUser?.first_name || ''}
              onChange={(e) => setEditUser(prev => prev ? { ...prev, first_name: e.target.value } : null)}
              margin="normal"
            />
            <TextField
              fullWidth
              label="Last Name"
              value={editUser?.last_name || ''}
              onChange={(e) => setEditUser(prev => prev ? { ...prev, last_name: e.target.value } : null)}
              margin="normal"
            />
            <FormControl fullWidth margin="normal">
              <InputLabel>Role</InputLabel>
              <Select
                value={editUser?.role || ''}
                onChange={(e) => setEditUser(prev => prev ? { ...prev, role: e.target.value as UserRole } : null)}
              >
                {Object.values(UserRole).map((role) => (
                  <MenuItem key={role} value={role}>
                    {role}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <FormControl fullWidth margin="normal">
              <InputLabel>Status</InputLabel>
              <Select
                value={editUser?.is_active ? 'active' : 'inactive'}
                onChange={(e) => setEditUser(prev => prev ? { ...prev, is_active: e.target.value === 'active' } : null)}
              >
                <MenuItem value="active">Active</MenuItem>
                <MenuItem value="inactive">Inactive</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsEditDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleSaveUser}
            variant="contained"
            disabled={updateUserMutation.isPending}
          >
            {updateUserMutation.isPending ? 'Saving...' : 'Save'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete User Dialog */}
      <Dialog open={isDeleteDialogOpen} onClose={() => setIsDeleteDialogOpen(false)}>
        <DialogTitle>Delete User</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete user "{deleteUser?.username}"? This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsDeleteDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleConfirmDelete}
            color="error"
            variant="contained"
            disabled={deleteUserMutation.isPending}
          >
            {deleteUserMutation.isPending ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Create User Dialog */}
      <Dialog open={isCreateDialogOpen} onClose={() => setIsCreateDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add New User</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            <TextField
              label="Username"
              value={createUser?.username || ''}
              onChange={(e) => setCreateUser(prev => prev ? { ...prev, username: e.target.value } : null)}
              required
            />
            <TextField
              label="Email"
              type="email"
              value={createUser?.email || ''}
              onChange={(e) => setCreateUser(prev => prev ? { ...prev, email: e.target.value } : null)}
              required
            />
            <TextField
              label="Password"
              type="password"
              value={createUser?.password || ''}
              onChange={(e) => setCreateUser(prev => prev ? { ...prev, password: e.target.value } : null)}
              required
            />
            <TextField
              label="First Name"
              value={createUser?.first_name || ''}
              onChange={(e) => setCreateUser(prev => prev ? { ...prev, first_name: e.target.value } : null)}
            />
            <TextField
              label="Last Name"
              value={createUser?.last_name || ''}
              onChange={(e) => setCreateUser(prev => prev ? { ...prev, last_name: e.target.value } : null)}
            />
            <FormControl>
              <InputLabel>Role</InputLabel>
              <Select
                value={createUser?.role || UserRole.MEMBER}
                onChange={(e) => setCreateUser(prev => prev ? { ...prev, role: e.target.value as UserRole } : null)}
              >
                <MenuItem value={UserRole.MEMBER}>Member</MenuItem>
                <MenuItem value={UserRole.LIBRARIAN}>Librarian</MenuItem>
                <MenuItem value={UserRole.ADMIN}>Admin</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsCreateDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleSaveCreateUser}
            variant="contained"
            disabled={createUserMutation.isPending}
          >
            {createUserMutation.isPending ? 'Creating...' : 'Create User'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default UserManagement;
