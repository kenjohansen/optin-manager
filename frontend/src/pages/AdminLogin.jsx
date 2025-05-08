/**
 * AdminLogin.jsx
 *
 * Authentication page for admin and support users.
 *
 * This component provides the login interface for authenticated users (admin and
 * support roles). It handles credential validation, error handling, and redirects
 * authenticated users to the dashboard upon successful login.
 *
 * As noted in the memories, the system supports two roles for authenticated users:
 * - Admin: Can create campaigns, products, and manage authenticated users
 * - Support: Can view all pages but cannot create campaigns/products or manage users
 *
 * This login page is the entry point for these authenticated users to access
 * their role-specific functionality.
 *
 * Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
 * This file is part of the OptIn Manager project and is licensed under the MIT License.
 * See the root LICENSE file for details.
 */

import { useState } from 'react';
import { Box, Button, TextField, Typography, Paper, Stack, CircularProgress, Alert, Link } from '@mui/material';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import { login } from '../api';

/**
 * Admin login page component.
 * 
 * This component renders a login form for authenticated users (admin and support
 * roles) to access the application. It handles form submission, authentication via
 * the API, and stores the JWT token upon successful login. The component also
 * provides error handling and feedback during the authentication process.
 * 
 * @returns {JSX.Element} The rendered login page
 */
export default function AdminLogin() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  /**
   * Handles form submission and authentication.
   * 
   * This function processes the login form submission, validates credentials
   * through the API, and handles the authentication flow. Upon successful
   * authentication, it stores the JWT token in local storage and redirects
   * the user to the dashboard. It also handles error cases and provides
   * appropriate feedback.
   * 
   * @param {React.FormEvent} e - The form submission event
   */
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      console.log('Attempting login with username:', username);
      const data = await login({ username, password });
      console.log('Login response:', data);
      if (!data.access_token) {
        console.warn('No access_token in response:', data);
        setError('Login succeeded but no access token returned.');
        return;
      }
      localStorage.setItem('access_token', data.access_token);
      navigate('/dashboard');
    } catch (err) {
      console.error('Login error:', err);
      setError('Invalid credentials or server error.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: 'calc(100vh - 64px - 48px)',
        bgcolor: 'background.default',
        py: 4,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'flex-start',
        width: '100vw',
      }}
    >
      <Paper elevation={3} sx={{ p: 4, minWidth: 350, maxWidth: 600, width: '100%', mx: 'auto', textAlign: 'center' }}>
        <Typography variant="h5" mb={2}>Admin Login</Typography>
        {error && <Alert severity="error">{error}</Alert>}
        <form onSubmit={handleSubmit}>
          <Stack spacing={2}>
            <TextField
              label="Username"
              value={username}
              onChange={e => setUsername(e.target.value)}
              fullWidth
              autoFocus
            />
            <TextField
              label="Password"
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              fullWidth
            />
            <Button type="submit" variant="contained" color="primary" disabled={loading}>
              {loading ? <CircularProgress size={24} /> : 'Login'}
            </Button>
            <Box sx={{ mt: 2, textAlign: 'right' }}>
              <Link component={RouterLink} to="/forgot-password" variant="body2">
                Forgot password?
              </Link>
            </Box>
          </Stack>
        </form>
      </Paper>
    </Box>
  );
}
