import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import { CssBaseline, GlobalStyles } from '@mui/material';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { SnackbarProvider } from 'notistack';

import theme from './theme';
import { AuthProvider } from './contexts/AuthContext';
import Layout from './components/Layout/Layout';
import LoginPage from './pages/Auth/LoginPage';
import RegisterPage from './pages/Auth/RegisterPage';
import DashboardPage from './pages/Dashboard/DashboardPage';
import LibraryPage from './pages/Library/LibraryPage';
import BookDetailsPage from './pages/Books/BookDetailsPage';
import MyLoansPage from './pages/Loans/MyLoansPage';
import ProfilePage from './pages/Profile/ProfilePage';
import AdminDashboard from './pages/Admin/AdminDashboard';
import UserManagement from './pages/Admin/UserManagement';
import BookManagement from './pages/Admin/BookManagement';
import LoanManagement from './pages/Admin/LoanManagement';
import Analytics from './pages/Admin/Analytics';
import ProtectedRoute from './components/Auth/ProtectedRoute';
import { UserRole } from './types';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

const globalStyles = (
  <GlobalStyles
    styles={{
      '*': {
        boxSizing: 'border-box',
      },
      html: {
        height: '100%',
      },
      body: {
        height: '100%',
        margin: 0,
        background: 'linear-gradient(135deg, #FAFAFA 0%, #F5F5F5 100%)',
        fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
      },
      '#root': {
        height: '100%',
      },
      // Custom scrollbar
      '::-webkit-scrollbar': {
        width: '8px',
      },
      '::-webkit-scrollbar-track': {
        background: '#f1f1f1',
        borderRadius: '4px',
      },
      '::-webkit-scrollbar-thumb': {
        background: 'linear-gradient(135deg, #FF6B35 0%, #FF8A50 100%)',
        borderRadius: '4px',
      },
      '::-webkit-scrollbar-thumb:hover': {
        background: 'linear-gradient(135deg, #E65100 0%, #F4511E 100%)',
      },
    }}
  />
);

const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        {globalStyles}
        <SnackbarProvider 
          maxSnack={3}
          anchorOrigin={{
            vertical: 'bottom',
            horizontal: 'right',
          }}
          autoHideDuration={3000}
        >
          <AuthProvider>
            <Router>
              <Routes>
                {/* Auth Routes */}
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />
                
                {/* Protected Routes */}
                <Route
                  path="/*"
                  element={
                    <ProtectedRoute>
                      <Layout>
                        <Routes>
                          <Route path="/" element={<Navigate to="/dashboard" replace />} />
                          <Route path="/dashboard" element={<DashboardPage />} />
                          <Route path="/library" element={<LibraryPage />} />
                          <Route path="/books/:id" element={<BookDetailsPage />} />
                          <Route path="/my-loans" element={<MyLoansPage />} />
                          <Route path="/profile" element={<ProfilePage />} />
                          
                          {/* Admin/Librarian Routes */}
                          <Route
                            path="/admin/*"
                            element={
                              <ProtectedRoute allowedRoles={[UserRole.ADMIN, UserRole.LIBRARIAN]}>
                                <Routes>
                                  <Route path="/" element={<AdminDashboard />} />
                                  <Route path="/users" element={<UserManagement />} />
                                  <Route path="/books" element={<BookManagement />} />
                                  <Route path="/loans" element={<LoanManagement />} />
                                </Routes>
                              </ProtectedRoute>
                            }
                          />
                          
                          {/* Fallback */}
                          <Route path="*" element={<Navigate to="/dashboard" replace />} />
                        </Routes>
                      </Layout>
                    </ProtectedRoute>
                  }
                />
              </Routes>
            </Router>
          </AuthProvider>
        </SnackbarProvider>
      </ThemeProvider>
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
};

export default App;
