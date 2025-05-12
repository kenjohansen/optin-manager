import { useState } from 'react';
import { 
  Box, 
  Paper, 
  Typography, 
  TextField, 
  Button, 
  Stack, 
  Alert, 
  CircularProgress, 
  FormControlLabel, 
  Switch,
  Divider
} from '@mui/material';
import { fetchOptIns, updateContactPreferences, sendVerificationCode, fetchContactPreferences } from '../api';
import { useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { formatPhoneToE164, isValidPhoneNumber } from '../utils/phoneUtils';

// Helper function to mask email for display
function maskEmail(email) {
  if (!email) return '';
  const [user, domain] = email.split('@');
  return user[0] + '***@' + domain;
}

// Helper function to mask phone for display
function maskPhone(phone) {
  if (!phone) return '';
  return phone.replace(/\d(?=\d{2})/g, '*');
}

export default function VerbalOptIn() {
  // Get URL parameters - wrapped in try/catch for test environment
  let searchParams = { get: () => null }; // Default fallback for tests
  try {
    // This will work in the browser but might fail in some test environments
    [searchParams] = useSearchParams();
  } catch (error) {
    // In test environment, we'll use the default fallback
    console.log('Using fallback search params for testing environment');
  }
  
  // Contact info state
  const [contact, setContact] = useState('');
  const [contactType, setContactType] = useState('');
  const [masked, setMasked] = useState('');
  
  // UI state
  const [loading, setLoading] = useState(false);
  const [optinsLoading, setOptinsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Opt-in programs state
  const [optIns, setOptIns] = useState([]);
  const [contactPreferences, setContactPreferences] = useState([]);
  const [comment, setComment] = useState('');
  
  // Step state (0: enter contact, 1: select preferences)
  const [step, setStep] = useState(0);
  
  // Handle contact from URL params and load preferences when component mounts
  useEffect(() => {
    const processContactParam = async () => {
      const contactParam = searchParams.get('contact');
      if (!contactParam) return;
      
      const decodedContact = decodeURIComponent(contactParam);
      setContact(decodedContact);
      
      // Determine contact type and set masked value
      let type = '';
      if (decodedContact.includes('@')) {
        type = 'email';
        setContactType('email');
        setMasked(maskEmail(decodedContact));
      } else if (isValidPhoneNumber(decodedContact)) {
        type = 'phone';
        setContactType('phone');
        setMasked(maskPhone(decodedContact));
      } else {
        return; // Invalid contact format
      }
      
      // Load preferences for this contact
      setLoading(true);
      setError('');
      
      try {
        // Send verification code just to confirm contact exists
        await sendVerificationCode({
          contact: decodedContact,
          contactType: type
        });
        
        // Load any existing preferences
        const preferences = await fetchContactPreferences({
          contact: decodedContact 
        });
        
        console.log('Loaded preferences for contact:', preferences);
        
        setContactPreferences(preferences.programs || []);
        setStep(1); // Go directly to the preferences view
      } catch (error) {
        console.error('Error loading preferences:', error);
        setError('Could not load preferences for this contact.');
      } finally {
        setLoading(false);
      }
    };
    
    processContactParam();
  }, [searchParams]);
  
  // Load all available opt-ins on component mount
  useEffect(() => {
    const loadOptIns = async () => {
      try {
        setOptinsLoading(true);
        const data = await fetchOptIns();
        
        // Filter to only active opt-ins
        const activeOptIns = data.filter(optin => optin.status === 'active');
        setOptIns(activeOptIns);
        
        console.log('Loaded opt-ins:', activeOptIns);
      } catch (error) {
        console.error('Error loading opt-ins:', error);
        setError('Failed to load opt-in programs. Please refresh the page.');
      } finally {
        setOptinsLoading(false);
      }
    };
    
    loadOptIns();
  }, []);
  
  // Handle contact submission
  const handleContactSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    try {
      if (!contact) {
        setError('Please enter a contact email or phone number.');
        return;
      }
      
      // Determine contact type
      const isEmail = contact.includes('@');
      const isPhone = !isEmail && isValidPhoneNumber(contact);
      
      if (!isEmail && !isPhone) {
        setError('Enter a valid email or phone number.');
        return;
      }
      
      // Format phone number if needed
      let formattedContact = contact;
      if (isPhone) {
        formattedContact = formatPhoneToE164(contact);
        console.log(`Formatted phone number from ${contact} to ${formattedContact}`);
      }
      
      // Set contact info
      setContact(formattedContact);
      setContactType(isEmail ? 'email' : 'phone');
      setMasked(isEmail ? maskEmail(formattedContact) : maskPhone(formattedContact));
      
      // Try to fetch existing preferences for this contact
      try {
        console.log('Fetching preferences for contact:', formattedContact);
        const prefsData = await fetchContactPreferences({ contact: formattedContact });
        console.log('Existing preferences found:', prefsData);
        
        if (prefsData && prefsData.programs && prefsData.programs.length > 0) {
          // Create a map of preferences by name for easier lookup
          const prefsByName = {};
          prefsData.programs.forEach(program => {
            prefsByName[program.name] = program.opted_in;
            console.log(`Found preference for ${program.name}: opted_in=${program.opted_in}`);
          });
          
          // Map existing preferences to our format using name matching
          const existingPrefs = optIns.map(optin => {
            // Look up by name since IDs might be in different formats
            const isOptedIn = prefsByName[optin.name] === true;
            
            console.log(`Setting ${optin.name} to opted_in: ${isOptedIn}`);
            
            return {
              id: optin.id,
              name: optin.name,
              type: optin.type,
              opted_in: isOptedIn
            };
          });
          
          // Make sure we actually set the state with the new preferences
          console.log('Final mapped preferences:', existingPrefs);
          
          console.log('Final mapped preferences:', existingPrefs);
          setContactPreferences(existingPrefs);
          setSuccess('Existing preferences loaded for this contact.');
        } else {
          // Initialize preferences with all opt-ins set to false
          const initialPreferences = optIns.map(optin => ({
            id: optin.id,
            name: optin.name,
            type: optin.type,
            opted_in: false
          }));
          
          setContactPreferences(initialPreferences);
        }
      } catch (error) {
        console.log('No existing preferences found or error fetching:', error);
        // Initialize preferences with all opt-ins set to false
        const initialPreferences = optIns.map(optin => ({
          id: optin.id,
          name: optin.name,
          type: optin.type,
          opted_in: false
        }));
        
        setContactPreferences(initialPreferences);
      }
      
      setStep(1);
    } catch (error) {
      console.error('Error processing contact:', error);
      setError('An error occurred while processing the contact information.');
    } finally {
      setLoading(false);
    }
  };
  
  // Handle preference toggle
  const handleToggleOptIn = (index) => {
    setContactPreferences(prefs => 
      prefs.map((pref, i) => 
        i === index ? { ...pref, opted_in: !pref.opted_in } : pref
      )
    );
  };
  
  // Handle save preferences
  const handleSavePreferences = async () => {
    setLoading(true);
    setError('');
    setSuccess('');
    
    try {
      // Get authenticated user info from localStorage
      const authUserName = localStorage.getItem('username') || 'Support Agent';
      const authUserEmail = localStorage.getItem('email') || 'support@example.com';
      
      console.log('Auth user info:', { authUserName, authUserEmail });
      
      // Update preferences in the backend
      // Looking at the backend code, it expects a 'programs' array with objects that have 'id' and 'opted_in' properties
      const programsArray = contactPreferences.map(pref => ({
        id: pref.id,
        opted_in: pref.opted_in
      }));
      
      console.log('Sending programs array:', programsArray);
      
      await updateContactPreferences({
        contact: contact,
        programs: programsArray,
        comment: comment
      });
      
      // Send notification to the contact with auth user details
      await sendVerificationCode({
        contact: contact,
        contact_type: contactType,
        purpose: 'verbal_auth',
        auth_user_name: authUserName,
        auth_user_email: authUserEmail
      });
      
      // Show success message
      setSuccess(`Preferences updated for ${masked}. A notification has been sent to the contact with their current opt-in status and a link to review their preferences.`);
      
      // Reset form for next entry
      setTimeout(() => {
        setContact('');
        setMasked('');
        setContactPreferences([]);
        setComment('');
        setStep(0);
        setSuccess('');
      }, 5000);
      
    } catch (error) {
      console.error('Error saving preferences:', error);
      setError('Failed to update preferences. Please try again.');
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
        width: '90vw',
        margin: 'auto'
      }}
    >
      <Paper elevation={3} sx={{ p: 3, maxWidth: 600, width: '100%', mx: 'auto' }}>
        <Typography variant="h6" gutterBottom align="center">
          Verbal Opt-In Management
        </Typography>
        
        <Typography variant="body2" color="text.secondary" paragraph align="center">
          Use this form to record verbal opt-ins received from customers. The customer will receive
          a notification with their current preferences and a link to review them.
        </Typography>
        
        {step === 0 ? (
          <form onSubmit={handleContactSubmit}>
            <Stack spacing={2}>
              <TextField
                label="Customer Email or Phone"
                value={contact}
                onChange={(e) => setContact(e.target.value)}
                fullWidth
                required
                placeholder="email@example.com or +1234567890"
              />
              
              {error && <Alert severity="error">{error}</Alert>}
              
              <Button 
                type="submit" 
                variant="contained" 
                fullWidth
                disabled={optinsLoading}
              >
                {optinsLoading ? <CircularProgress size={24} /> : 'Continue'}
              </Button>
            </Stack>
          </form>
        ) : (
          <Stack spacing={3}>
            <Typography variant="subtitle1">
              Contact: <strong>{masked}</strong>
            </Typography>
            
            <Divider />
            
            <Typography variant="subtitle1">
              Select Opt-Ins the Customer Verbally Agreed To:
            </Typography>
            
            {contactPreferences.length === 0 ? (
              <Alert severity="info">No opt-in programs available.</Alert>
            ) : (
              contactPreferences.map((pref, index) => (
                <FormControlLabel
                  key={pref.id}
                  control={
                    <Switch
                      checked={pref.opted_in}
                      onChange={() => handleToggleOptIn(index)}
                      color="primary"
                    />
                  }
                  label={
                    <Typography>
                      {pref.name} <Typography component="span" color="text.secondary" variant="caption">({pref.type})</Typography>
                    </Typography>
                  }
                />
              ))
            )}
            
            <TextField
              label="Notes about this verbal opt-in"
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              multiline
              rows={2}
              fullWidth
              placeholder="e.g., Customer called and requested to receive promotional messages"
            />
            
            {error && <Alert severity="error">{error}</Alert>}
            {success && <Alert severity="success">{success}</Alert>}
            
            <Stack direction="row" spacing={2}>
              <Button 
                variant="outlined" 
                onClick={() => setStep(0)}
                disabled={loading}
                fullWidth
              >
                Back
              </Button>
              
              <Button 
                variant="contained" 
                onClick={handleSavePreferences}
                disabled={loading || contactPreferences.length === 0}
                fullWidth
              >
                {loading ? <CircularProgress size={24} /> : 'Save Preferences & Notify Customer'}
              </Button>
            </Stack>
          </Stack>
        )}
      </Paper>
    </Box>
  );
}
