import React, { useState } from 'react';
import { Link, Navigate } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  IconButton,
  InputAdornment,
  Alert,
  Container,
  useTheme,
  useMediaQuery,
  Stack,
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  MenuBook,
  AutoStories,
  LocalLibrary,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useAuth } from '../../contexts/AuthContext';
import DebugLogin from '../../components/DebugLogin';

const LoginPage: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const { user, login, error, isLoading } = useAuth();
  
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [localError, setLocalError] = useState('');

  // Redirect if already logged in
  if (user) {
    return <Navigate to="/dashboard" replace />;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError('');
    
    if (!formData.email || !formData.password) {
      setLocalError('Please fill in all fields');
      return;
    }

    console.log('LoginPage: Attempting login with:', formData.email);
    try {
      await login(formData.email, formData.password);
      console.log('LoginPage: Login successful');
    } catch (error: any) {
      console.error('LoginPage: Login failed:', error);
      // The error message is already set in the auth state by the login function
      // We don't need to set localError here since the auth error state will handle it
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  const containerVariants = {
    hidden: { opacity: 0, y: 50 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.6,
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.5 },
    },
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: theme.gradients.primary,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        p: 2,
      }}
    >
      <Container maxWidth="lg">
        <Stack 
          direction={{ xs: 'column', md: 'row' }} 
          spacing={4} 
          alignItems="center" 
          justifyContent="center"
          sx={{ minHeight: '100vh' }}
        >
          {/* Left Side - Welcome Section */}
          {!isMobile && (
            <Box sx={{ flex: 1, maxWidth: 600 }}>
              <motion.div
                initial="hidden"
                animate="visible"
                variants={containerVariants}
              >
                <Box sx={{ color: 'white', textAlign: 'center' }}>
                  <motion.div variants={itemVariants}>
                    <Box sx={{ display: 'flex', justifyContent: 'center', mb: 3 }}>
                      <MenuBook sx={{ fontSize: 80, opacity: 0.9 }} />
                    </Box>
                  </motion.div>
                  
                  <motion.div variants={itemVariants}>
                    <Typography variant="h2" component="h1" gutterBottom fontWeight="bold">
                      My Book Shelf
                    </Typography>
                  </motion.div>
                  
                  <motion.div variants={itemVariants}>
                    <Typography variant="h5" sx={{ mb: 4, opacity: 0.9 }}>
                      Your Personal Library Management System
                    </Typography>
                  </motion.div>
                  
                  <motion.div variants={itemVariants}>
                    <Stack direction="row" spacing={4} justifyContent="center" sx={{ mb: 4 }}>
                      <Box sx={{ textAlign: 'center' }}>
                        <AutoStories sx={{ fontSize: 40, mb: 1 }} />
                        <Typography variant="body1">Browse Books</Typography>
                      </Box>
                      <Box sx={{ textAlign: 'center' }}>
                        <LocalLibrary sx={{ fontSize: 40, mb: 1 }} />
                        <Typography variant="body1">Manage Loans</Typography>
                      </Box>
                    </Stack>
                  </motion.div>
                  
                  <motion.div variants={itemVariants}>
                    <Typography variant="body1" sx={{ opacity: 0.8, maxWidth: 400, mx: 'auto' }}>
                      Discover, borrow, and manage your favorite books with our intuitive 
                      library management system. Join thousands of readers today!
                    </Typography>
                  </motion.div>
                </Box>
              </motion.div>
            </Box>
          )}

          {/* Right Side - Login Form */}
          <Box sx={{ flex: 1, maxWidth: 500 }}>
            <motion.div
              initial="hidden"
              animate="visible"
              variants={containerVariants}
            >
              <Card
                sx={{
                  maxWidth: 400,
                  mx: 'auto',
                  boxShadow: theme.customShadows.card,
                  background: theme.gradients.card,
                  backdropFilter: 'blur(20px)',
                  border: '1px solid rgba(255, 255, 255, 0.2)',
                }}
              >
                <CardContent sx={{ p: 4 }}>
                  <motion.div variants={itemVariants}>
                    <Box sx={{ textAlign: 'center', mb: 3 }}>
                      {isMobile && (
                        <MenuBook sx={{ fontSize: 40, color: 'primary.main', mb: 2 }} />
                      )}
                      <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
                        Welcome Back
                      </Typography>
                      <Typography variant="body1" color="text.secondary">
                        Sign in to your account
                      </Typography>
                    </Box>
                  </motion.div>

                  {(error || localError) && (
                    <motion.div variants={itemVariants}>
                      <Alert severity="error" sx={{ mb: 3 }}>
                        {error || localError}
                      </Alert>
                    </motion.div>
                  )}

                  <motion.div variants={itemVariants}>
                    <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
                      <TextField
                        fullWidth
                        label="Email Address"
                        name="email"
                        type="email"
                        value={formData.email}
                        onChange={handleChange}
                        margin="normal"
                        required
                        autoComplete="email"
                        sx={{ mb: 2 }}
                      />

                      <TextField
                        fullWidth
                        label="Password"
                        name="password"
                        type={showPassword ? 'text' : 'password'}
                        value={formData.password}
                        onChange={handleChange}
                        margin="normal"
                        required
                        autoComplete="current-password"
                        InputProps={{
                          endAdornment: (
                            <InputAdornment position="end">
                              <IconButton
                                onClick={() => setShowPassword(!showPassword)}
                                edge="end"
                              >
                                {showPassword ? <VisibilityOff /> : <Visibility />}
                              </IconButton>
                            </InputAdornment>
                          ),
                        }}
                        sx={{ mb: 3 }}
                      />

                      <Button
                        type="submit"
                        fullWidth
                        variant="contained"
                        size="large"
                        disabled={isLoading}
                        sx={{
                          py: 1.5,
                          mb: 2,
                          fontSize: '1.1rem',
                          fontWeight: 600,
                        }}
                      >
                        {isLoading ? 'Signing In...' : 'Sign In'}
                      </Button>

                      <Box sx={{ textAlign: 'center', mt: 3 }}>
                        <Typography variant="body2" color="text.secondary">
                          Don't have an account?{' '}
                          <Link 
                            to="/register" 
                            style={{ 
                              color: theme.palette.primary.main,
                              textDecoration: 'none',
                              fontWeight: 500,
                            }}
                          >
                            Sign up here
                          </Link>
                        </Typography>
                      </Box>
                    </Box>
                  </motion.div>
                </CardContent>
              </Card>
            </motion.div>
          </Box>
        </Stack>
      </Container>
      
      {/* Debug Component */}
      <DebugLogin />
    </Box>
  );
};

export default LoginPage;
