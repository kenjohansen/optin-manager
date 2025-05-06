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

export default function AppHeader({ mode, setMode, logoUrl, navLinks = [] }) {
  const [anchorEl, setAnchorEl] = useState(null);
  const open = Boolean(anchorEl);
  
  const handleUserMenuClick = (event) => {
    setAnchorEl(event.currentTarget);
  };
  
  const handleUserMenuClose = () => {
    setAnchorEl(null);
  };
  const theme = useTheme();
  const navigate = useNavigate();
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

  const filteredLinks = navLinks.filter(link => {
    if (link.always) return true;
    if (link.label === 'Opt-Out') return !userIsAuthenticated; // Hide Preferences when logged in
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
