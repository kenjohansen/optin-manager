import { useState } from 'react';
import { Typography, Stack, Switch, Button, Alert, CircularProgress, Paper, FormControlLabel, TextField } from '@mui/material';
import { updateContactPreferences } from '../api';

export default function PreferencesDashboard({ masked, contact, preferences, setPreferences }) {
  // Local preferences for opt-ins
const [localPrefs, setLocalPrefs] = useState(preferences.programs.map(p => ({ ...p })));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [comment, setComment] = useState('');
  const [globalLoading, setGlobalLoading] = useState(false);
  const [globalSuccess, setGlobalSuccess] = useState('');
  const [globalError, setGlobalError] = useState('');

  const handleToggle = idx => {
    setLocalPrefs(prefs =>
      prefs.map((p, i) => i === idx ? { ...p, opted_in: !p.opted_in } : p)
    );
    setSuccess('');
    setError('');
  };

  const handleSave = async () => {
    setLoading(true);
    setError('');
    setSuccess('');
    try {
      await updateContactPreferences({ contact, preferences: { programs: localPrefs }, comment });
      setPreferences({ programs: localPrefs });
      setSuccess('Preferences updated!');
    } catch {
      setError('Failed to update preferences.');
    } finally {
      setLoading(false);
    }
  };

  const handleGlobalOptOut = async () => {
    setGlobalLoading(true);
    setGlobalError('');
    setGlobalSuccess('');
    try {
      await updateContactPreferences({ contact, preferences: {}, comment, global_opt_out: true });
      setPreferences({ programs: localPrefs.map(p => ({ ...p, opted_in: false })) });
      setGlobalSuccess('You have been opted out of all opt-ins.');
    } catch {
      setGlobalError('Failed to opt out of everything.');
    } finally {
      setGlobalLoading(false);
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
      <Paper elevation={3} sx={{ p: 3, minWidth: 350, maxWidth: 600, width: '100%', mx: 'auto', textAlign: 'center' }}>
        <Stack spacing={2}>
        <Typography variant="subtitle1">Manage Preferences for <b>{masked}</b></Typography>
        {localPrefs.map((p, idx) => (
          <FormControlLabel
            key={p.id}
            control={
              <Switch
                checked={p.opted_in}
                onChange={() => handleToggle(idx)}
                color="primary"
                disabled={globalLoading}
              />
            }
            label={p.name}
          />
        ))}
        <TextField
          label="Optional Comment (saved with your record)"
          value={comment}
          onChange={e => setComment(e.target.value)}
          multiline
          minRows={2}
          disabled={globalLoading || loading}
        />
        {error && <Alert severity="error">{error}</Alert>}
        {success && <Alert severity="success">{success}</Alert>}
        {globalError && <Alert severity="error">{globalError}</Alert>}
        {globalSuccess && <Alert severity="success">{globalSuccess}</Alert>}
        <Stack direction="row" spacing={2}>
          <Button variant="contained" onClick={handleSave} disabled={loading || globalLoading}>
            {loading ? <CircularProgress size={24} /> : 'Save Opt-ins'}
          </Button>
          <Button variant="outlined" color="error" onClick={handleGlobalOptOut} disabled={globalLoading || loading}>
          {globalLoading ? <CircularProgress size={24} /> : 'Opt Out of All Opt-ins'}
        </Button>
        </Stack>
      </Stack>
      </Paper>
    </Box>
  );
}
