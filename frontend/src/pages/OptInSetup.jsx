/**
 * OptInSetup.jsx
 *
 * Opt-in program management interface.
 *
 * This component provides an interface for administrators to create, view, and manage
 * opt-in programs (formerly called campaigns/products). It supports creating new
 * opt-in programs, filtering existing ones, and editing program details.
 *
 * As noted in the memories, this page is accessible to both Admin and Support roles,
 * but only Admin users can create or modify opt-in programs. Support users have
 * view-only access. This role-based access control is critical for maintaining
 * proper separation of duties in the system.
 *
 * Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
 * This file is part of the OptIn Manager project and is licensed under the MIT License.
 * See the root LICENSE file for details.
 */

import { Box, Typography, Paper, Button, TextField, Stack, MenuItem, Alert, CircularProgress } from '@mui/material';
import { useState, useEffect } from 'react';
import { createOptIn, fetchOptIns, updateOptIn } from '../api';
import { isAdmin, isSupport, isAuthenticated } from '../utils/auth';

/**
 * Available opt-in program types.
 * 
 * These types categorize opt-in programs based on their purpose and usage:
 * - Promotional: Marketing and promotional communications
 * - Transactional: Essential transaction-related communications
 * - Alert: Time-sensitive notifications and alerts
 * 
 * This categorization helps ensure proper compliance with regulations that
 * treat different types of communications differently.
 */
const OPTIN_TYPES = [
  { label: 'Promotional', value: 'promotional' },
  { label: 'Transactional', value: 'transactional' },
  { label: 'Alert', value: 'alert' }
];

/**
 * Opt-in program management component.
 * 
 * This component provides a comprehensive interface for managing opt-in programs,
 * which define the types of communications that users can consent to receive.
 * It implements role-based access control to ensure that only authorized users
 * can create or modify opt-in programs.
 * 
 * The component includes features for creating new opt-in programs, viewing and
 * filtering existing programs, and editing program details. These capabilities
 * are essential for organizations to maintain compliance with privacy regulations
 * by clearly defining and managing their communication programs.
 * 
 * @returns {JSX.Element} The rendered opt-in setup interface
 */
