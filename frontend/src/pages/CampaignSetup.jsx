import { Box, Typography, Paper, Button, TextField, Stack, MenuItem, Alert, CircularProgress } from '@mui/material';
import { useState, useEffect } from 'react';
import { createCampaign, fetchCampaigns } from '../api';
import { isAdmin, isSupport, isAuthenticated } from '../utils/auth';

const CAMPAIGN_TYPES = [
  { label: 'Promotional', value: 'promotional' },
  { label: 'Transactional', value: 'transactional' },
  { label: 'Alert', value: 'alert' }
];

export default function CampaignSetup() {
  const token = localStorage.getItem('access_token');
  const admin = isAdmin(token);
  const support = isSupport(token);
  const authenticated = isAuthenticated(token);
  if (!authenticated) return null; // Optionally redirect to login

  const [name, setName] = useState('');
  const [type, setType] = useState(CAMPAIGN_TYPES[0].value);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [campaigns, setCampaigns] = useState([]);
  const [fetchingCampaigns, setFetchingCampaigns] = useState(true);
  const [fetchError, setFetchError] = useState('');

  const loadCampaigns = async () => {
    setFetchingCampaigns(true);
    setFetchError('');
    try {
      const data = await fetchCampaigns();
      setCampaigns(data);
    } catch (err) {
      console.log('Failed to fetch campaigns:', err);
      setFetchError('Failed to fetch campaigns. Your session may have expired. Please log in again.');
    } finally {
      setFetchingCampaigns(false);
    }
  };

  useEffect(() => {
    loadCampaigns();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess(false);
    try {
      await createCampaign({ name, type });
      setSuccess(true);
      setName('');
      setType(CAMPAIGN_TYPES[0].value);
      await loadCampaigns();
    } catch {
      setError('Failed to create campaign.');
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
        <Typography variant="h5" gutterBottom sx={{ mb: 4, textAlign: 'center' }}>Campaign Management</Typography>
        <Box sx={{ p: { xs: 2, sm: 4 }, width: '100%' }}>
          {error && <Alert severity="error">{error}</Alert>}
          {success && <Alert severity="success">Campaign created!</Alert>}
          {admin && (
            <form onSubmit={handleSubmit}>
              <Stack spacing={2}>
                <TextField
                  label="Campaign Name"
                  value={name}
                  onChange={e => setName(e.target.value)}
                  fullWidth
                  required
                  disabled={loading}
                />
                <TextField
                  select
                  label="Campaign Type"
                  value={type}
                  onChange={e => setType(e.target.value)}
                  fullWidth
                  disabled={loading}
                >
                  {CAMPAIGN_TYPES.map(opt => (
                    <MenuItem key={opt.value} value={opt.value}>{opt.label}</MenuItem>
                  ))}
                </TextField>
                <Button type="submit" variant="contained" color="primary" disabled={loading}>
                  {loading ? <CircularProgress size={24} /> : 'Create'}
                </Button>
              </Stack>
            </form>
          )}
        </Box>
        <Box sx={{ width: '100%', maxWidth: 600, mt: 4, mx: 'auto' }}>
          <Typography variant="h6" mb={2} sx={{ textAlign: 'center' }}>Existing Campaigns</Typography>
          {fetchingCampaigns ? (
            <CircularProgress />
          ) : fetchError ? (
            <Alert severity="error">{fetchError}</Alert>
          ) : campaigns.length === 0 ? (
            <Typography color="text.secondary">No campaigns found.</Typography>
          ) : (
            <Paper elevation={1} sx={{ p: 2 }}>
              {campaigns.map((c) => (
                <Box key={c.id} display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                  <Box display="flex" alignItems="center" gap={1}>
                    {admin && c.status !== 'closed' ? (
                      <TextField
                        size="small"
                        value={c._editingName ?? c.name}
                        onChange={e => {
                          setCampaigns(prev => prev.map(x => x.id === c.id ? { ...x, _editingName: e.target.value } : x));
                        }}
                        onBlur={async e => {
                          if ((c._editingName ?? c.name) !== c.name) {
                            try {
                              await updateCampaign({ id: c.id, name: c._editingName });
                              await loadCampaigns();
                            } catch {
                              setError('Failed to update campaign name.');
                            }
                          }
                        }}
                        onKeyDown={async e => {
                          if (e.key === 'Enter') {
                            e.target.blur();
                          }
                        }}
                      />
                    ) : (
                      <Typography>{c.name}</Typography>
                    )}
                    <Typography color="text.secondary" ml={2}>{c.type}</Typography>
                    <Typography color={c.status === 'closed' ? 'error' : 'text.secondary'} ml={2}>
                      {c.status.charAt(0).toUpperCase() + c.status.slice(1)}
                    </Typography>
                  </Box>
                  {admin && c.status !== 'closed' && (
                    <Button
                      size="small"
                      variant="outlined"
                      color="error"
                      onClick={async () => {
                        try {
                          await updateCampaign({ id: c.id, status: 'closed' });
                          await loadCampaigns();
                        } catch {
                          setError('Failed to close campaign.');
                        }
                      }}
                    >
                      Close
                    </Button>
                  )}
                </Box>
              ))}
            </Paper>
          )}
        </Box>
      </Paper>
    </Box>
  );
}
