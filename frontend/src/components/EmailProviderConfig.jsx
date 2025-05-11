import React, { useState, useEffect } from 'react';
import { Box, TextField, Button, FormControl, InputLabel, Select, MenuItem, Alert } from '@mui/material';
import { testProviderConnection, setProviderSecret, deleteProviderSecret, getSecretsStatus } from '../api/providerSecrets';

/**
 * Email Provider Configuration Component
 * Handles the configuration, testing, and deletion of email provider settings
 */
function EmailProviderConfig({ provider: initialProvider = 'aws_ses' }) {
  // Local state for provider configuration
  const [provider, setProvider] = useState(initialProvider);
  const [accessKey, setAccessKey] = useState('');
  const [secretKey, setSecretKey] = useState('');
  const [fromAddress, setFromAddress] = useState('');
  const [region, setRegion] = useState('us-east-1');
  
  // UI state
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [error, setError] = useState('');
  const [testResult, setTestResult] = useState('');
  
  // Status state
  const [configured, setConfigured] = useState(false);
  const [status, setStatus] = useState('untested');
  
  // Fetch initial status
  useEffect(() => {
    fetchStatus();
  }, []);
  
  // Fetch the current status from the backend
  const fetchStatus = async () => {
    try {
      const statusData = await getSecretsStatus();
      setConfigured(statusData.email_configured || false);
      setStatus(statusData.email_status || 'untested');
      
      // If configured, fetch the credentials
      if (statusData.email_configured) {
        // We can't fetch the actual credentials for security reasons,
        // but we can show that they exist
        setAccessKey('********');
        setSecretKey('********');
      }
    } catch (error) {
      console.error('Error fetching email provider status:', error);
    }
  };

  /**
   * Handle provider selection change
   */
  const handleProviderChange = (e) => {
    setProvider(e.target.value);
  };

  /**
   * Save email provider credentials
   */
  const handleSave = async () => {
    setSaving(true);
    setError(null);
    
    try {
      // Validate required fields
      const credentials = {
        providerType: 'email',
        accessKey,
        secretKey,
        region,
        fromAddress
      };
      
      // Save directly to the backend
      await setProviderSecret(credentials);
      
      // Update status
      setConfigured(true);
      setStatus('untested'); // Reset test status when new credentials are saved
      setTestResult('');
      
      // Store in localStorage as a backup
      localStorage.setItem('email_configured', 'true');
      localStorage.setItem('email_tested', 'false');
    } catch (error) {
      console.error('Error saving email provider credentials:', error);
      setError(error.response?.data?.detail || error.message || 'Failed to save credentials');
    } finally {
      setSaving(false);
    }
  };

  /**
   * Handle test connection button click
   */
  const handleTest = async () => {
    setTesting(true);
    setTestResult('');
    setError('');
    
    try {
      // Call the API to test the connection
      const result = await testProviderConnection({ providerType: 'email' });
      setTestResult(result.message || 'Connection successful');
      
      // Update status
      setStatus('tested');
      localStorage.setItem('email_tested', 'true');
      
      // Refresh status from backend
      fetchStatus();
    } catch (error) {
      console.error('Error testing email provider connection:', error);
      setError(error.response?.data?.detail || error.message || 'Connection test failed');
      setStatus('failed');
      localStorage.setItem('email_tested', 'false');
    } finally {
      setTesting(false);
    }
  };

  /**
   * Handle delete credentials button click
   */
  const handleDelete = async () => {
    setSaving(true);
    setError('');
    
    try {
      // Call the API to delete the credentials
      await deleteProviderSecret({ providerType: 'email' });
      
      // Reset form fields
      setAccessKey('');
      setSecretKey('');
      setFromAddress('');
      setRegion('us-east-1');
      setTestResult('');
      
      // Update status
      setConfigured(false);
      setStatus('untested');
      
      // Clear localStorage
      localStorage.removeItem('email_configured');
      localStorage.removeItem('email_tested');
      
      // Refresh status from backend
      fetchStatus();
    } catch (error) {
      console.error('Error deleting email provider credentials:', error);
      setError(error.response?.data?.detail || error.message || 'Failed to delete credentials');
    } finally {
      setSaving(false);
    }
  };

  return (
    <Box sx={{ mb: 4 }} data-testid="email-provider-section">
      <h3>Email Provider Configuration</h3>
      
      {/* Status indicators */}
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <Box sx={{ mr: 2, fontWeight: 'bold' }}>Status:</Box>
        {configured ? (
          <Alert severity="success" sx={{ py: 0 }}>
            Configured
          </Alert>
        ) : (
          <Alert severity="warning" sx={{ py: 0 }}>
            Not Configured
          </Alert>
        )}
        {configured && (
          <Alert 
            severity={status === 'tested' ? 'success' : status === 'failed' ? 'error' : 'info'} 
            sx={{ ml: 1, py: 0 }}
          >
            {status === 'tested' ? 'Tested' : 
             status === 'failed' ? 'Test Failed' : 'Not Tested'}
          </Alert>
        )}
      </Box>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      {testResult && (
        <Alert severity="success" sx={{ mb: 2 }}>
          {testResult}
        </Alert>
      )}
      
      <FormControl fullWidth sx={{ mb: 2 }}>
        <InputLabel>Email Provider</InputLabel>
        <Select
          value={provider || ''}
          onChange={handleProviderChange}
          data-testid="email-provider-select"
        >
          <MenuItem value="aws_ses">AWS SES</MenuItem>
          <MenuItem value="aws_sns">AWS SNS</MenuItem>
        </Select>
      </FormControl>
      
      <TextField
        label="Access Key"
        value={accessKey}
        onChange={(e) => setAccessKey(e.target.value)}
        fullWidth
        margin="normal"
        data-testid="email-access-key-input"
      />
      
      <TextField
        label="Secret Key"
        value={secretKey}
        onChange={(e) => setSecretKey(e.target.value)}
        fullWidth
        margin="normal"
        type="password"
        data-testid="email-secret-key-input"
      />
      
      <TextField
        label="From Address"
        value={fromAddress}
        onChange={(e) => setFromAddress(e.target.value)}
        fullWidth
        margin="normal"
        data-testid="email-from-address-input"
      />
      
      <TextField
        label="Region"
        value={region}
        onChange={(e) => setRegion(e.target.value)}
        fullWidth
        margin="normal"
        data-testid="email-region-input"
      />
      
      <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
        <Button 
          variant="contained" 
          onClick={handleSave}
          disabled={saving}
          data-testid="save-email-button"
        >
          {saving ? 'Saving...' : 'Save'}
        </Button>
        
        <Button 
          variant="outlined" 
          onClick={handleTest}
          disabled={testing || !configured}
          data-testid="test-email-button"
        >
          {testing ? 'Testing...' : 'Test'}
        </Button>
        
        <Button 
          variant="outlined" 
          color="error" 
          onClick={handleDelete}
          disabled={!configured}
          data-testid="delete-email-button"
        >
          Delete
        </Button>
      </Box>
    </Box>
  );
}

export default EmailProviderConfig;
