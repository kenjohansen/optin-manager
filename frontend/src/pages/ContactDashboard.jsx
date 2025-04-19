import { useState, useEffect } from 'react';
import { Box, Typography, Paper, TextField, Stack, Button, List, ListItem, ListItemText, Divider, CircularProgress, Alert, MenuItem } from '@mui/material';
import { fetchContacts, optOutById } from '../api';

// Utility to mask PII
function maskEmail(email) {
  if (!email) return '';
  const [user, domain] = email.split('@');
  return user[0] + '***@' + domain;
}
function maskPhone(phone) {
  if (!phone) return '';
  return phone.replace(/\d(?=\d{2})/g, '*');
}

const CONSENT_OPTIONS = [
  { label: 'Any', value: '' },
  { label: 'Opted In', value: 'opted_in' },
  { label: 'Opted Out', value: 'opted_out' },
];

export default function ContactDashboard() {
  const [search, setSearch] = useState('');
  const [contacts, setContacts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [consent, setConsent] = useState('');
  const [timeWindow, setTimeWindow] = useState('');
  // Added missing state for runtime errors
  const [prefDialogId, setPrefDialogId] = useState(null);
  const [optOutLoadingId, setOptOutLoadingId] = useState(null);
  const [optOutError, setOptOutError] = useState('');
  const [optOutSuccess, setOptOutSuccess] = useState('');

  const fetchAndSetContacts = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await fetchContacts({ search, consent, timeWindow });
      setContacts(data.contacts || []);
    } catch {
      setError('Failed to load contacts.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAndSetContacts();
    // eslint-disable-next-line
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    fetchAndSetContacts();
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
      <Paper elevation={3} sx={{ p: 3, maxWidth: 600, width: '100%', mx: 'auto', textAlign: 'center' }}>
          <Typography variant="h5" mb={2}>Contact Dashboard</Typography>
        <Typography variant="caption" color="text.secondary" mb={2}>
          For compliance, all contact info is masked. No names or unmasked PII are ever shown.
        </Typography>
        <form onSubmit={handleSearch}>
          <Stack direction="row" spacing={2} mb={2}>
            <TextField
              label="Search by Email or Phone"
              value={search}
              onChange={e => setSearch(e.target.value)}
              fullWidth
            />
            <TextField
              select
              label="Consent Status"
              value={consent}
              onChange={e => setConsent(e.target.value)}
              sx={{ minWidth: 140 }}
            >
              {CONSENT_OPTIONS.map(opt => (
                <MenuItem key={opt.value} value={opt.value}>{opt.label}</MenuItem>
              ))}
            </TextField>
            <TextField
              label="Time Window (days)"
              type="number"
              value={timeWindow}
              onChange={e => setTimeWindow(e.target.value)}
              sx={{ minWidth: 140 }}
            />
            <Button type="submit" variant="contained">Search</Button>
          </Stack>
        </form>
        {optOutError && <Alert severity="error">{optOutError}</Alert>}
        {optOutSuccess && <Alert severity="success">{optOutSuccess}</Alert>}
        {loading ? (
          <CircularProgress />
        ) : error ? (
          <Alert severity="error">{error}</Alert>
        ) : (
          <List>
            {contacts.map(c => (
              <div key={c.id}>
                <ListItem>
                  <ListItemText
                    primary={c.email ? maskEmail(c.email) : maskPhone(c.phone)}
                    secondary={`Consent: ${c.consent}`}
                  />
                  <Button variant="outlined" color="primary" size="small" sx={{ mr: 1 }} onClick={() => setPrefDialogId(c.id)}>Preferences</Button>
                  <Button
                    variant="outlined"
                    color="error"
                    size="small"
                    disabled={optOutLoadingId === c.id}
                    onClick={async () => {
                      setOptOutLoadingId(c.id);
                      setOptOutError('');
                      setOptOutSuccess('');
                      try {
                        await optOutById(c.id);
                        setContacts(contacts => contacts.map(contact => contact.id === c.id ? { ...contact, consent: 'Opted Out' } : contact));
                        setOptOutSuccess('Contact opted out.');
                      } catch {
                        setOptOutError('Failed to opt out contact.');
                      } finally {
                        setOptOutLoadingId(null);
                      }
                    }}
                  >
                    {optOutLoadingId === c.id ? <CircularProgress size={18} /> : 'Opt-Out'}
                  </Button>
                </ListItem>
                <Divider />
              </div>
            ))}
          </List>
        )}
      </Paper>
    </Box>
  );
}
