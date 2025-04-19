import { AppBar, Toolbar, Typography, IconButton, Box, Button, useTheme } from '@mui/material';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import { Link } from 'react-router-dom';

import { useNavigate } from 'react-router-dom';

export default function AppHeader({ mode, setMode, logoUrl, navLinks = [] }) {
  const theme = useTheme();
  const navigate = useNavigate();
  const handleThemeToggle = () => {
    setMode(prev =>
      prev === 'light' ? 'dark' : prev === 'dark' ? 'system' : 'light'
    );
  };
  const themeIcon = theme.palette.mode === 'dark' ? <Brightness7Icon /> : <Brightness4Icon />;
  const isAuthenticated = !!localStorage.getItem('access_token');
  const handleLogout = () => {
    localStorage.removeItem('access_token');
    navigate('/login');
  };

  const filteredLinks = navLinks.filter(link => {
    if (link.label === 'Opt-Out') return true;
    if (link.label === 'Login') return !isAuthenticated;
    if ([
      'Dashboard',
      'Customization',
      'Campaigns',
      'Products',
      'Contacts',
    ].includes(link.label)) {
      return isAuthenticated;
    }
    return false;
  });

  return (
    <AppBar position="fixed" color="primary" enableColorOnDark sx={{ width: '100vw', left: 0 }}>
      <Toolbar>
        {logoUrl && (
          <Box mr={2}>
            <img src={logoUrl} alt="Logo" style={{ height: 36, verticalAlign: 'middle' }} />
          </Box>
        )}
        <Typography variant="h6" sx={{ flexGrow: 1 }} component={Link} to="/" color="inherit" style={{ textDecoration: 'none' }}>
          OptIn Manager
        </Typography>
        {filteredLinks.map(link => (
          <Button key={link.path} color="inherit" component={Link} to={link.path} sx={{ ml: 1 }}>
            {link.label}
          </Button>
        ))}
        {isAuthenticated && (
          <Button color="inherit" onClick={handleLogout} sx={{ ml: 1 }}>Logout</Button>
        )}
        <IconButton color="inherit" onClick={handleThemeToggle} sx={{ ml: 1 }}>
          {themeIcon}
        </IconButton>
      </Toolbar>
    </AppBar>
  );
}
