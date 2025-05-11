import React, { useState, useEffect } from 'react';
import { Box, TextField, Button, FormControl, InputLabel, Select, MenuItem, Alert } from '@mui/material';
import { testProviderConnection, setProviderSecret, deleteProviderSecret, getSecretsStatus } from '../api/providerSecrets';

/**
 * SMS Provider Configuration Component
 * Handles the configuration, testing, and deletion of SMS provider settings
 */
function SmsProviderConfig({ provider: initialProvider = 'aws_sns' }) {
  // Local state for provider configuration
  const [provider, setProvider] = useState(initialProvider);
  const [accessKey, setAccessKey] = useState('');
  const [secretKey, setSecretKey] = useState('');
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
      setConfigured(statusData.sms_configured || false);
      setStatus(statusData.sms_status || 'untested');
      
      // If configured, fetch the credentials
      if (statusData.sms_configured) {
        // We can't fetch the actual credentials for security reasons,
        // but we can show that they exist
        setAccessKey('********');
        setSecretKey('********');
      }
    } catch (error) {
      console.error('Error fetching SMS provider status:', error);
    }
  };

  /**
   * Handle provider selection change
   */
  const handleProviderChange = (e) => {
    setProvider(e.target.value);
  };

  /**
   * Save SMS provider credentials
   */
  const handleSave = async () => {
    if (!accessKey || !secretKey) {
      setError('Access key and secret key are required');
      return;
    }
    
    setSaving(true);
    setError('');
    
    try {
      // Prepare credentials object
      const credentials = {
        providerType: 'sms',
        accessKey,
        secretKey,
        region
      };
      
      // Save directly to the backend
      await setProviderSecret(credentials);
      
      // Update status
      setConfigured(true);
      setStatus('untested'); // Reset test status when new credentials are saved
      setTestResult('');
      
      // Store in localStorage as a backup
      localStorage.setItem('sms_configured', 'true');
      localStorage.setItem('sms_tested', 'false');
      
      // Refresh status from backend
      fetchStatus();
    } catch (error) {
      console.error('Error saving SMS provider credentials:', error);
      setError(error.response?.data?.detail || error.message || 'Failed to save credentials');
    } finally {
      setSaving(false);
    }
  };

  /**
   * Test SMS provider connection
   */
  const handleTest = async () => {
    setTesting(true);
    setTestResult('');
    setError('');
    
    try {
      // Call the API to test the connection
      const result = await testProviderConnection({ providerType: 'sms' });
      setTestResult(result.message || 'Connection successful');
      
      // Update status
      setStatus('tested');
      localStorage.setItem('sms_tested', 'true');
      
      // Refresh status from backend
      fetchStatus();
    } catch (error) {
      console.error('Error testing SMS provider connection:', error);
      setError(error.response?.data?.detail || error.message || 'Connection test failed');
      setStatus('failed');
      localStorage.setItem('sms_tested', 'false');
    } finally {
      setTesting(false);
    }
  };

  /**
   * Delete SMS provider credentials
   */
  const handleDelete = async () => {
    setSaving(true);
    setError('');
    
    try {
      // Call the API to delete the credentials
      await deleteProviderSecret({ providerType: 'sms' });
      
      // Reset form fields
      setAccessKey('');
      setSecretKey('');
      setRegion('us-east-1');
      setTestResult('');
      
      // Update status
      setConfigured(false);
      setStatus('untested');
      
      // Clear localStorage
      localStorage.removeItem('sms_configured');
      localStorage.removeItem('sms_tested');
      
      // Refresh status from backend
      fetchStatus();
    } catch (error) {
      console.error('Error deleting SMS provider credentials:', error);
      setError(error.response?.data?.detail || error.message || 'Failed to delete credentials');
    } finally {
      setSaving(false);
    }
  };

  return (
    <Box sx={{ mb: 4 }} data-testid="sms-provider-section">
      <h3>SMS Provider Configuration</h3>
      
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
        <InputLabel>SMS Provider</InputLabel>
        <Select
          value={provider || ''}
          onChange={handleProviderChange}
          data-testid="sms-provider-select"
        >
          <MenuItem value="aws_sns">AWS SNS</MenuItem>
          <MenuItem value="twilio">Twilio</MenuItem>
        </Select>
      </FormControl>
      
      <TextField
        label="Access Key"
        value={accessKey}
        onChange={(e) => setAccessKey(e.target.value)}
        fullWidth
        margin="normal"
        data-testid="sms-access-key-input"
      />
      
      <TextField
        label="Secret Key"
        value={secretKey}
        onChange={(e) => setSecretKey(e.target.value)}
        fullWidth
        margin="normal"
        type="password"
        data-testid="sms-secret-key-input"
      />
      
      <TextField
        label="Region"
        value={region}
        onChange={(e) => setRegion(e.target.value)}
        fullWidth
        margin="normal"
        data-testid="sms-region-input"
      />
      
      {/* Test phone number fields removed as they're no longer needed for credential validation */}
      
      <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
        <Button 
          variant="contained" 
          onClick={handleSave}
          disabled={saving}
          data-testid="save-sms-button"
        >
          {saving ? 'Saving...' : 'Save'}
        </Button>
        
        <Button 
          variant="outlined" 
          onClick={handleTest}
          disabled={testing}
          data-testid="test-sms-button"
        >
          {testing ? 'Testing...' : 'Test'}
        </Button>
        
        <Button 
          variant="outlined" 
          color="error" 
          onClick={handleDelete}
          data-testid="delete-sms-button"
        >
          Delete
        </Button>
      </Box>
    </Box>
  );
}

export default SmsProviderConfig;
