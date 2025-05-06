import { useState } from 'react';
import { Box, Button, TextField, Typography, Paper, Stack, CircularProgress, Alert, Link } from '@mui/material';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import { login } from '../api';

export default function AdminLogin() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

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
