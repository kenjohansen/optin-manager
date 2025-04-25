import { useState } from 'react';
import { Typography, Stack, Switch, Button, Alert, CircularProgress, Paper, FormControlLabel, TextField, Box, Divider } from '@mui/material';
import { updateContactPreferences } from '../api';

export default function PreferencesDashboard({ masked, token, preferences, setPreferences }) {
  console.log('PreferencesDashboard received:', { masked, token, preferences });
  
  // Handle case where preferences object is empty or doesn't have programs
  const hasPrograms = preferences && preferences.programs && Array.isArray(preferences.programs);
  
  // Extract contact information from preferences
  const contactInfo = preferences?.contact || {};
  const contactValue = contactInfo.value;
  const contactType = contactInfo.type;
  
  // Extract last comment from preferences
  const lastComment = preferences?.last_comment || '';
  
  // Log the programs received from the backend
  if (hasPrograms) {
    console.log('Programs from backend:', preferences.programs);
    preferences.programs.forEach(program => {
      console.log(`Program ${program.name} (ID: ${program.id}): opted_in=${program.opted_in}`);
    });
  }
  
  // Local preferences for opt-ins - default to empty array if no programs
  const [localPrefs, setLocalPrefs] = useState(
    hasPrograms ? preferences.programs.map(p => ({ ...p })) : []
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [comment, setComment] = useState(lastComment || '');
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
      // Use either token or contact value based on what's available
      await updateContactPreferences({ 
        token, 
        contact: !token ? contactValue : undefined,
        preferences: { programs: localPrefs }, 
        comment 
      });
      
      // Update the parent component state with new preferences
      setPreferences(prev => ({
        ...prev,
        programs: localPrefs
      }));
      
      setSuccess('Preferences updated!');
    } catch (error) {
      console.error('Error updating preferences:', error);
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
      // Use either token or contact value based on what's available
      await updateContactPreferences({ 
        token, 
        contact: !token ? contactValue : undefined,
        preferences: {}, 
        comment, 
        global_opt_out: true 
      });
      
      // Update both the parent component state and local state
      const updatedPrefs = localPrefs.map(p => ({ ...p, opted_in: false }));
      setLocalPrefs(updatedPrefs);
      setPreferences(prev => ({
        ...prev,
        programs: updatedPrefs
      }));
      
      setGlobalSuccess('You have been opted out of all opt-ins.');
    } catch (error) {
      console.error('Error opting out:', error);
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
        width: '100%',
      }}
    >
      <Paper elevation={3} sx={{ p: 3, maxWidth: 600, width: '100%', mx: 'auto' }}>
        <Stack spacing={3}>
          <Typography variant="h6">Manage Your Preferences</Typography>
          <Typography variant="body2">
            Contact: <b>{masked}</b>
          </Typography>
          
          {!hasPrograms && (
            <Alert severity="info">
              No opt-in programs are currently available. This could be because:
              <ul>
                <li>No opt-in programs have been created yet</li>
                <li>There was an issue retrieving your preferences</li>
              </ul>
              If you believe this is an error, please contact support.
            </Alert>
          )}
          
          {hasPrograms && localPrefs.length === 0 && (
            <Alert severity="info">
              You don't have any preferences set up yet. Once programs are available, they will appear here.
            </Alert>
          )}
          
          {localPrefs.map((program, idx) => (
            <Stack key={program.id} direction="row" spacing={2} alignItems="center" sx={{ width: '100%' }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={program.opted_in}
                    onChange={() => handleToggle(idx)}
                    color="primary"
                  />
                }
                label={<Typography variant="body1">{program.name}</Typography>}
                sx={{ flexGrow: 1 }}
              />
              <Typography variant="caption" color="text.secondary">
                {program.last_updated ? `Updated: ${new Date(program.last_updated).toLocaleDateString()}` : ''}
              </Typography>
            </Stack>
          ))}
          
          {localPrefs.length > 0 && (
            <>
              {lastComment && (
                <Alert severity="info" sx={{ mb: 2 }}>
                  <Typography variant="subtitle2">Last update reason:</Typography>
                  <Typography variant="body2">{lastComment}</Typography>
                </Alert>
              )}
              
              <TextField
                label="Reason for changes (optional)"
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                multiline
                rows={2}
                fullWidth
                margin="normal"
                placeholder={lastComment ? "Enter a new reason" : "Why are you making these changes?"}
              />
              
              {error && <Alert severity="error">{error}</Alert>}
              {success && <Alert severity="success">{success}</Alert>}
              
              <Button
                variant="contained"
                onClick={handleSave}
                disabled={loading || localPrefs.length === 0}
              >
                {loading ? <CircularProgress size={24} /> : 'Save Preferences'}
              </Button>
            </>
          )}
          
          <Divider sx={{ my: 2 }} />
          
          <Typography variant="h6">Global Opt-Out</Typography>
          <Typography variant="body2">
            Use this button to opt out of all communications at once.
          </Typography>
          
          {globalError && <Alert severity="error">{globalError}</Alert>}
          {globalSuccess && <Alert severity="success">{globalSuccess}</Alert>}
          
          <Button
            variant="outlined"
            color="error"
            onClick={handleGlobalOptOut}
            disabled={globalLoading}
          >
            {globalLoading ? <CircularProgress size={24} /> : 'Opt Out of Everything'}
          </Button>
        </Stack>
      </Paper>
    </Box>
  );
}
