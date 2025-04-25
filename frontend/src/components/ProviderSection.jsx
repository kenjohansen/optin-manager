import { Stack, TextField, Button, Typography } from '@mui/material';

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
