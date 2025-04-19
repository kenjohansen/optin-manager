import { useMemo, useState } from 'react';
import { ThemeProvider, CssBaseline, Box } from '@mui/material';
import { getTheme } from './theme';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

import AppHeader from './components/AppHeader';
import AdminLogin from './pages/AdminLogin';
import Customization from './pages/Customization';
import Dashboard from './pages/Dashboard';
import ContactOptOut from './pages/ContactOptOut';
import CampaignSetup from './pages/CampaignSetup';
import ProductSetup from './pages/ProductSetup';
import ContactDashboard from './pages/ContactDashboard';
import ProtectedRoute from './components/ProtectedRoute';

const navLinks = [
  { label: 'Dashboard', path: '/dashboard' },
  { label: 'Customization', path: '/customization' },
  { label: 'Campaigns', path: '/campaigns' },
  { label: 'Products', path: '/products' },
  { label: 'Contacts', path: '/contacts' },
  { label: 'Opt-Out', path: '/optout' },
  { label: 'Login', path: '/login' },
];


function App() {
  // Theme state: system, light, dark
  const [mode, setMode] = useState('system');
  // These come from backend customization API
  const [primary, setPrimary] = useState('');
  const [secondary, setSecondary] = useState('');
  const [logoUrl, setLogoUrl] = useState(null);
  const [companyName, setCompanyName] = useState('');
  const [privacyPolicy, setPrivacyPolicy] = useState('');

  // Detect system theme if 'system' selected
  const actualMode = mode === 'system'
    ? (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
    : mode;
  const theme = useMemo(() => getTheme(actualMode, primary, secondary), [actualMode, primary, secondary]);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <AppHeader mode={mode} setMode={setMode} logoUrl={logoUrl} navLinks={navLinks} />
        <Box
          sx={{
            minHeight: '90vh',
            background: theme.palette.background.default,
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'flex-start',
            width: '100%',
            pt: { xs: 7, sm: 8 }, // Add top padding for fixed AppBar
          }}
        >
          <Box sx={{ width: '100%' }}>
            <Routes>
              <Route path="/login" element={<AdminLogin />} />
              <Route path="/optout" element={<ContactOptOut />} />
              <Route path="/customization" element={<ProtectedRoute><Customization setLogoUrl={setLogoUrl} setPrimary={setPrimary} setSecondary={setSecondary} setCompanyName={setCompanyName} setPrivacyPolicy={setPrivacyPolicy} /></ProtectedRoute>} />
              <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
              <Route path="/campaigns" element={<ProtectedRoute><CampaignSetup /></ProtectedRoute>} />
              <Route path="/products" element={<ProtectedRoute><ProductSetup /></ProtectedRoute>} />
              <Route path="/contacts" element={<ProtectedRoute><ContactDashboard /></ProtectedRoute>} />
              <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
              <Route path="*" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
            </Routes>
          </Box>
        </Box>
        <Box component="footer" sx={{
          p: 2,
          textAlign: 'center',
          bgcolor: 'background.paper',
          borderTop: 1,
          borderColor: 'divider',
          width: '100vw',
          position: 'fixed',
          left: 0,
          bottom: 0,
          zIndex: 1201
        }}>
          <span style={{ color: '#888' }}>
            OptIn Manager &copy; {new Date().getFullYear()} {companyName && `— ${companyName}`}
            {privacyPolicy && (
              <>
                {' | '}
                <a href={privacyPolicy} target="_blank" rel="noopener noreferrer" style={{ color: '#888', textDecoration: 'underline' }}>
                  Privacy Policy
                </a>
              </>
            )}
          </span>
        </Box>
      </Router>
    </ThemeProvider>
  );
}


export default App;