export default function OptInSetup() {
  const token = localStorage.getItem('access_token');
  const admin = isAdmin(token);
  const support = isSupport(token);
  const authenticated = isAuthenticated(token);
  if (!authenticated) return null;

  // Form state for creating new opt-in programs
  const [name, setName] = useState('');
  const [type, setType] = useState(OPTIN_TYPES[0].value);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  
  // State for existing opt-in programs
  const [optIns, setOptIns] = useState([]);
  const [fetchingOptIns, setFetchingOptIns] = useState(false);
  const [fetchError, setFetchError] = useState('');
  
  // Filtering state for the opt-in programs list
  const [filterName, setFilterName] = useState('');
  const [filterType, setFilterType] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  
  // Inline edit state for modifying existing opt-in programs
  const [editingId, setEditingId] = useState(null);
  const [editingName, setEditingName] = useState('');

  /**
   * Fetches the list of opt-in programs from the API.
   * 
   * This function retrieves all opt-in programs from the backend and updates
   * the component state with the results. It handles loading states and error
   * conditions, providing appropriate feedback to the user.
   */
  const loadOptIns = async () => {
    setFetchingOptIns(true);
    setFetchError('');
    try {
      const data = await fetchOptIns();
      setOptIns(data);
    } catch (err) {
      setFetchError('Failed to fetch opt-ins. Your session may have expired. Please log in again.');
    } finally {
      setFetchingOptIns(false);
    }
  };

  /**
   * Loads opt-in programs when the component mounts.
   * 
   * This effect ensures that the list of opt-in programs is loaded
   * when the component is first rendered, providing users with the
   * most current data without requiring manual refresh.
   */
  useEffect(() => {
    loadOptIns();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess(false);
    try {
      await createOptIn({ name, type });
      setSuccess(true);
      setName('');
      setType(OPTIN_TYPES[0].value);
      await loadOptIns();
    } catch {
      setError('Failed to create opt-in.');
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
      <Paper elevation={3} sx={{ p: 3, width: '90%', mx: 'auto' }}>
        <Typography variant="h4" align="center" mb={3}>
          Opt-In Setup
        </Typography>
        
        {/* Create Opt-In Form */}
        <Box sx={{ width: '100%', mb: 4 }}>
          <form onSubmit={handleSubmit}>
            <Stack spacing={2} direction={{ xs: 'column', sm: 'row' }}>
              <TextField
                label="Name"
                value={name}
                onChange={e => setName(e.target.value)}
                required
                disabled={loading || !admin}
              />
              <TextField
                select
                label="Type"
                value={type}
                onChange={e => setType(e.target.value)}
                required
                disabled={loading || !admin}
              >
                {OPTIN_TYPES.map(opt => (
                  <MenuItem key={opt.value} value={opt.value}>{opt.label}</MenuItem>
                ))}
              </TextField>
              <Button type="submit" variant="contained" color="primary" disabled={loading || !admin}>
                {loading ? <CircularProgress size={24} /> : 'Create'}
              </Button>
            </Stack>
          </form>
          {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
          {success && <Alert severity="success" sx={{ mt: 2 }}>Opt-in created successfully!</Alert>}
        </Box>
        
        {/* Existing Opt-Ins */}
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" mb={2}>Existing Opt-Ins</Typography>
          {/* Filters */}
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} mb={2}>
            <TextField
              label="Filter by Name"
              value={filterName}
              onChange={e => setFilterName(e.target.value)}
              size="small"
            />
            <TextField
              select
              label="Type"
              value={filterType}
              onChange={e => setFilterType(e.target.value)}
              size="small"
              sx={{ minWidth: 120 }}
            >
              <MenuItem value="">All Types</MenuItem>
              {OPTIN_TYPES.map(opt => (
                <MenuItem key={opt.value} value={opt.value}>{opt.label}</MenuItem>
              ))}
            </TextField>
            <TextField
              select
              label="Status"
              value={filterStatus}
              onChange={e => setFilterStatus(e.target.value)}
              size="small"
              sx={{ minWidth: 120 }}
            >
              <MenuItem value="">All Statuses</MenuItem>
              <MenuItem value="active">Active</MenuItem>
              <MenuItem value="paused">Paused</MenuItem>
            </TextField>
          </Stack>
          {fetchingOptIns ? (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="80px">
              <CircularProgress />
            </Box>
          ) : fetchError ? (
            <Alert severity="error">{fetchError}</Alert>
          ) : (
            <Stack spacing={2}>
              {optIns
                .filter(optin =>
                  (!filterName || optin.name.toLowerCase().includes(filterName.toLowerCase())) &&
                  (!filterType || optin.type === filterType) &&
                  (!filterStatus || optin.status === filterStatus)
                )
                .map(optin => (
                  <Paper key={optin.id} sx={{ p: 2, display: 'flex', alignItems: 'center' }}>
                    {editingId === optin.id ? (
                      <Box sx={{ flexGrow: 1 }}>
                        <TextField
                          value={editingName}
                          onChange={e => setEditingName(e.target.value)}
                          size="small"
                          fullWidth
                          autoFocus
                          onBlur={async () => {
                            try {
                              await updateOptIn({ id: optin.id, name: editingName });
                              setEditingId(null);
                              await loadOptIns();
                            } catch {
                              setError('Failed to update opt-in name.');
                              setEditingId(null);
                            }
                          }}
                          onKeyDown={e => {
                            if (e.key === 'Enter') {
                              e.target.blur();
                            } else if (e.key === 'Escape') {
                              setEditingId(null);
                            }
                          }}
                        />
                      </Box>
                    ) : (
                      <Box sx={{ flexGrow: 1 }}>
                        <Typography variant="subtitle1" component="div">
                          {optin.name}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {OPTIN_TYPES.find(t => t.value === optin.type)?.label || optin.type}
                          {' • '}
                          <span style={{ color: optin.status === 'active' ? 'green' : 'orange' }}>
                            {optin.status === 'active' ? 'Active' : 'Paused'}
                          </span>
                        </Typography>
                      </Box>
                    )}
                    <Box sx={{ display: 'flex', width: '180px', justifyContent: 'flex-end' }}>
                      {admin && (
                        <Button
                          variant="outlined"
                          size="small"
                          color="primary"
                          onClick={() => {
                            setEditingId(optin.id);
                            setEditingName(optin.name);
                          }}
                          sx={{ mr: 1 }}
                          disabled={editingId === optin.id}
                        >
                          Edit
                        </Button>
                      )}
                      {admin && (
                        <Button
                          variant="outlined"
                          size="small"
                          color={optin.status === 'active' ? 'warning' : 'success'}
                          onClick={async () => {
                            try {
                              await updateOptIn({ id: optin.id, status: optin.status === 'active' ? 'paused' : 'active' });
                              await loadOptIns();
                            } catch {
                              setError('Failed to update opt-in status.');
                            }
                          }}
                        >
                          {optin.status === 'active' ? 'Pause' : 'Activate'}
                        </Button>
                      )}
                    </Box>
                  </Paper>
                ))}
            </Stack>
          )}
        </Paper>
      </Paper>
    </Box>
  );
}
