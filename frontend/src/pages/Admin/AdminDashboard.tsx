import React from 'react';
import { Box, Typography, Card, CardContent, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { 
  People, 
  Book, 
  Assignment, 
  TrendingUp,
  PersonAdd,
  BookmarkAdd
} from '@mui/icons-material';

const AdminDashboard: React.FC = () => {
  const navigate = useNavigate();

  const adminCards = [
    {
      title: 'User Management',
      description: 'View and manage all users in the system',
      icon: <People sx={{ fontSize: 40, color: 'primary.main' }} />,
      action: () => navigate('/admin/users'),
      buttonText: 'Manage Users'
    },
    {
      title: 'Book Management',
      description: 'Add, edit, and delete books in the library',
      icon: <Book sx={{ fontSize: 40, color: 'secondary.main' }} />,
      action: () => navigate('/admin/books'),
      buttonText: 'Manage Books'
    },
    {
      title: 'Loan Management',
      description: 'Monitor and manage book loans',
      icon: <Assignment sx={{ fontSize: 40, color: 'info.main' }} />,
      action: () => navigate('/admin/loans'),
      buttonText: 'Manage Loans'
    }
  ];

  const quickActions = [
    {
      title: 'Add New User',
      icon: <PersonAdd />,
      action: () => navigate('/admin/users', { state: { openCreateDialog: true } }),
      color: 'primary'
    },
    {
      title: 'Add New Book',
      icon: <BookmarkAdd />,
      action: () => navigate('/admin/books', { state: { openCreateDialog: true } }),
      color: 'secondary'
    }
  ];

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom sx={{ mb: 4 }}>
        Admin Dashboard
      </Typography>

      {/* Quick Actions */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          Quick Actions
        </Typography>
        <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 2 }}>
          {quickActions.map((action, index) => (
            <Button
              key={index}
              variant="contained"
              color={action.color as any}
              fullWidth
              startIcon={action.icon}
              onClick={action.action}
              sx={{ py: 2 }}
            >
              {action.title}
            </Button>
          ))}
        </Box>
      </Box>

      {/* Admin Management Cards */}
      <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
        Management Sections
      </Typography>
      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 3 }}>
        {adminCards.map((card, index) => (
          <Card 
            key={index}
            sx={{ 
              height: '100%', 
              display: 'flex', 
              flexDirection: 'column',
              transition: 'transform 0.2s, elevation 0.2s',
              '&:hover': {
                transform: 'translateY(-4px)',
                elevation: 8
              }
            }}
          >
            <CardContent sx={{ flexGrow: 1, textAlign: 'center', p: 3 }}>
              <Box sx={{ mb: 2 }}>
                {card.icon}
              </Box>
              <Typography variant="h6" component="h2" gutterBottom>
                {card.title}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                {card.description}
              </Typography>
              <Button
                variant="contained"
                onClick={card.action}
                fullWidth
                sx={{ mt: 'auto' }}
              >
                {card.buttonText}
              </Button>
            </CardContent>
          </Card>
        ))}
      </Box>
    </Box>
  );
};

export default AdminDashboard;
