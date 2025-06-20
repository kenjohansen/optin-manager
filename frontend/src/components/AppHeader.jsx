/**
 * AppHeader.jsx
 *
 * Application header component with navigation and user controls.
 *
 * This component implements the main navigation header for the OptIn Manager
 * application, including the responsive menu system, user authentication controls,
 * and theme switching functionality. It dynamically adjusts its display based on
 * the user's authentication status and role.
 *
 * As noted in the memories, the system supports two roles for authenticated users:
 * - Admin: Can access all pages including user management
 * - Support: Can view all pages but cannot manage users
 * 
 * Non-authenticated users can only see the Opt-Out page, the Login menu,
 * and the light/dark mode icon. This component enforces these visibility rules
 * for the navigation links.
 *
 * Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
 * This file is part of the OptIn Manager project and is licensed under the MIT License.
 * See the root LICENSE file for details.
 */

import { AppBar, Toolbar, Typography, IconButton, Box, Button, useTheme, useMediaQuery, Drawer, List, ListItem, ListItemButton, ListItemText, Divider, Chip, Avatar, Menu, MenuItem, ListItemIcon } from '@mui/material';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import MenuIcon from '@mui/icons-material/Menu';
import LogoutIcon from '@mui/icons-material/Logout';
import LockIcon from '@mui/icons-material/Lock';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import { Link } from 'react-router-dom';
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { isAdmin, isAuthenticated as checkAuthentication, parseJwt } from '../utils/auth';

/**
 * Application header component with navigation and user controls.
 * 
 * This component serves as the main navigation interface for the application,
 * adapting its display based on screen size (desktop/mobile), user authentication
 * status, and user role. It implements the role-based access control requirements
 * by filtering navigation options based on the user's permissions.
 * 
 * Key features:
 * - Responsive design with collapsible menu for mobile devices
 * - Dynamic navigation links based on user authentication and role
 * - Theme switching between light, dark, and system modes
 * - User profile menu with authentication actions
 * - Organization branding through customizable logo
 * 
 * @param {Object} props - Component props
 * @param {string} props.mode - Current theme mode ('light', 'dark', or 'system')
 * @param {Function} props.setMode - Function to update the theme mode
 * @param {string} props.logoUrl - URL to the organization's logo image
 * @param {Array} props.navLinks - Navigation link configuration objects
 * @returns {JSX.Element} The rendered header component
 */
export default function AppHeader({ mode, setMode, logoUrl, navLinks = [] }) {
  const [anchorEl, setAnchorEl] = useState(null);
  const open = Boolean(anchorEl);
  
  /**
   * Handles opening the user menu dropdown
   * @param {React.MouseEvent} event - The click event
   */
  const handleUserMenuClick = (event) => {
    setAnchorEl(event.currentTarget);
  };
  
  /**
   * Handles closing the user menu dropdown
   */
  const handleUserMenuClose = () => {
    setAnchorEl(null);
  };
  const theme = useTheme();
  const navigate = useNavigate();
  
  /**
   * Cycles through theme modes: light → dark → system
   */
  const handleThemeToggle = () => {
    setMode(prev =>
      prev === 'light' ? 'dark' : prev === 'dark' ? 'system' : 'light'
    );
  };
  const themeIcon = theme.palette.mode === 'dark' ? <Brightness7Icon /> : <Brightness4Icon />;
  const isAuthenticatedLocal = !!localStorage.getItem('access_token');
  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('username');
    localStorage.removeItem('email');
    handleUserMenuClose();
    navigate('/login');
  };
  
  const handleChangePassword = () => {
    handleUserMenuClose();
    navigate('/change-password');
  };

  const token = localStorage.getItem('access_token');
  const userIsAdmin = isAdmin(token);
  const userIsAuthenticated = checkAuthentication(token);

  // PRD-compliant: Unauthenticated users see Preferences (ContactOptOut) and Login only
  const filteredLinks = navLinks.filter(link => {
    if (link.always) return true;
    if (!userIsAuthenticated) {
      return link.label === 'Preferences' || link.label === 'Login';
    }
    if (link.adminOnly) return userIsAdmin;
    // Authenticated users: show all except Preferences/Login
    if ([
      'Dashboard',
      'Customization',
      'Opt-Ins',
      'Contacts',
      'Verbal Opt-in',
    ].includes(link.label)) {
      return true;
    }
    return false;
  });

  // Get user info from token
  const getUserInfo = () => {
    const token = localStorage.getItem('access_token');
    if (!token) return { name: '', username: '' };
    
    const payload = parseJwt(token);
    if (!payload) return { name: '', username: '' };
    
    return {
      name: payload.name || payload.sub || '',
      username: payload.sub || ''
    };
  };
  
  const userInfo = getUserInfo();
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
                {isAuthenticatedLocal && (
                  <>
                    <Box sx={{ p: 2, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <Chip
                        avatar={<Avatar>{userInfo.name.charAt(0).toUpperCase()}</Avatar>}
                        label={userInfo.name || userInfo.username}
                        color="secondary"
                        sx={{ width: '100%' }}
                        onClick={handleUserMenuClose}
                      />
                    </Box>
                    <List>
                      <ListItem disablePadding>
                        <ListItemButton onClick={handleChangePassword}>
                          <ListItemIcon>
                            <LockIcon fontSize="small" />
                          </ListItemIcon>
                          <ListItemText primary="Change Password" />
                        </ListItemButton>
                      </ListItem>
                      <ListItem disablePadding>
                        <ListItemButton onClick={handleLogout}>
                          <ListItemIcon>
                            <LogoutIcon fontSize="small" />
                          </ListItemIcon>
                          <ListItemText primary="Logout" />
                        </ListItemButton>
                      </ListItem>
                    </List>
                  </>
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
            {isAuthenticatedLocal && (
              <>
                <Chip
                  avatar={<Avatar>{userInfo.name.charAt(0).toUpperCase()}</Avatar>}
                  label={userInfo.name || userInfo.username}
                  color="secondary"
                  variant="outlined"
                  onClick={handleUserMenuClick}
                  deleteIcon={<KeyboardArrowDownIcon />}
                  onDelete={handleUserMenuClick}
                  sx={{ 
                    ml: 1, 
                    bgcolor: 'rgba(255,255,255,0.1)',
                    cursor: 'pointer',
                    '& .MuiChip-deleteIcon': {
                      color: 'inherit',
                    }
                  }}
                />
                <Menu
                  anchorEl={anchorEl}
                  open={open}
                  onClose={handleUserMenuClose}
                  MenuListProps={{
                    'aria-labelledby': 'user-menu-button',
                  }}
                >
                  <MenuItem onClick={handleChangePassword}>
                    <ListItemIcon>
                      <LockIcon fontSize="small" />
                    </ListItemIcon>
                    Change Password
                  </MenuItem>
                  <MenuItem onClick={handleLogout}>
                    <ListItemIcon>
                      <LogoutIcon fontSize="small" />
                    </ListItemIcon>
                    Logout
                  </MenuItem>
                </Menu>
              </>
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
