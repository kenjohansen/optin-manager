/**
 * BrandingSection.jsx
 *
 * Branding customization form component.
 *
 * This component provides a form interface for administrators to customize the
 * application's branding elements, including company name, logo, colors, and
 * privacy policy URL. These customization settings are essential for allowing
 * organizations to match the OptIn Manager interface to their brand identity.
 *
 * As noted in the memories, this supports the UI branding elements that are part
 * of the customization settings, which are essential for consistent user experience.
 *
 * Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
 * This file is part of the OptIn Manager project and is licensed under the MIT License.
 * See the root LICENSE file for details.
 */

import { Box, Typography, Stack, TextField, Button } from '@mui/material';

/**
 * Branding section component for customization settings.
 * 
 * This component renders a form that allows administrators to customize the
 * application's branding elements. It handles logo uploads, color selection,
 * company name, and privacy policy URL settings. These customizations are stored
 * in the backend and applied throughout the application to maintain consistent
 * branding.
 * 
 * @param {Object} props - Component props
 * @param {string} props.logoPreview - URL for the logo preview image
 * @param {Function} props.handleLogoChange - Handler for logo file selection
 * @param {string} props.companyName - Organization name
 * @param {Function} props.setCompanyName - Function to update company name
 * @param {string} props.privacyPolicy - Privacy policy URL
 * @param {Function} props.setPrivacyPolicy - Function to update privacy policy URL
 * @param {string} props.primary - Primary brand color in hex format
 * @param {Function} props.setPrimary - Function to update primary color
 * @param {string} props.secondary - Secondary brand color in hex format
 * @param {Function} props.setSecondary - Function to update secondary color
 * @param {boolean} props.saving - Whether a save operation is in progress
 * @param {Function} props.handleSave - Form submission handler
 * @returns {JSX.Element} The rendered branding form
 */
export default function BrandingSection({
  logoPreview, handleLogoChange, companyName, setCompanyName, privacyPolicy, setPrivacyPolicy, primary, setPrimary, secondary, setSecondary, saving, handleSave
}) {
  return (
    <Box mb={4}>
      <Typography variant="h6" mb={2}>Branding</Typography>
      <form onSubmit={handleSave}>
        <Stack spacing={2} alignItems="center">
          <TextField label="Company Name" value={companyName} onChange={e => setCompanyName(e.target.value)} fullWidth />
          <TextField label="Privacy Policy URL" value={privacyPolicy} onChange={e => setPrivacyPolicy(e.target.value)} fullWidth />
          {logoPreview && (
            <Box mt={2} display="flex" justifyContent="center">
              <img src={logoPreview} alt="Logo Preview" style={{ maxWidth: 120, maxHeight: 80, width: '100%', objectFit: 'contain' }} />
            </Box>
          )}
          <Button variant="contained" component="label" sx={{ width: { xs: '100%', sm: 'auto' } }}>
            Upload Logo
            <input type="file" accept="image/*" hidden onChange={handleLogoChange} />
          </Button>
          <TextField label="Primary Color" type="color" value={primary} onChange={e => setPrimary(e.target.value)} InputLabelProps={{ shrink: true }} fullWidth />
          <TextField label="Secondary Color" type="color" value={secondary} onChange={e => setSecondary(e.target.value)} InputLabelProps={{ shrink: true }} fullWidth />
          <Button type="submit" variant="contained" color="primary" disabled={saving} fullWidth sx={{ mt: 1 }}>
            {saving ? 'Saving...' : 'Save'}
          </Button>
        </Stack>
      </form>
    </Box>
  );
}
