import { useState, useEffect } from 'react';
import { Box, Paper, CircularProgress, Alert } from '@mui/material';
import BrandingSection from '../components/BrandingSection';
import ProviderSection from '../components/ProviderSection';
import { fetchCustomization, saveCustomization, API_BASE } from '../api';
import { setProviderSecret, getSecretsStatus, testProviderConnection, deleteProviderSecret } from '../api/providerSecrets';

export default function Customization({ setLogoUrl, setPrimary, setSecondary, setCompanyName, setPrivacyPolicy }) {
  const [logo, setLogo] = useState(null);
  const [logoPreview, setLogoPreview] = useState(null);
  const [primary, setPrimaryLocal] = useState('#1976d2');
  const [secondary, setSecondaryLocal] = useState('#9c27b0');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  // Company/Policy/Provider
  const [companyName, setCompanyNameLocal] = useState('');
  const [privacyPolicy, setPrivacyPolicyLocal] = useState('');
  const [emailProvider, setEmailProvider] = useState('aws_ses');
  const [smsProvider, setSmsProvider] = useState('aws_sns');

  // Provider credentials and status
  const [emailCreds, setEmailCreds] = useState({ accessKey: '', secretKey: '', region: '' });
  const [smsCreds, setSmsCreds] = useState({ accessKey: '', secretKey: '', region: '' });
  // Remove secretsStatus, rely on customization API's status fields
  const [testResult, setTestResult] = useState({ email: '', sms: '' });
  const [credSaving, setCredSaving] = useState({ email: false, sms: false });
  const [credError, setCredError] = useState({ email: '', sms: '' });
  const [customization, setCustomization] = useState({});
  const [credsSaved, setCredsSaved] = useState({ email: false, sms: false });

  const refreshCustomization = () => {
    setLoading(true);
    fetchCustomization()
      .then(data => {
        setCustomization(data);
        if (data.logo_url) {
          let logoUrl = data.logo_url;
          if (logoUrl && logoUrl.startsWith('/')) {
            let backendOrigin = API_BASE.replace(/\/api\/v1\/?$/, '');
            logoUrl = backendOrigin + logoUrl;
          }
          setLogoPreview(logoUrl);
          if (setLogoUrl) setLogoUrl(logoUrl);
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
      .catch(() => {
        setError('Failed to load customization.');
        setLoading(false);
      });
  };

  useEffect(() => {
    refreshCustomization();
  }, [setLogoUrl, setPrimary, setSecondary]);

  const handleLogoChange = (e) => {
    const file = e.target.files[0];
    setLogo(file);
    const preview = file ? URL.createObjectURL(file) : null;
    setLogoPreview(preview);
    if (setLogoUrl) setLogoUrl(preview);
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    setSuccess(false);
    try {
      await saveCustomization({
        logo,
        primary,
        secondary,
        company_name: companyName,
        privacy_policy_url: privacyPolicy,
        email_provider: emailProvider,
        sms_provider: smsProvider,
      });
      setSuccess(true);
      if (setPrimary) setPrimary(primary);
      if (setSecondary) setSecondary(secondary);
      if (setCompanyName) setCompanyName(companyName);
      if (setPrivacyPolicy) setPrivacyPolicy(privacyPolicy);
    } catch {
      setError('Failed to save customization.');
    } finally {
      setSaving(false);
    }
  };

  const handleCredSave = async (type) => {
    setCredSaving(cs => ({ ...cs, [type]: true }));
    setCredError(ce => ({ ...ce, [type]: '' }));
    try {
      const creds = type === 'email' ? emailCreds : smsCreds;
      await setProviderSecret({ providerType: type, ...creds });
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
      setTestResult(tr => ({ ...tr, [type]: 'Failed to connect.' }));
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
