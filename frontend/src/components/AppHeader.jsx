import { AppBar, Toolbar, Typography, IconButton, Box, Button, useTheme, useMediaQuery, Drawer, List, ListItem, ListItemButton, ListItemText, Divider } from '@mui/material';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import MenuIcon from '@mui/icons-material/Menu';
import { Link } from 'react-router-dom';
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { isAdmin, isAuthenticated } from '../utils/auth';

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

  const token = localStorage.getItem('access_token');
  const userIsAdmin = isAdmin(token);
  const userIsAuthenticated = isAuthenticated(token);

  const filteredLinks = navLinks.filter(link => {
    if (link.always) return true;
    if (link.label === 'Opt-Out') return true;
    if (link.label === 'Login') return !userIsAuthenticated;
    if (link.adminOnly) return userIsAdmin;
    if ([
      'Dashboard',
      'Customization',
      'Opt-Ins',
      'Contacts',
      'Verbal Opt-in',
    ].includes(link.label)) {
      return userIsAuthenticated;
    }
    return false;
  });

  const isSmallScreen = useMediaQuery(theme.breakpoints.down('md'));
  const [drawerOpen, setDrawerOpen] = useState(false);

  const handleDrawerToggle = () => setDrawerOpen(open => !open);
  const handleDrawerClose = () => setDrawerOpen(false);

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
        {isSmallScreen ? (
          <>
            <IconButton color="inherit" edge="end" onClick={handleDrawerToggle}>
              <MenuIcon />
            </IconButton>
            <Drawer anchor="right" open={drawerOpen} onClose={handleDrawerClose}>
              <Box sx={{ width: 220 }} role="presentation" onClick={handleDrawerClose}>
                <List>
                  {filteredLinks.map(link => (
                    <ListItem key={link.path} disablePadding>
                      <ListItemButton component={Link} to={link.path}>
                        <ListItemText primary={link.label} />
                      </ListItemButton>
                    </ListItem>
                  ))}
                </List>
                <Divider />
                {isAuthenticated && (
                  <List>
                    <ListItem disablePadding>
                      <ListItemButton onClick={handleLogout}>
                        <ListItemText primary="Logout" />
                      </ListItemButton>
                    </ListItem>
                  </List>
                )}
                <Divider />
                <Box display="flex" justifyContent="center" alignItems="center" py={1}>
                  <IconButton color="inherit" onClick={handleThemeToggle}>
                    {themeIcon}
                  </IconButton>
                </Box>
              </Box>
            </Drawer>
          </>
        ) : (
          <>
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
          </>
        )}
      </Toolbar>
    </AppBar>
  );
}
