import React, { useState } from 'react';
import { Button, Box, Typography } from '@mui/material';
import { useAuth } from '../contexts/AuthContext';

const DebugLogin: React.FC = () => {
  const { login, user, error, isLoading } = useAuth();
  const [status, setStatus] = useState<string>('');

  const testLogin = async () => {
    setStatus('Testing login...');
    try {
      console.log('DebugLogin: Starting test login');
      await login('aditya@test.com', 'Aditya@2004');
      console.log('DebugLogin: Login completed successfully');
      setStatus('Login successful!');
    } catch (error: any) {
      console.error('DebugLogin: Login failed:', error);
      setStatus(`Login failed: ${error.message || 'Unknown error'}`);
    }
  };

  return (
    <Box sx={{ p: 3, border: '1px solid #ccc', m: 2 }}>
      <Typography variant="h6">Debug Login Component</Typography>
      <Typography>User: {user ? JSON.stringify(user, null, 2) : 'Not logged in'}</Typography>
      <Typography>Error: {error || 'None'}</Typography>
      <Typography>Loading: {isLoading ? 'Yes' : 'No'}</Typography>
      <Typography>Status: {status}</Typography>
      <Button onClick={testLogin} variant="contained" sx={{ mt: 2 }}>
        Test Login
      </Button>
    </Box>
  );
};

export default DebugLogin;
