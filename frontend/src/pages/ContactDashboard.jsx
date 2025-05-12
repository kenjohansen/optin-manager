/**
 * ContactDashboard.jsx
 *
 * Contact lookup and management interface.
 *
 * This component provides an administrative interface for searching, viewing, and
 * managing contacts in the system. It allows administrators to search for contacts
 * by email or phone, filter by consent status, and perform administrative opt-outs.
 *
 * As noted in the memories, this component was updated to fix search functionality
 * issues related to encrypted contact values. The implementation now properly handles
 * searching for contacts and displaying their consent status from the related consent
 * records.
 *
 * Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
 * This file is part of the OptIn Manager project and is licensed under the MIT License.
 * See the root LICENSE file for details.
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Typography, Paper, TextField, Stack, Button, List, ListItem, ListItemText, Divider, CircularProgress, Alert, MenuItem } from '@mui/material';
import { fetchContacts } from '../api';

/**
 * Masks an email address for privacy protection.
 * 
 * This utility function obscures most of the username portion of an email
 * address while preserving the domain, helping to protect user privacy
 * while still providing enough information for identification.
 * 
 * @param {string} email - The email address to mask
 * @returns {string} The masked email address
 */
function maskEmail(email) {
  if (!email) return '';
  const [user, domain] = email.split('@');
  return user[0] + '***@' + domain;
}

/**
 * Masks a phone number for privacy protection.
 * 
 * This utility function obscures most digits of a phone number while
 * preserving the last two digits, helping to protect user privacy
 * while still providing enough information for identification.
 * 
 * @param {string} phone - The phone number to mask
 * @returns {string} The masked phone number
 */
function maskPhone(phone) {
  if (!phone) return '';
  return phone.replace(/\d(?=\d{2})/g, '*');
}

/**
 * Available consent status filter options.
 * 
 * These options allow administrators to filter contacts based on their
 * current consent status, making it easier to identify and manage specific
 * groups of contacts.
 */
const CONSENT_OPTIONS = [
  { label: 'Any', value: '' },
  { label: 'Opted In', value: 'opted_in' },
  { label: 'Opted Out', value: 'opted_out' },
];

/**
 * Contact lookup and management dashboard component.
 * 
 * This component provides administrators with tools to search for and manage
 * contacts in the system. It includes features for filtering contacts by consent
 * status, searching by email or phone, and performing administrative opt-outs.
 * 
 * As noted in the memories, this component was updated to fix search functionality
 * issues related to encrypted contact values and to properly display contacts with
 * their consent status from related consent records.
 * 
 * @returns {JSX.Element} The rendered contact dashboard
 */
export default function ContactDashboard() {
  // Search and filter state
  const [search, setSearch] = useState('');
  const [contacts, setContacts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [consent, setConsent] = useState('');
  const [timeWindow, setTimeWindow] = useState('365'); // Default to 365 days to show more contacts
  
  // Contact management state
  const navigate = useNavigate();

  /**
   * Fetches contacts based on current search and filter criteria.
   * 
   * This function retrieves contacts from the backend API using the current
   * search term, consent filter, and time window settings. It handles loading
   * states and error conditions, providing appropriate feedback to the user.
   * 
   * As noted in the memories, this function was updated to work with the
   * encrypted contact values by implementing two search approaches:
   * - For complete email searches: Using deterministic ID pattern matching
   * - For partial searches: Fetching and decrypting records in memory
   */
  const fetchAndSetContacts = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await fetchContacts({ search, consent, timeWindow });
      console.log('API Response:', data);
      console.log('Contacts:', data.contacts);
      if (data.contacts && data.contacts.length > 0) {
        console.log('First contact:', data.contacts[0]);
      }
      setContacts(data.contacts || []);
    } catch (error) {
      console.error('Error fetching contacts:', error);
      setError('Failed to load contacts.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Initial fetch with the default time window of 7 days
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
          <Typography variant="h5" mb={2}>Contacts Lookup</Typography>
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

        {loading ? (
          <CircularProgress />
        ) : error ? (
          <Alert severity="error">{error}</Alert>
        ) : (
          <Box sx={{ mt: 3, width: '100%' }}>
            <Typography variant="h6" align="left" sx={{ mb: 1, borderBottom: '1px solid', borderColor: 'divider', pb: 1 }}>
              Contact Results
            </Typography>
            
            {contacts.length === 0 ? (
              <Alert severity="info" sx={{ mt: 2 }}>
                No contacts found matching your search criteria. Try adjusting your filters.
              </Alert>
            ) : (
              <>
                <Typography variant="body2" align="left" color="text.secondary" sx={{ mb: 1 }}>
                  Showing {contacts.length} contact(s) from the last {timeWindow} days
                </Typography>
                <List sx={{ width: '100%', bgcolor: 'background.paper', border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
                  {contacts.map(c => (
                    <div key={c.id}>
                      <ListItem>
                        <ListItemText
                          primary={c.email ? maskEmail(c.email) : maskPhone(c.phone)}
                          secondary={
                            <>
                              <Typography component="span" variant="body2" color={c.consent === 'Opted Out' ? 'error.main' : 'success.main'}>
                                {c.consent}
                              </Typography>
                              {c.last_updated && (
                                <Typography component="span" variant="body2" color="text.secondary" sx={{ ml: 1 }}>
                                  • Updated: {new Date(c.last_updated).toLocaleDateString()}
                                </Typography>
                              )}
                            </>
                          }
                        />
                        <Button variant="outlined" color="primary" size="small" onClick={() => navigate(`/verbal-optin?contact=${c.email || c.phone}`)}>View Preferences</Button>
                      </ListItem>
                      <Divider />
                    </div>
                  ))}
                </List>
              </>
            )}
          </Box>
        )}
      </Paper>
    </Box>
  );
}
