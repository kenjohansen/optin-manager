/**
 * ProviderSection.jsx
 *
 * Communication provider configuration component.
 *
 * This component provides a form interface for administrators to configure
 * communication provider credentials (email and SMS services). It supports
 * saving, testing, and deleting provider configurations, which are essential
 * for the system's messaging capabilities.
 *
 * As noted in the memories, this supports the customization settings for
 * communication providers that are essential for consistent user experience
 * and proper message delivery.
 *
 * Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
 * This file is part of the OptIn Manager project and is licensed under the MIT License.
 * See the root LICENSE file for details.
 */

import { Stack, TextField, Button, Typography } from '@mui/material';

/**
 * Provider configuration section component.
 * 
 * This component renders a form that allows administrators to configure
 * communication provider credentials for email or SMS services. It handles
 * credential input, validation, testing, and management. These configurations
 * are securely stored in the backend and used for sending verification codes
 * and other communications to users.
 * 
 * @param {Object} props - Component props
 * @param {string} props.type - Provider type ('email' or 'sms')
 * @param {string} props.provider - Selected provider name
 * @param {Object} props.creds - Provider credentials object
 * @param {string} props.status - Current status of the provider connection
 * @param {boolean} props.credsSaved - Whether credentials have been saved
 * @param {Function} props.onSave - Handler for saving credentials
 * @param {Function} props.onTest - Handler for testing provider connection
 * @param {Function} props.onDelete - Handler for deleting provider configuration
 * @param {boolean} props.credSaving - Whether a save operation is in progress
 * @param {string} props.credError - Error message from credential operations
 * @param {Object} props.testResult - Result of connection test
 * @param {string} props.primaryColor - Primary brand color for styling
 * @param {string} props.secondaryColor - Secondary brand color for styling
 * @param {Function} props.setProvider - Function to update selected provider
 * @param {Function} props.setCreds - Function to update credential values
 * @returns {JSX.Element} The rendered provider configuration form
 */
export default function ProviderSection({
  type, provider, creds, status, credsSaved, onSave, onTest, onDelete, credSaving, credError, testResult, primaryColor, secondaryColor, setProvider, setCreds
}) {
  const isSavedOrTested = credsSaved || status === 'tested';
  const isTested = status === 'tested';
  return (
    <Stack spacing={2} alignItems="center" mb={4}>
      {type === 'email' && (
        <TextField
          label="Sender Email Address"
          fullWidth
          value={creds.fromAddress || ''}
          onChange={e => setCreds(c => ({ ...c, fromAddress: e.target.value }))}
          helperText="This must be a valid sender address for your chosen provider."

        />
      )}
      <TextField label={`${type === 'email' ? 'Email' : 'SMS'} Provider`} select SelectProps={{ native: true }} value={provider} onChange={e => setProvider(e.target.value)} fullWidth>
        <option value={type === 'email' ? 'aws_ses' : 'aws_sns'}>{type === 'email' ? 'AWS SES' : 'AWS SNS'}</option>
      </TextField>
      <TextField label="Access Key" type="password" fullWidth autoComplete="off" value={creds.accessKey} onChange={e => setCreds(c => ({ ...c, accessKey: e.target.value }))} />
      <TextField label="Secret Key" type="password" fullWidth autoComplete="off" value={creds.secretKey} onChange={e => setCreds(c => ({ ...c, secretKey: e.target.value }))} />
      <TextField label="Region" fullWidth value={creds.region} onChange={e => setCreds(c => ({ ...c, region: e.target.value }))} />
      <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} width="100%">
        <Button
          variant="contained"
          onClick={() => onSave(type)}
          disabled={credSaving}
          fullWidth
          sx={{
            bgcolor: isSavedOrTested ? (secondaryColor) : (primaryColor),
            color: '#fff',
            '&:hover': {
              bgcolor: isSavedOrTested ? (secondaryColor) : (primaryColor),
              opacity: 0.9,
            },
          }}
        >
          {isSavedOrTested ? 'Update' : 'Save'}
        </Button>
        <Button
          variant="outlined"
          onClick={() => onTest(type)}
          fullWidth
          sx={{
            borderColor: isTested ? (secondaryColor) : (primaryColor),
            color: isTested ? (secondaryColor) : (primaryColor),
            '&:hover': {
              borderColor: isTested ? (secondaryColor) : (primaryColor),
              backgroundColor: isTested ? (secondaryColor + '22') : (primaryColor + '22'),
            },
          }}
        >
          Test
        </Button>
        <Button variant="outlined" color="error" onClick={() => onDelete(type)} fullWidth>Delete</Button>
      </Stack>
      {testResult && <Typography variant="body2" color={testResult.includes('Success') ? 'success.main' : 'error.main'}>{testResult}</Typography>}
      {credError && <Typography variant="body2" color="error.main">{credError}</Typography>}
    </Stack>
  );
}
