/**
 * Customization.jsx
 *
 * System customization and provider configuration interface.
 *
 * This component provides an administrative interface for customizing the application's
 * branding and configuring communication providers. It allows administrators to set
 * company information, upload logos, choose theme colors, and configure email and SMS
 * provider credentials.
 *
 * As noted in the memories, this component is accessible to users with Admin role and
 * provides essential configuration options for the system's appearance and communication
 * capabilities. The provider configuration is particularly important for the Opt-Out
 * workflow, as it enables the system to send verification codes and other communications.
 *
 * Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
 * This file is part of the OptIn Manager project and is licensed under the MIT License.
 * See the root LICENSE file for details.
 */

import { useState, useEffect } from 'react';
import { Box, Paper, CircularProgress, Alert } from '@mui/material';
import BrandingSection from '../components/BrandingSection';
import ProviderSection from '../components/ProviderSection';
import { fetchCustomization, saveCustomization, API_BASE } from '../api';
import { setProviderSecret, getSecretsStatus, testProviderConnection, deleteProviderSecret } from '../api/providerSecrets';

/**
 * System customization and provider configuration component.
 * 
 * This component provides a comprehensive interface for administrators to customize
 * the application's appearance and configure communication providers. It handles
 * branding elements like company name, logo, colors, and privacy policy URL, as well
 * as the configuration of email and SMS provider credentials.
 * 
 * The component communicates with the backend to fetch existing customization settings,
 * save updated settings, and test provider connections. It also updates the application's
 * global theme based on the selected colors.
 * 
 * @param {Object} props - Component props
 * @param {Function} props.setLogoUrl - Function to update the logo URL in the parent component
 * @param {Function} props.setPrimary - Function to update the primary color in the parent component
 * @param {Function} props.setSecondary - Function to update the secondary color in the parent component
 * @param {Function} props.setCompanyName - Function to update the company name in the parent component
 * @param {Function} props.setPrivacyPolicy - Function to update the privacy policy URL in the parent component
 * @returns {JSX.Element} The rendered customization interface
 */
