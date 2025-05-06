import { useState } from 'react';
import { Box, Button, TextField, Typography, Paper, Stack, CircularProgress, Alert, Link } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import { API_BASE } from '../api';
import axios from 'axios';

export default function ForgotPassword() {
  const [username, setUsername] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess(false);
    
    try {
      // Call the password reset endpoint
      await axios.post(`${API_BASE}/auth/reset-password`, { username });
      setSuccess(true);
    } catch (err) {
      console.error('Password reset error:', err);
      setError(err.response?.data?.detail || 'An error occurred. Please try again.');
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
        <Typography variant="h5" mb={2}>Forgot Password</Typography>
        
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        
        {success ? (
          <>
            <Alert severity="success" sx={{ mb: 2 }}>
              If an account with this username exists, a password reset email has been sent.
              Please check your email for further instructions.
            </Alert>
            <Button component={RouterLink} to="/login" variant="contained" color="primary">
              Return to Login
            </Button>
          </>
        ) : (
          <form onSubmit={handleSubmit}>
            <Stack spacing={2}>
              <TextField
                label="Username"
                value={username}
                onChange={e => setUsername(e.target.value)}
                fullWidth
                autoFocus
                required
              />
              <Button type="submit" variant="contained" color="primary" disabled={loading}>
                {loading ? <CircularProgress size={24} /> : 'Reset Password'}
              </Button>
              <Box sx={{ mt: 2 }}>
                <Link component={RouterLink} to="/login" variant="body2">
                  Back to Login
                </Link>
              </Box>
            </Stack>
          </form>
        )}
      </Paper>
    </Box>
  );
}
