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
  Stack,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  MenuBook,
  PersonAdd,
  Email,
  Person,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useAuth } from '../../contexts/AuthContext';

const RegisterPage: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const { user, register, error, isLoading } = useAuth();
  
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    full_name: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [localError, setLocalError] = useState('');

  // Redirect if already logged in
  if (user) {
    return <Navigate to="/dashboard" replace />;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError('');
    
    if (!formData.username || !formData.email || !formData.password || !formData.full_name) {
      setLocalError('Please fill in all fields');
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setLocalError('Passwords do not match');
      return;
    }

    if (formData.password.length < 6) {
      setLocalError('Password must be at least 6 characters long');
      return;
    }

    try {
      await register({
        username: formData.username,
        email: formData.email,
        password: formData.password,
        full_name: formData.full_name,
      });
    } catch (error: any) {
      setLocalError(error.message);
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
                      <PersonAdd sx={{ fontSize: 80, opacity: 0.9 }} />
                    </Box>
                  </motion.div>
                  
                  <motion.div variants={itemVariants}>
                    <Typography variant="h2" component="h1" gutterBottom fontWeight="bold">
                      Join Our Library
                    </Typography>
                  </motion.div>
                  
                  <motion.div variants={itemVariants}>
                    <Typography variant="h5" sx={{ mb: 4, opacity: 0.9 }}>
                      Start Your Reading Journey Today
                    </Typography>
                  </motion.div>
                  
                  <motion.div variants={itemVariants}>
                    <Stack direction="row" spacing={4} justifyContent="center" sx={{ mb: 4 }}>
                      <Box sx={{ textAlign: 'center' }}>
                        <MenuBook sx={{ fontSize: 40, mb: 1 }} />
                        <Typography variant="body1">Unlimited Access</Typography>
                      </Box>
                      <Box sx={{ textAlign: 'center' }}>
                        <Person sx={{ fontSize: 40, mb: 1 }} />
                        <Typography variant="body1">Personal Profile</Typography>
                      </Box>
                    </Stack>
                  </motion.div>
                  
                  <motion.div variants={itemVariants}>
                    <Typography variant="body1" sx={{ opacity: 0.8, maxWidth: 400, mx: 'auto' }}>
                      Create your account to access thousands of books, track your reading 
                      progress, and join our community of book lovers.
                    </Typography>
                  </motion.div>
                </Box>
              </motion.div>
            </Box>
          )}

          {/* Right Side - Registration Form */}
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
                        <PersonAdd sx={{ fontSize: 40, color: 'primary.main', mb: 2 }} />
                      )}
                      <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
                        Create Account
                      </Typography>
                      <Typography variant="body1" color="text.secondary">
                        Join our library community
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
                        label="Full Name"
                        name="full_name"
                        value={formData.full_name}
                        onChange={handleChange}
                        margin="normal"
                        required
                        autoComplete="name"
                        InputProps={{
                          startAdornment: (
                            <InputAdornment position="start">
                              <Person />
                            </InputAdornment>
                          ),
                        }}
                        sx={{ mb: 2 }}
                      />

                      <TextField
                        fullWidth
                        label="Username"
                        name="username"
                        value={formData.username}
                        onChange={handleChange}
                        margin="normal"
                        required
                        autoComplete="username"
                        sx={{ mb: 2 }}
                      />

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
                        InputProps={{
                          startAdornment: (
                            <InputAdornment position="start">
                              <Email />
                            </InputAdornment>
                          ),
                        }}
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
                        autoComplete="new-password"
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
                        sx={{ mb: 2 }}
                      />

                      <TextField
                        fullWidth
                        label="Confirm Password"
                        name="confirmPassword"
                        type={showConfirmPassword ? 'text' : 'password'}
                        value={formData.confirmPassword}
                        onChange={handleChange}
                        margin="normal"
                        required
                        autoComplete="new-password"
                        InputProps={{
                          endAdornment: (
                            <InputAdornment position="end">
                              <IconButton
                                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                                edge="end"
                              >
                                {showConfirmPassword ? <VisibilityOff /> : <Visibility />}
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
                        {isLoading ? 'Creating Account...' : 'Create Account'}
                      </Button>

                      <Box sx={{ textAlign: 'center', mt: 3 }}>
                        <Typography variant="body2" color="text.secondary">
                          Already have an account?{' '}
                          <Link 
                            to="/login" 
                            style={{ 
                              color: theme.palette.primary.main,
                              textDecoration: 'none',
                              fontWeight: 500,
                            }}
                          >
                            Sign in here
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
    </Box>
  );
};

export default RegisterPage;