export default function Customization({ setLogoUrl, setPrimary, setSecondary, setCompanyName, setPrivacyPolicy }) {
  // Branding state
  const [logo, setLogo] = useState(null);
  const [logoPreview, setLogoPreview] = useState(null);
  const [primary, setPrimaryLocal] = useState('#1976d2');
  const [secondary, setSecondaryLocal] = useState('#9c27b0');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  // Company information and provider selection state
  const [companyName, setCompanyNameLocal] = useState('');
  const [privacyPolicy, setPrivacyPolicyLocal] = useState('');
  const [emailProvider, setEmailProvider] = useState('aws_ses');
  const [smsProvider, setSmsProvider] = useState('aws_sns');

  // Provider credentials and connection status state
  const [emailCreds, setEmailCreds] = useState({ accessKey: '', secretKey: '', region: '', fromAddress: '' });
  const [smsCreds, setSmsCreds] = useState({ accessKey: '', secretKey: '', region: '' });
  const [testResult, setTestResult] = useState({ email: '', sms: '' });
  const [credSaving, setCredSaving] = useState({ email: false, sms: false });
  const [credError, setCredError] = useState({ email: '', sms: '' });
  const [customization, setCustomization] = useState({});
  const [credsSaved, setCredsSaved] = useState({ email: false, sms: false });

  /**
   * Fetches current customization settings from the backend.
   * 
   * This function retrieves the current branding and provider configuration
   * settings from the backend API. It updates the component state with the
   * retrieved values and handles authentication checks and error conditions.
   * 
   * This is essential for ensuring that administrators can view and modify
   * the current system settings rather than starting from default values.
   */
  const refreshCustomization = () => {
    setLoading(true);
    setError('');
    
    // Check if user is authenticated
    const token = localStorage.getItem('access_token');
    if (!token) {
      setError('Authentication required. Please log in to access customization settings.');
      setLoading(false);
      return;
    }
    
    fetchCustomization()
      .then(data => {
        // Check if data is empty (could happen if there was an error)
        if (!data || Object.keys(data).length === 0) {
          console.warn('Received empty customization data');
          setLoading(false);
          return;
        }
        
        setCustomization(data);
        if (data.logo_url) {
          let logoUrl = data.logo_url;
          // Check if the URL is a relative path (starts with /) and doesn't already contain the backend origin
          if (logoUrl && logoUrl.startsWith('/') && !logoUrl.includes('://')) {
            let backendOrigin = API_BASE.replace(/\/api\/v1\/?$/, '');
            logoUrl = backendOrigin + logoUrl;
          }
          
          // Add cache-busting timestamp to prevent browser caching
          const timestamp = new Date().getTime();
          logoUrl = `${logoUrl}?t=${timestamp}`;
          
          console.log('Setting logo URL with cache busting:', logoUrl);
          
          setLogoPreview(logoUrl);
          if (setLogoUrl) setLogoUrl(logoUrl);
        } else {
          console.log('No logo URL in customization data');
          // Clear the logo preview if there's no logo URL
          setLogoPreview(null);
          if (setLogoUrl) setLogoUrl(null);
        }
        
        if (data.primary_color) {
          setPrimaryLocal(data.primary_color);
          if (setPrimary) setPrimary(data.primary_color);
        }
        if (data.secondary_color) {
          setSecondaryLocal(data.secondary_color);
          if (setSecondary) setSecondary(data.secondary_color);
        }
        if (data.company_name) setCompanyNameLocal(data.company_name);
        if (data.privacy_policy_url) setPrivacyPolicyLocal(data.privacy_policy_url);
        if (data.email_provider) setEmailProvider(data.email_provider);
        if (data.sms_provider) setSmsProvider(data.sms_provider);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Error refreshing customization:', err);
        setError('Failed to load customization. ' + (err.message || ''));
        setLoading(false);
      });
  };

  useEffect(() => {
    refreshCustomization();
  }, [setLogoUrl, setPrimary, setSecondary]);

  const handleLogoChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    console.log('Selected logo file:', file.name);
    setLogo(file);
    
    // Create a preview URL
    const preview = URL.createObjectURL(file);
    console.log('Created preview URL:', preview);
    setLogoPreview(preview);
    
    // Update the app header logo
    if (setLogoUrl) setLogoUrl(preview);
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    setSuccess(false);
    
    // Check if user is authenticated
    const token = localStorage.getItem('access_token');
    if (!token) {
      setError('Authentication required. Please log in to save customization settings.');
      setSaving(false);
      return;
    }
    
    console.log('Saving customization with logo:', logo ? logo.name : 'none');
    
    try {
      const result = await saveCustomization({
        logo,
        primary,
        secondary,
        company_name: companyName,
        privacy_policy_url: privacyPolicy,
        email_provider: emailProvider,
        sms_provider: smsProvider,
      });
      
      console.log('Save customization result:', result);
      setSuccess(true);
      
      if (setPrimary) setPrimary(primary);
      if (setSecondary) setSecondary(secondary);
      if (setCompanyName) setCompanyName(companyName);
      if (setPrivacyPolicy) setPrivacyPolicy(privacyPolicy);
      
      // After successful save, refresh to get the updated logo URL from the backend
      // Increased timeout to ensure file is fully processed
      setTimeout(() => {
        refreshCustomization();
      }, 1000);
    } catch (error) {
      console.error('Error saving customization:', error);
      // Provide more specific error message if available
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to save customization.';
      setError(errorMessage);
      
      // If it's an authentication error, suggest logging in again
      if (error.response?.status === 401) {
        setError('Your session has expired. Please log in again.');
      }
    } finally {
      setSaving(false);
    }
  };

  const handleCredSave = async (type) => {
    setCredSaving(cs => ({ ...cs, [type]: true }));
    setCredError(ce => ({ ...ce, [type]: '' }));
    try {
      let creds = type === 'email' ? emailCreds : smsCreds;
      // Ensure fromAddress is sent for email
      if (type === 'email') {
        await setProviderSecret({ providerType: type, ...creds, fromAddress: creds.fromAddress });
      } else {
        await setProviderSecret({ providerType: type, ...creds });
      }
      setCredsSaved(s => ({ ...s, [type]: true }));
      refreshCustomization();
    } catch (e) {
      setCredError(ce => ({ ...ce, [type]: 'Failed to save credentials.' }));
    } finally {
      setCredSaving(cs => ({ ...cs, [type]: false }));
    }
  };

  const handleTestConnection = async (type) => {
    setTestResult(tr => ({ ...tr, [type]: 'Testing...' }));
    try {
      const res = await testProviderConnection({ providerType: type });
      setTestResult(tr => ({ ...tr, [type]: res.message || 'Success!' }));
      refreshCustomization();
    } catch (e) {
      // Extract detailed error message from the response if available
      const errorDetail = e.response?.data?.detail || e.message || 'Failed to connect.';
      console.error(`Test connection error (${type}):`, errorDetail);
      setTestResult(tr => ({ ...tr, [type]: errorDetail }));
    }
  };

  const handleDeleteCredentials = async (type) => {
    try {
      await deleteProviderSecret({ providerType: type });
      refreshCustomization();
    } catch (e) {
      setError('Failed to delete credentials.');
    }
  };

  if (loading) return (
    <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh"><CircularProgress /></Box>
  );

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
      <Paper
        elevation={3}
        sx={{
          p: { xs: 2, sm: 3, md: 4 },
          width: { xs: '100%', sm: 500, md: 650 },
          maxWidth: 650,
          mx: 'auto',
          textAlign: 'center',
        }}
      >
        <h2>Optin Customization</h2>
        {error && <Alert severity="error">{error}</Alert>}
        {success && <Alert severity="success">Saved!</Alert>}
        <BrandingSection
          logoPreview={logoPreview}
          handleLogoChange={handleLogoChange}
          companyName={companyName}
          setCompanyName={setCompanyNameLocal}
          privacyPolicy={privacyPolicy}
          setPrivacyPolicy={setPrivacyPolicyLocal}
          primary={primary}
          setPrimary={v => { setPrimaryLocal(v); if (setPrimary) setPrimary(v); }}
          secondary={secondary}
          setSecondary={v => { setSecondaryLocal(v); if (setSecondary) setSecondary(v); }}
          saving={saving}
          handleSave={handleSave}
        />
        <ProviderSection
          type="email"
          provider={emailProvider}
          setProvider={setEmailProvider}
          creds={emailCreds}
          setCreds={setEmailCreds}
          status={customization.email_connection_status}
          credsSaved={credsSaved.email}
          onSave={handleCredSave}
          onTest={handleTestConnection}
          onDelete={handleDeleteCredentials}
          credSaving={credSaving.email}
          credError={credError.email}
          testResult={testResult.email}
          primaryColor={primary}
          secondaryColor={secondary}
        />
        <ProviderSection
          type="sms"
          provider={smsProvider}
          setProvider={setSmsProvider}
          creds={smsCreds}
          setCreds={setSmsCreds}
          status={customization.sms_connection_status}
          credsSaved={credsSaved.sms}
          onSave={handleCredSave}
          onTest={handleTestConnection}
          onDelete={handleDeleteCredentials}
          credSaving={credSaving.sms}
          credError={credError.sms}
          testResult={testResult.sms}
          primaryColor={primary}
          secondaryColor={secondary}
        />
      </Paper>
    </Box>
  );
}
