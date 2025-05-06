import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Button, 
  Paper, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  IconButton,
  Chip,
  Alert,
  Snackbar
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import LockResetIcon from '@mui/icons-material/LockReset';
import axios from 'axios';
import { isAdmin } from '../utils/auth';
import { API_BASE } from '../api';

const UserManagement = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [dialogMode, setDialogMode] = useState('create'); // 'create' or 'edit'
  const [currentUser, setCurrentUser] = useState(null);
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    name: '',
    email: '',
    role: 'support', // Default role is support
    is_active: true
  });
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success'
  });

  const token = localStorage.getItem('access_token');
  const userIsAdmin = isAdmin(token);

  // Fetch users on component mount
  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/auth_users/`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch users');
      }
      
      const data = await response.json();
      setUsers(data);
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
      showSnackbar('Error fetching users', 'error');
    }
  };

  const handleOpenDialog = (mode, user = null) => {
    setDialogMode(mode);
    if (mode === 'edit' && user) {
      setCurrentUser(user);
      setFormData({
        username: user.username,
        password: '', // Don't show password in edit mode
        name: user.name || '',
        email: user.email || '',
        role: user.role,
        is_active: user.is_active
      });
    } else {
      setCurrentUser(null);
      setFormData({
        username: '',
        password: '',
        name: '',
        email: '',
        role: 'support',
        is_active: true
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
  };

  const handleInputChange = (e) => {
    const { name, value, checked } = e.target;
    setFormData({
      ...formData,
      [name]: name === 'is_active' ? checked : value
    });
  };

  const handleSubmit = async () => {
    try {
      let response;
      let payload = { ...formData };
      
      // For edit mode, only include password if it was changed
      if (dialogMode === 'edit' && !payload.password) {
        delete payload.password;
      }

      if (dialogMode === 'create') {
        response = await fetch(`${API_BASE}/auth_users/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify(payload)
        });
      } else {
        response = await fetch(`${API_BASE}/auth_users/${currentUser.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify(payload)
        });
      }

      if (!response.ok) {
        throw new Error(`Failed to ${dialogMode} user`);
      }

      handleCloseDialog();
      fetchUsers();
      showSnackbar(`User ${dialogMode === 'create' ? 'created' : 'updated'} successfully`, 'success');
    } catch (err) {
      showSnackbar(err.message, 'error');
    }
  };

  const handleDeleteUser = async (userId) => {
    if (!window.confirm('Are you sure you want to delete this user?')) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/auth_users/${userId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to delete user');
      }

      fetchUsers();
      showSnackbar('User deleted successfully', 'success');
    } catch (err) {
      showSnackbar(err.message, 'error');
    }
  };
  
  const handleForcePasswordReset = async (user) => {
    if (!window.confirm(`Are you sure you want to force a password reset for ${user.username}?`)) {
      return;
    }
    
    try {
      const response = await axios.post(
        `${API_BASE}/auth/reset-password`,
        { username: user.username },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      showSnackbar(`Password reset initiated for ${user.username}. They will receive an email with instructions.`, 'success');
    } catch (err) {
      showSnackbar(err.response?.data?.detail || 'Failed to reset password', 'error');
    }
  };

  const showSnackbar = (message, severity = 'success') => {
    setSnackbar({
      open: true,
      message,
      severity
    });
  };

  const handleCloseSnackbar = () => {
    setSnackbar({
      ...snackbar,
      open: false
    });
  };

  // If not admin, show access denied
  if (!userIsAdmin) {
    return (
      <Box sx={{ width: '90vw', margin: 'auto', mt: 4 }}>
        <Alert severity="error">
          Access Denied - You must have admin privileges to manage users.
        </Alert>
      </Box>
    );
  }

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
      <Paper elevation={3} sx={{ p: 3, width: '90%', mx: 'auto' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          User Management
        </Typography>
        <Button 
          variant="contained" 
          color="primary" 
          onClick={() => handleOpenDialog('create')}
        >
          Add New User
        </Button>
      </Box>

      {loading ? (
        <Typography>Loading users...</Typography>
      ) : error ? (
        <Alert severity="error">{error}</Alert>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Username</TableCell>
                <TableCell>Name</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Role</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Created At</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {users.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} align="center">No users found</TableCell>
                </TableRow>
              ) : (
                users.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell>{user.username}</TableCell>
                    <TableCell>{user.name || '-'}</TableCell>
                    <TableCell>{user.email || '-'}</TableCell>
                    <TableCell>
                      <Chip 
                        label={user.role} 
                        color={user.role === 'admin' ? 'primary' : 'default'} 
                        variant={user.role === 'admin' ? 'filled' : 'outlined'}
                      />
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={user.is_active ? 'Active' : 'Inactive'} 
                        color={user.is_active ? 'success' : 'error'} 
                      />
                    </TableCell>
                    <TableCell>
                      {user.created_at ? new Date(user.created_at).toLocaleDateString() : '-'}
                    </TableCell>
                    <TableCell>
                      <IconButton 
                        color="primary" 
                        onClick={() => handleOpenDialog('edit', user)}
                        title="Edit User"
                      >
                        <EditIcon />
                      </IconButton>
                      <IconButton 
                        color="secondary" 
                        onClick={() => handleForcePasswordReset(user)}
                        title="Force Password Reset"
                      >
                        <LockResetIcon />
                      </IconButton>
                      <IconButton 
                        color="error" 
                        onClick={() => handleDeleteUser(user.id)}
                        title="Delete User"
                      >
                        <DeleteIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Create/Edit User Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {dialogMode === 'create' ? 'Create New User' : 'Edit User'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              label="Username"
              name="username"
              value={formData.username}
              onChange={handleInputChange}
              fullWidth
              required
              disabled={dialogMode === 'edit'} // Username cannot be changed in edit mode
            />
            <TextField
              label="Password"
              name="password"
              type="password"
              value={formData.password}
              onChange={handleInputChange}
              fullWidth
              required={dialogMode === 'create'} // Password is required only in create mode
              helperText={dialogMode === 'edit' ? 'Leave blank to keep current password' : ''}
            />
            <TextField
              label="Full Name"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              fullWidth
              placeholder="John Doe"
            />
            <TextField
              label="Email Address"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleInputChange}
              fullWidth
              placeholder="john.doe@example.com"
            />
            <FormControl fullWidth>
              <InputLabel>Role</InputLabel>
              <Select
                name="role"
                value={formData.role}
                onChange={handleInputChange}
                label="Role"
              >
                <MenuItem value="admin">Admin</MenuItem>
                <MenuItem value="support">Support</MenuItem>
              </Select>
            </FormControl>
            <FormControl fullWidth>
              <InputLabel>Status</InputLabel>
              <Select
                name="is_active"
                value={formData.is_active}
                onChange={handleInputChange}
                label="Status"
              >
                <MenuItem value={true}>Active</MenuItem>
                <MenuItem value={false}>Inactive</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog} color="inherit">Cancel</Button>
          <Button onClick={handleSubmit} color="primary" variant="contained">
            {dialogMode === 'create' ? 'Create' : 'Update'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity}>
          {snackbar.message}
        </Alert>
      </Snackbar>
      </Paper>
    </Box>
  );
};

export default UserManagement;
