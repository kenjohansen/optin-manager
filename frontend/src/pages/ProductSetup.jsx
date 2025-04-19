import { Box, Typography, Paper, Button, TextField, Stack, Alert, CircularProgress } from '@mui/material';
import { useState } from 'react';
import { createProduct } from '../api';

export default function ProductSetup() {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess(false);
    try {
      await createProduct({ name, description });
      setSuccess(true);
      setName('');
      setDescription('');
    } catch {
      setError('Failed to create product.');
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
      <Paper elevation={3} sx={{ p: 3, minWidth: 350, maxWidth: 650, width: '100%', mx: 'auto', textAlign: 'center' }}>
        <Typography variant="h6" gutterBottom>Create Product/Service</Typography>
        {error && <Alert severity="error">{error}</Alert>}
        {success && <Alert severity="success">Product created!</Alert>}
        <form onSubmit={handleSubmit}>
          <Stack spacing={2}>
            <TextField
              label="Product/Service Name"
              value={name}
              onChange={e => setName(e.target.value)}
              fullWidth
              required
              disabled={loading}
            />
            <TextField
              label="Description"
              value={description}
              onChange={e => setDescription(e.target.value)}
              fullWidth
              multiline
              minRows={2}
              disabled={loading}
            />
            <Button type="submit" variant="contained" color="primary" disabled={loading}>
              {loading ? <CircularProgress size={24} /> : 'Create'}
            </Button>
          </Stack>
        </form>
      </Paper>
    </Box>
  );
}
