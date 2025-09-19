import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Avatar,
  Button,
  LinearProgress,
  Chip,
  Stack,
  useTheme,
} from '@mui/material';
import {
  MenuBook,
  TrendingUp,
  Schedule,
  Star,
  Person,
  LibraryBooks,
  AccessTime,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useAuth } from '../../contexts/AuthContext';
import { useDashboardStats, usePopularBooks, useUserLoans } from '../../hooks/useApi';

const DashboardPage: React.FC = () => {
  const theme = useTheme();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { data: stats, isLoading: statsLoading } = useDashboardStats();
  const { data: popularBooks } = usePopularBooks();
  const { data: userLoans } = useUserLoans();

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: { duration: 0.5 },
    },
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good Morning';
    if (hour < 18) return 'Good Afternoon';
    return 'Good Evening';
  };

  const statsCards = [
    {
      title: 'Books Read',
      value: userLoans?.filter(loan => loan.status === 'returned').length || 0,
      icon: <MenuBook />,
      color: theme.palette.primary.main,
      trend: '+12%',
    },
    {
      title: 'Currently Reading',
      value: userLoans?.filter(loan => loan.status === 'active').length || 0,
      icon: <AccessTime />,
      color: theme.palette.warning.main,
      trend: '+5%',
    },
    {
      title: 'Favorite Genre',
      value: 'Fiction',
      icon: <Star />,
      color: theme.palette.success.main,
      trend: 'Most read',
    },
    {
      title: 'Reading Goal',
      value: '8/12',
      icon: <TrendingUp />,
      color: theme.palette.info.main,
      trend: '67%',
    },
  ];

  return (
    <motion.div
      initial="hidden"
      animate="visible"
      variants={containerVariants}
    >
      <Box sx={{ p: { xs: 2, md: 3 } }}>
        {/* Welcome Section */}
        <motion.div variants={itemVariants}>
          <Card
            sx={{
              mb: 4,
              background: theme.gradients.primary,
              color: 'white',
              overflow: 'hidden',
            }}
          >
            <CardContent sx={{ p: 4, position: 'relative' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 3 }}>
                <Avatar
                  sx={{
                    width: 80,
                    height: 80,
                    bgcolor: 'rgba(255, 255, 255, 0.2)',
                    fontSize: '2rem',
                    border: '3px solid rgba(255, 255, 255, 0.3)',
                  }}
                >
                  {user?.first_name?.charAt(0).toUpperCase() || 
                   user?.username?.charAt(0).toUpperCase() || 'U'}
                </Avatar>
                <Box>
                  <Typography variant="h4" fontWeight="bold" gutterBottom>
                    {getGreeting()}, {user?.first_name || user?.username}!
                  </Typography>
                  <Typography variant="h6" sx={{ opacity: 0.9 }}>
                    Ready to continue your reading journey?
                  </Typography>
                  <Button
                    variant="contained"
                    onClick={() => navigate('/library')}
                    sx={{
                      mt: 2,
                      bgcolor: 'rgba(255, 255, 255, 0.2)',
                      '&:hover': { bgcolor: 'rgba(255, 255, 255, 0.3)' },
                    }}
                  >
                    Browse Library
                  </Button>
                </Box>
              </Box>
              {/* Decorative elements */}
              <Box
                sx={{
                  position: 'absolute',
                  top: -20,
                  right: -20,
                  width: 100,
                  height: 100,
                  borderRadius: '50%',
                  bgcolor: 'rgba(255, 255, 255, 0.1)',
                }}
              />
              <Box
                sx={{
                  position: 'absolute',
                  bottom: -30,
                  right: 50,
                  width: 60,
                  height: 60,
                  borderRadius: '50%',
                  bgcolor: 'rgba(255, 255, 255, 0.05)',
                }}
              />
            </CardContent>
          </Card>
        </motion.div>

        {/* Stats Cards */}
        <Box sx={{ mb: 4 }}>
          <Stack 
            direction={{ xs: 'column', sm: 'row' }} 
            spacing={3}
            sx={{
              '& > *': {
                flex: { sm: 1 },
              },
            }}
          >
            {statsCards.map((stat, index) => (
              <motion.div variants={itemVariants} key={stat.title}>
                <Card
                  sx={{
                    height: '100%',
                    background: theme.gradients.card,
                    transition: 'transform 0.2s',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                    },
                  }}
                >
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Avatar
                        sx={{
                          bgcolor: `${stat.color}20`,
                          color: stat.color,
                          mr: 2,
                        }}
                      >
                        {stat.icon}
                      </Avatar>
                      <Box>
                        <Typography variant="h4" fontWeight="bold">
                          {stat.value}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {stat.title}
                        </Typography>
                      </Box>
                    </Box>
                    <Chip
                      label={stat.trend}
                      size="small"
                      sx={{
                        bgcolor: `${stat.color}20`,
                        color: stat.color,
                      }}
                    />
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </Stack>
        </Box>

        <Stack direction={{ xs: 'column', md: 'row' }} spacing={3}>
          {/* Current Reading */}
          <Box sx={{ flex: { md: 2 } }}>
            <motion.div variants={itemVariants}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Continue Reading
                  </Typography>
                  {userLoans?.filter(loan => loan.status === 'active').length ? (
                    <Stack spacing={2}>
                      {userLoans
                        .filter(loan => loan.status === 'active')
                        .slice(0, 3)
                        .map((loan) => (
                          <Box
                            key={loan.id}
                            sx={{
                              p: 2,
                              border: '1px solid',
                              borderColor: 'divider',
                              borderRadius: 2,
                            }}
                          >
                            <Typography variant="subtitle1" fontWeight="bold">
                              {loan.book?.title || 'Unknown Title'}
                            </Typography>
                            <Typography variant="body2" color="text.secondary" gutterBottom>
                              by {loan.book?.authors?.[0]?.full_name || 'Unknown Author'}
                            </Typography>
                            <Box sx={{ mt: 1 }}>
                              <Typography variant="body2" gutterBottom>
                                Progress: 65%
                              </Typography>
                              <LinearProgress
                                variant="determinate"
                                value={65}
                                sx={{ height: 6, borderRadius: 3 }}
                              />
                            </Box>
                          </Box>
                        ))}
                    </Stack>
                  ) : (
                    <Box sx={{ textAlign: 'center', py: 4 }}>
                      <LibraryBooks sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
                      <Typography variant="body1" color="text.secondary">
                        No books currently borrowed
                      </Typography>
                      <Button 
                        variant="outlined" 
                        onClick={() => navigate('/library')}
                        sx={{ mt: 2 }}
                      >
                        Browse Library
                      </Button>
                    </Box>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          </Box>

          {/* Popular Books */}
          <Box sx={{ flex: { md: 1 } }}>
            <motion.div variants={itemVariants}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Popular This Week
                  </Typography>
                  <Stack spacing={2}>
                    {popularBooks?.slice(0, 5).map((book, index) => (
                      <Box
                        key={book.id}
                        sx={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: 2,
                        }}
                      >
                        <Typography
                          variant="h6"
                          color="primary"
                          sx={{ minWidth: 20 }}
                        >
                          {index + 1}
                        </Typography>
                        <Box sx={{ flexGrow: 1 }}>
                          <Typography variant="subtitle2" noWrap>
                            {book.title}
                          </Typography>
                          <Typography variant="body2" color="text.secondary" noWrap>
                            {book.authors?.[0]?.full_name || 'Unknown Author'}
                          </Typography>
                        </Box>
                        <Chip
                          size="small"
                          label={`${book.available_copies} left`}
                          color={book.available_copies > 0 ? 'success' : 'error'}
                        />
                      </Box>
                    ))}
                  </Stack>
                </CardContent>
              </Card>
            </motion.div>
          </Box>
        </Stack>
      </Box>
    </motion.div>
  );
};

export default DashboardPage;
