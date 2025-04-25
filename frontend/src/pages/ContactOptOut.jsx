import { useState, useEffect } from 'react';
import { Box, Button, Typography, Paper, TextField, Stack, Alert, CircularProgress } from '@mui/material';
import { useSearchParams } from 'react-router-dom';
import { optOutContact, sendVerificationCode, verifyCode, fetchContactPreferences } from '../api';
import PreferencesDashboard from './PreferencesDashboard';
import { formatPhoneToE164, isValidPhoneNumber } from '../utils/phoneUtils';

function maskEmail(email) {
  if (!email) return '';
  const [user, domain] = email.split('@');
  return user[0] + '***@' + domain;
}
function maskPhone(phone) {
  if (!phone) return '';
  return phone.replace(/\d(?=\d{2})/g, '*');
}

export default function ContactOptOut({ mode = 'preferences' }) {
  // mode can be 'preferences' or 'verbal'
  const [searchParams] = useSearchParams();
  const [step, setStep] = useState(0); // 0: enter, 1: verify consent, 2: enter code, 3: preferences
  const [contact, setContact] = useState('');
  const [masked, setMasked] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const [codeSent, setCodeSent] = useState(false);
  const [code, setCode] = useState('');
  const [codeError, setCodeError] = useState('');
  const [verified, setVerified] = useState(false);
  const [preferences, setPreferences] = useState(null);
  const [token, setToken] = useState('');

  // On mount, check for token, email/phone, and code in URL
  useEffect(() => {
    // First, check if we have a preferences token
    const preferencesToken = localStorage.getItem('preferences_token');
    
    // For Phase 1, we'll always start at step 0 (enter contact) to enforce verification
    // This ensures users must verify their identity before accessing preferences
    if (mode === 'preferences') {
      setStep(0);
      checkUrlParams();
    } else if (preferencesToken && mode === 'verbal') {
      // For verbal mode, if we have a token, fetch preferences directly
      setToken(preferencesToken);
      setVerified(true);
      setLoading(true);
      
      fetchContactPreferences({ token: preferencesToken })
        .then(prefs => {
          console.log('Fetched preferences with token:', prefs);
          setPreferences(prefs);
          setStep(3); // Skip to preferences page for verbal mode only
        })
        .catch(error => {
          console.error('Error fetching preferences with token:', error);
          // Token might be expired, clear it and start over
          localStorage.removeItem('preferences_token');
          checkUrlParams();
        })
        .finally(() => {
          setLoading(false);
        });
    } else {
      // No token, check URL parameters
      checkUrlParams();
    }
    
    function checkUrlParams() {
      const email = searchParams.get('email');
      const phone = searchParams.get('phone');
      const contactParam = searchParams.get('contact');
      const codeParam = searchParams.get('code');
      
      // Use contact from URL parameters (in order of preference)
      const contactValue = contactParam || email || phone;
      
      console.log('URL parameters:', { contactParam, email, phone, contactValue, codeParam });
      
      if (contactValue) {
        // Decode the contact value if it's URL encoded
        const decodedContact = decodeURIComponent(contactValue);
        console.log('Decoded contact:', decodedContact);
        
        setContact(decodedContact);
        setMasked(decodedContact.includes('@') ? maskEmail(decodedContact) : maskPhone(decodedContact));
        
        // If we have both contact and code in URL, go to verification step
        if (codeParam && mode === 'preferences') {
          console.log('Code provided in URL, going to verification step');
          setCode(codeParam);
          setStep(2); // Go to verification step but don't auto-verify
        } else if (mode === 'preferences') {
          // For preferences mode with contact but no code, go to step 1 (send code)
          setStep(1);
        } else {
          // For verbal mode, start at step 0
          setStep(0);
        }
      } else {
        // No contact info, start at step 0 (enter contact)
        setStep(0);
      }
    }
  }, [searchParams, mode]);

  // Step 0: Enter contact if not in URL
  const handleContactSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (!contact) {
      setError('Please enter your email or phone number.');
      return;
    }
    const isEmail = contact.includes('@');
    const isPhone = !isEmail && isValidPhoneNumber(contact);
    if (!isEmail && !isPhone) {
      setError('Enter a valid email or phone number (at least 8 digits).');
      return;
    }
    
    // Format phone number if needed
    let formattedContact = contact;
    if (isPhone) {
      formattedContact = formatPhoneToE164(contact);
      console.log(`Formatted phone number from ${contact} to ${formattedContact}`);
    }
    
    // Update contact with formatted version
    setContact(formattedContact);
    setMasked(isEmail ? maskEmail(formattedContact) : maskPhone(formattedContact));
    setStep(1);
  };

  // State for dev mode code display
  const [devCode, setDevCode] = useState('');

  // Step 1: Send verification code
  const handleSendCode = async () => {
    setLoading(true);
    setError('');
    setDevCode(''); // Clear any previous dev code
    try {
      // Determine purpose based on mode
      let purpose, auth_user_name;
      
      if (mode === 'verbal') {
        // For verbal mode, always use verbal_auth purpose
        purpose = 'verbal_auth';
        auth_user_name = 'Support Agent'; // In a real app, get from user context
      } else {
        // For preferences mode, use self_service
        purpose = 'self_service';
        auth_user_name = undefined;
      }
      
      // Determine contact type based on format
      const isEmail = contact.includes('@');
      const contactType = isEmail ? 'email' : 'phone';
      
      // Ensure phone numbers are properly formatted
      let formattedContact = contact;
      if (!isEmail) {
        formattedContact = formatPhoneToE164(contact);
        if (formattedContact !== contact) {
          console.log(`Formatted phone number for sending: ${contact} → ${formattedContact}`);
          setContact(formattedContact); // Update state with formatted number
        }
      }
      
      const response = await sendVerificationCode({ 
        contact: formattedContact, 
        contact_type: contactType,
        purpose, 
        auth_user_name 
      });
      
      // Check if we received a dev code (development mode only)
      if (response && response.dev_code) {
        console.log('Development mode: Verification code received in response');
        setDevCode(response.dev_code);
      }
      
      setCodeSent(true);
      
      // For verbal opt-in mode, show confirmation and don't proceed to code entry
      if (mode === 'verbal') {
        // Show success message and stay on current step
        setSuccess(`Verification code sent to ${masked}. The contact will need to verify their email and set preferences.`);
        // Don't advance to code verification step for verbal mode
      } else {
        // For preferences mode, proceed to code verification
        setStep(2);
      }
    } catch (error) {
      console.error('Error sending verification code:', error);
      setError('Failed to send verification code.');
    } finally {
      setLoading(false);
    }
  };

  // Step 2: Verify code
  const handleVerifyCode = async (e) => {
    if (e) e.preventDefault();
    setLoading(true);
    setCodeError('');
    try {
      // Determine contact type based on format
      const isEmail = contact.includes('@');
      const contactType = isEmail ? 'email' : 'phone';
      
      // Ensure phone numbers are properly formatted
      let formattedContact = contact;
      if (!isEmail) {
        formattedContact = formatPhoneToE164(contact);
        if (formattedContact !== contact) {
          console.log(`Formatted phone number for verification: ${contact} → ${formattedContact}`);
          setContact(formattedContact); // Update state with formatted number
        }
      }
      
      console.log('Verifying code with:', { contact: formattedContact, contactType, code });
      
      const result = await verifyCode({ 
        contact: formattedContact, 
        contact_type: contactType,
        code 
      });
      console.log('Verification result:', result);
      
      // Store token for future use
      if (result.token) {
        localStorage.setItem('preferences_token', result.token);
        setToken(result.token);
      } else {
        console.error('No token received from verification');
        setCodeError('Verification failed - no token received');
        setLoading(false);
        return;
      }
      
      setVerified(true);
      
      // Fetch preferences using the token
      try {
        console.log('Fetching preferences with token:', result.token);
        const prefs = await fetchContactPreferences({ token: result.token });
        console.log('Fetched preferences:', prefs);
        setPreferences(prefs);
        
        // Update the URL to /preferences without reloading the page
        window.history.pushState({}, '', `/preferences?contact=${encodeURIComponent(contact)}`);
        
        // Move to preferences dashboard
        setStep(3);
      } catch (error) {
        console.error('Error fetching preferences:', error);
        setCodeError('Verification successful, but failed to load preferences.');
      }
    } catch (error) {
      console.error('Verification error:', error);
      setCodeError(error.response?.data?.detail || 'Invalid verification code');
    } finally {
      setLoading(false);
    }
  };

  // Debug current state
  console.log('Render state:', { mode, step, verified, preferences, token });
  
  // Check if user is authenticated
  const isAuthenticated = !!localStorage.getItem('access_token');
  
  // If this is verbal mode and user is not authenticated, redirect to login
  useEffect(() => {
    if (mode === 'verbal' && !isAuthenticated) {
      window.location.href = '/login';
    }
  }, [mode, isAuthenticated]);
  
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

          <Typography variant="h6" gutterBottom>
            {mode === 'verbal' ? 'Verbal Opt-in' : 'Manage Communication Preferences'}
          </Typography>
        <Typography variant="caption" color="text.secondary" mb={2}>
          {mode === 'verbal' 
            ? 'Send a verification code to a contact for verbal opt-in purposes.'
            : 'For compliance, only masked contact info is shown. No names or raw PII are ever stored or displayed.'}
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
            {success ? (
              <>
                <Alert severity="success">{success}</Alert>
                <Typography variant="body2">
                  The contact will receive an email with a verification code and instructions to manage their preferences.
                </Typography>
                <Button variant="outlined" onClick={() => setStep(0)}>Start Over</Button>
              </>
            ) : (
              <>
                <Typography>
                  We will send a verification code to <b>{masked}</b> to confirm you are the owner. Do you want to continue?
                </Typography>
                {error && <Alert severity="error">{error}</Alert>}
                <Button variant="contained" onClick={handleSendCode} disabled={loading}>
                  {loading ? <CircularProgress size={24} /> : 'Send Code'}
                </Button>
              </>
            )}
          </Stack>
        )}
        {step === 2 && (
          <form onSubmit={handleVerifyCode}>
            <Stack spacing={2}>
              <Typography>Enter the code sent to <b>{masked}</b>:</Typography>
              
              {/* Display the dev code if available */}
              {devCode && (
                <Alert severity="info">
                  <Typography variant="subtitle2">Development Mode</Typography>
                  <Typography variant="body2">
                    Since SMS delivery depends on AWS SNS configuration, here's your verification code for testing: <b>{devCode}</b>
                  </Typography>
                </Alert>
              )}
              
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
              <Button 
                variant="text" 
                onClick={() => {
                  setCode('');
                  setCodeError('');
                  handleSendCode();
                }}
                disabled={loading}
              >
                Resend Code
              </Button>
            </Stack>
          </form>
        )}
        {step === 3 && (
          <>
            {preferences ? (
              <Box sx={{ width: '100%', maxWidth: 800, mx: 'auto', p: 2 }}>
                <PreferencesDashboard 
                  masked={masked} 
                  token={token} 
                  preferences={preferences} 
                  setPreferences={setPreferences} 
                />
              </Box>
            ) : (
              <Stack spacing={2}>
                <Alert severity="info">Loading your preferences...</Alert>
                <CircularProgress />
              </Stack>
            )}
          </>
        )}

      </Paper>
    </Box>
  );
}
