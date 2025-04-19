import { Box, Typography, Paper, Grid, CircularProgress, Alert } from '@mui/material';
import { useEffect, useState } from 'react';
import { fetchDashboardStats } from '../api';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    setLoading(true);
    fetchDashboardStats()
      .then(data => {
        setStats(data);
        setLoading(false);
      })
      .catch(() => {
        setError('Failed to load dashboard stats.');
        setLoading(false);
      });
  }, []);

  if (loading) return <Box p={4}><CircularProgress /></Box>;
  if (error) return <Box p={4}><Alert severity="error">{error}</Alert></Box>;

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
      <Typography variant="h4" gutterBottom sx={{ mb: 4, textAlign: 'center' }}>Admin Dashboard</Typography>
      <Box sx={{ display: 'flex', gap: 4, flexWrap: 'wrap', justifyContent: 'center', maxWidth: 900, width: '100%', mx: 'auto' }}>
        <Paper elevation={3} sx={{ p: 3, minWidth: 250, textAlign: 'center' }}>
          <Typography variant="h6">Total Contacts</Typography>
          <Typography variant="h4">{stats?.total_contacts ?? 0}</Typography>
        </Paper>
        <Paper elevation={3} sx={{ p: 3, minWidth: 250, textAlign: 'center' }}>
          <Typography variant="h6">Active Campaigns</Typography>
          <Typography variant="h4">{stats?.active_campaigns ?? 0}</Typography>
        </Paper>
        <Paper elevation={3} sx={{ p: 3, minWidth: 250, textAlign: 'center' }}>
          <Typography variant="h6">Opt-Outs (30d)</Typography>
          <Typography variant="h4">{stats?.opt_outs ?? 0}</Typography>
        </Paper>
      </Box>
    </Box>
  );
}
