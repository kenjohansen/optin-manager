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
 * Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
 * This file is part of the OptIn Manager project and is licensed under the MIT License.
 * See the root LICENSE file for details.
 */

import React, { useState, useEffect } from 'react';
import { Box, Paper, Snackbar, Alert } from '@mui/material';
import BrandingSection from '../components/BrandingSection';
import EmailProviderConfig from '../components/EmailProviderConfig';
import SmsProviderConfig from '../components/SmsProviderConfig';
import { fetchCustomization, saveCustomization } from '../api';

/**
 * System customization and provider configuration component.
 * 
 * This component provides a comprehensive interface for administrators to customize
 * the application's appearance and configure communication providers. It contains
 * three independent components:
 * 
 * 1. BrandingSection - For customizing company branding (logo, colors, etc.)
 * 2. EmailProviderConfig - For configuring email provider credentials
 * 3. SmsProviderConfig - For configuring SMS provider credentials
 * 
 * Each component handles its own state and API calls independently.
 * 
 * @param {Object} props - Component props
 * @returns {JSX.Element} The rendered customization interface
 */
export default function Customization() {
  // Branding state
  const [companyName, setCompanyName] = useState('');
  const [privacyPolicy, setPrivacyPolicy] = useState('');
  const [primary, setPrimary] = useState('#1976d2');
  const [secondary, setSecondary] = useState('#dc004e');
  const [logoPreview, setLogoPreview] = useState('');
  const [logoFile, setLogoFile] = useState(null);
  
  // UI state
  const [saving, setSaving] = useState(false);
  const [alert, setAlert] = useState({ open: false, message: '', severity: 'success' });
  
  // Fetch initial customization data
  useEffect(() => {
    fetchBrandingData();
  }, []);
  
  // Load customization data from API
  const fetchBrandingData = async () => {
    try {
      const data = await fetchCustomization();
      console.log('Fetched customization data:', data);
      
      if (data) {
        setCompanyName(data.company_name || '');
        setPrivacyPolicy(data.privacy_policy_url || '');
        setPrimary(data.primary_color || '#1976d2');
        setSecondary(data.secondary_color || '#dc004e');
        
        // Set logo preview if available
        if (data.logo_url) {
          setLogoPreview(data.logo_url);
        }
      }
    } catch (error) {
      console.error('Error fetching branding data:', error);
      setAlert({
        open: true,
        message: 'Failed to load customization data',
        severity: 'error'
      });
    }
  };
  
  // Handle logo file selection
  const handleLogoChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setLogoFile(file);
      const reader = new FileReader();
      reader.onload = (e) => setLogoPreview(e.target.result);
      reader.readAsDataURL(file);
    }
  };
  
  // Handle form submission
  const handleSaveBranding = async (e) => {
    e?.preventDefault();
    setSaving(true);
    
    try {
      await saveCustomization({
        company_name: companyName,
        privacy_policy_url: privacyPolicy,
        primary: primary,
        secondary: secondary,
        logo: logoFile // Only send the file if it's been changed
      });
      
      setAlert({
        open: true,
        message: 'Branding saved successfully',
        severity: 'success'
      });
      
      // Refresh data from server to get the processed logo URL
      fetchBrandingData();
    } catch (error) {
      console.error('Error saving branding:', error);
      setAlert({
        open: true,
        message: 'Failed to save branding settings',
        severity: 'error'
      });
    } finally {
      setSaving(false);
    }
  };
  
  // Handle alert close
  const handleAlertClose = () => {
    setAlert({ ...alert, open: false });
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
        
        {/* Branding Section - Pass all necessary props */}
        <BrandingSection 
          logoPreview={logoPreview}
          handleLogoChange={handleLogoChange}
          companyName={companyName}
          setCompanyName={setCompanyName}
          privacyPolicy={privacyPolicy}
          setPrivacyPolicy={setPrivacyPolicy}
          primary={primary}
          setPrimary={setPrimary}
          secondary={secondary}
          setSecondary={setSecondary}
          saving={saving}
          handleSave={handleSaveBranding}
        />
        
        {/* Email Provider Config - Completely independent component */}
        <EmailProviderConfig />
        
        {/* SMS Provider Config - Completely independent component */}
        <SmsProviderConfig />
      </Paper>
      
      {/* Notification for save/error events */}
      <Snackbar 
        open={alert.open} 
        autoHideDuration={6000} 
        onClose={handleAlertClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert 
          onClose={handleAlertClose} 
          severity={alert.severity}
          sx={{ width: '100%' }}
        >
          {alert.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}
