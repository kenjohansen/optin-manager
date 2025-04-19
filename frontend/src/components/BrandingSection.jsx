import { Box, Typography, Stack, TextField, Button } from '@mui/material';

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
