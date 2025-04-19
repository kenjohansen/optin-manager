import { useState, useEffect } from 'react';
import { Box, Button, Typography, Paper, TextField, Stack, Alert, CircularProgress } from '@mui/material';
import { useSearchParams } from 'react-router-dom';
import { optOutContact, sendVerificationCode, verifyCode, fetchContactPreferences } from '../api';
import PreferencesDashboard from './PreferencesDashboard';

function maskEmail(email) {
  if (!email) return '';
  const [user, domain] = email.split('@');
  return user[0] + '***@' + domain;
}
function maskPhone(phone) {
  if (!phone) return '';
  return phone.replace(/\d(?=\d{2})/g, '*');
}

export default function ContactOptOut() {
  const [searchParams] = useSearchParams();
  const [step, setStep] = useState(0); // 0: enter, 1: verify consent, 2: enter code, 3: preferences
  const [contact, setContact] = useState('');
  const [masked, setMasked] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [codeSent, setCodeSent] = useState(false);
  const [code, setCode] = useState('');
  const [codeError, setCodeError] = useState('');
  const [verified, setVerified] = useState(false);
  const [preferences, setPreferences] = useState(null);

  // On mount, check for email/phone in URL
  useEffect(() => {
    const email = searchParams.get('email');
    const phone = searchParams.get('phone');
    if (email || phone) {
      setContact(email || phone);
      setMasked(email ? maskEmail(email) : maskPhone(phone));
      setStep(1); // skip straight to verification consent
    }
  }, [searchParams]);

  // Step 0: Enter contact if not in URL
  const handleContactSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (!contact) {
      setError('Please enter your email or phone number.');
      return;
    }
    const isEmail = contact.includes('@');
    const isPhone = !isEmail && /\d{6,}/.test(contact);
    if (!isEmail && !isPhone) {
      setError('Enter a valid email or phone number.');
      return;
    }
    setMasked(isEmail ? maskEmail(contact) : maskPhone(contact));
    setStep(1);
  };

  // Step 1: Send verification code
  const handleSendCode = async () => {
    setLoading(true);
    setError('');
    try {
      await sendVerificationCode({ contact });
      setCodeSent(true);
      setStep(2);
    } catch {
      setError('Failed to send verification code.');
    } finally {
      setLoading(false);
    }
  };

  // Step 2: Verify code
  const handleVerifyCode = async (e) => {
    e.preventDefault();
    setCodeError('');
    setLoading(true);
    try {
      await verifyCode({ contact, code });
      setVerified(true);
      // Fetch preferences (stub)
      const prefs = await fetchContactPreferences({ contact });
      setPreferences(prefs);
      setStep(3);
    } catch {
      setCodeError('Invalid or expired code.');
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
      <Paper elevation={3} sx={{ p: 3, maxWidth: 600, width: '100%', mx: 'auto', textAlign: 'center' }}>

          <Typography variant="h6" gutterBottom>Opt-Out / Manage Preferences</Typography>
        <Typography variant="caption" color="text.secondary" mb={2}>
          For compliance, only masked contact info is shown. No names or raw PII are ever stored or displayed.
        </Typography>
        {step === 0 && (
          <form onSubmit={handleContactSubmit}>
            <Stack spacing={2}>
              <TextField
                label="Email or Phone"
                value={contact}
                onChange={e => setContact(e.target.value)}
                fullWidth
                required
              />
              {error && <Alert severity="error">{error}</Alert>}
              <Button type="submit" variant="contained">Continue</Button>
            </Stack>
          </form>
        )}
        {step === 1 && (
          <Stack spacing={2}>
            <Typography>
              We will send a verification code to <b>{masked}</b> to confirm you are the owner. Do you want to continue?
            </Typography>
            {error && <Alert severity="error">{error}</Alert>}
            <Button variant="contained" onClick={handleSendCode} disabled={loading}>
              {loading ? <CircularProgress size={24} /> : 'Send Code'}
            </Button>
          </Stack>
        )}
        {step === 2 && (
          <form onSubmit={handleVerifyCode}>
            <Stack spacing={2}>
              <Typography>Enter the code sent to <b>{masked}</b>:</Typography>
              <TextField
                label="Verification Code"
                value={code}
                onChange={e => setCode(e.target.value)}
                fullWidth
                required
              />
              {codeError && <Alert severity="error">{codeError}</Alert>}
              <Button type="submit" variant="contained" disabled={loading}>
                {loading ? <CircularProgress size={24} /> : 'Verify'}
              </Button>
            </Stack>
          </form>
        )}
        {step === 3 && preferences && (
          <PreferencesDashboard
            masked={masked}
            contact={contact}
            preferences={preferences}
            setPreferences={setPreferences}
          />
        )}

      </Paper>
    </Box>
  );
}
