/**
 * App.jsx
 *
 * Main application component for the OptIn Manager frontend.
 *
 * This component serves as the entry point for the OptIn Manager application,
 * handling routing, theme management, and authentication state. It implements
 * role-based access control as specified in the requirements, where:
 * - Admin users can access all pages including user management
 * - Support users can view all pages but cannot manage users
 * - Non-authenticated users can only access the Opt-Out page and login
 *
 * The component fetches and applies customization settings (branding, colors)
 * from the backend to ensure consistent visual identity.
 *
 * Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
 * This file is part of the OptIn Manager project and is licensed under the MIT License.
 * See the root LICENSE file for details.
 */

import { useMemo, useState } from 'react';
import { Box, Container, ThemeProvider, CssBaseline, alpha } from '@mui/material';
import { getTheme } from './theme';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

import AppHeader from './components/AppHeader';
import AdminLogin from './pages/AdminLogin';
import Customization from './pages/Customization';
import Dashboard from './pages/Dashboard';
import ContactOptOut from './pages/ContactOptOut';
import OptInSetup from './pages/OptInSetup';
import ContactDashboard from './pages/ContactDashboard';
import UserManagement from './pages/UserManagement';
import VerbalOptIn from './pages/VerbalOptIn';
import ForgotPassword from './pages/ForgotPassword';
import ChangePassword from './pages/ChangePassword';
import ProtectedRoute from './components/ProtectedRoute';

/**
 * Navigation links configuration for the application header.
 * 
 * This array defines the navigation structure of the application, with special
 * properties to control access based on user roles. The 'adminOnly' flag ensures
 * that certain pages (like user management) are only accessible to administrators,
 * implementing the role-based access control requirements.
 */
const navLinks = [
  { label: 'Dashboard', path: '/dashboard' },
  { label: 'Customization', path: '/customization' },
  { label: 'Opt-Ins', path: '/optins' },
  { label: 'Contacts', path: '/contacts' },
  { label: 'Verbal Opt-in', path: '/verbal-optin' },
  { label: 'Users', path: '/users', adminOnly: true },
  { label: 'Preferences', path: '/preferences' },
  { label: 'Login', path: '/login' },
];

import { useEffect } from 'react';
import { fetchCustomization } from './api';

/**
 * Main application component that handles routing, theme, and authentication state.
 * 
 * This component:
 * 1. Manages authentication state and user roles
 * 2. Fetches and applies customization settings from the backend
 * 3. Implements protected routes based on authentication status and user role
 * 4. Provides theme customization based on user preferences and brand settings
 * 
 * The component structure ensures that non-authenticated users can only access
 * the Opt-Out page and login page, while authenticated users can access different
 * pages based on their role (admin or support).
 * 
 * @returns {JSX.Element} The rendered application with routing and theming
 */
function App() {
  // Theme state: system, light, dark
  const [mode, setMode] = useState('system');
  // These come from backend customization API
  const [primary, setPrimary] = useState('');
  const [secondary, setSecondary] = useState('');
  const [logoUrl, setLogoUrl] = useState(null);
  const [companyName, setCompanyName] = useState('');
  const [privacyPolicy, setPrivacyPolicy] = useState('');

  // Fetch customization on initial app load
  useEffect(() => {
    fetchCustomization().then(data => {
      if (data) {
        // Handle logo URL - ensure it has the backend domain and cache busting
        if (data.logo_url) {
          let logoUrl = data.logo_url;
          // Check if the URL is a relative path (starts with /) and doesn't already contain the backend origin
          if (logoUrl && logoUrl.startsWith('/') && !logoUrl.includes('://')) {
            // Get the backend origin from the API_BASE
            const API_BASE = 'http://127.0.0.1:8000/api/v1';
            let backendOrigin = API_BASE.replace(/\/api\/v1\/?$/, '');
            logoUrl = backendOrigin + logoUrl;
          }
          
          // Add cache-busting timestamp to prevent browser caching
          const timestamp = new Date().getTime();
          logoUrl = `${logoUrl}?t=${timestamp}`;
          
          console.log('App: Setting logo URL with cache busting:', logoUrl);
          setLogoUrl(logoUrl);
        } else {
          setLogoUrl(null);
        }
        
        setPrimary(data.primary_color || '');
        setSecondary(data.secondary_color || '');
        setCompanyName(data.company_name || '');
        setPrivacyPolicy(data.privacy_policy_url || '');
      }
    }).catch(e => {
      console.error('Error fetching customization in App:', e);
      // Optionally log or show error
      console.warn('Failed to fetch customization:', e);
    });
  }, []);

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
              <Route path="/forgot-password" element={<ForgotPassword />} />
              <Route path="/change-password" element={<ProtectedRoute><ChangePassword /></ProtectedRoute>} />
              {/* Redirect /optout to /preferences for backward compatibility */}
              <Route path="/optout" element={<Navigate to="/preferences" replace />} />
              {/* Preferences page is accessible to everyone */}
              <Route path="/preferences" element={<ContactOptOut mode="preferences" />} />
              {/* Verbal Opt-in is only for authenticated users */}
              <Route path="/verbal-optin" element={<ProtectedRoute><VerbalOptIn /></ProtectedRoute>} />
              <Route path="/optins" element={<ProtectedRoute><OptInSetup /></ProtectedRoute>} />
              <Route path="/customization" element={<ProtectedRoute><Customization setLogoUrl={setLogoUrl} setPrimary={setPrimary} setSecondary={setSecondary} setCompanyName={setCompanyName} setPrivacyPolicy={setPrivacyPolicy} /></ProtectedRoute>} />
              <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
              <Route path="/contacts" element={<ProtectedRoute><ContactDashboard /></ProtectedRoute>} />
              <Route path="/users" element={<ProtectedRoute><UserManagement /></ProtectedRoute>} />
              <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
              <Route path="*" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
            </Routes>
          </Box>
        </Box>
        <Box component="footer" sx={{
          p: 2,
          textAlign: 'center',
          bgcolor: (theme) => alpha(theme.palette.secondary.main, 0.5),
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
