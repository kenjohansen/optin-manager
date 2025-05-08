/**
 * UserManagement.test.jsx
 * 
 * Unit tests for the UserManagement component.
 * 
 * These tests verify that the UserManagement component correctly renders,
 * handles role-based access control, and provides user management functionality.
 */

import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import UserManagement from './UserManagement';
import * as auth from '../utils/auth';
import axios from 'axios';
import { API_BASE } from '../api';

// Mock axios
jest.mock('axios');

// Mock window.confirm
window.confirm = jest.fn();

// Mock fetch
global.fetch = jest.fn();

// Mock localStorage
Object.defineProperty(window, 'localStorage', {
  value: {
    getItem: jest.fn(() => 'mock-token'),
    setItem: jest.fn(),
    removeItem: jest.fn()
  },
  writable: true
});

// Mock auth util
jest.mock('../utils/auth', () => ({
  isAdmin: jest.fn(() => true)
}));

// Mock user data
const mockUsers = [
  {
    id: 1,
    username: 'admin',
    name: 'Admin User',
    email: 'admin@example.com',
    role: 'admin',
    is_active: true,
    created_at: '2023-01-01T00:00:00Z'
  },
  {
    id: 2,
    username: 'support',
    name: 'Support User',
    email: 'support@example.com',
    role: 'support',
    is_active: true,
    created_at: '2023-01-02T00:00:00Z'
  }
];

describe('UserManagement Component', () => {
  beforeEach(() => {
    // Reset all mocks
    jest.clearAllMocks();
    
    // Mock successful fetch response for users
    global.fetch.mockImplementation(() => {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockUsers)
      });
    });
    
    // Mock axios implementation
    axios.post.mockResolvedValue({ data: { success: true } });
  });

  test('renders access denied message for non-admin users', () => {
    // Override the mock for this specific test
    const isAdmin = require('../utils/auth').isAdmin;
    isAdmin.mockReturnValueOnce(false);
    
    render(
      <MemoryRouter>
        <UserManagement />
      </MemoryRouter>
    );
    
    // Check for access denied message
    expect(screen.getByText(/access denied/i)).toBeInTheDocument();
  });

  test('renders user management page', async () => {
    render(
      <MemoryRouter>
        <UserManagement />
      </MemoryRouter>
    );
    
    // Verify fetch was called
    expect(global.fetch).toHaveBeenCalledWith(
      `${API_BASE}/auth_users/`,
      expect.objectContaining({
        headers: expect.any(Object)
      })
    );
    
    // Wait for users to be loaded
    await waitFor(() => {
      expect(screen.queryByText(/Loading users/i)).not.toBeInTheDocument();
    });
    
    // Check that Add New User button is present
    expect(screen.getByText(/Add New Authorized User/i)).toBeInTheDocument();
  });

  test('shows loading state while fetching users', async () => {
    // Mock a delayed response
    global.fetch.mockImplementationOnce(() => {
      return new Promise(resolve => {
        setTimeout(() => {
          resolve({
            ok: true,
            json: () => Promise.resolve(mockUsers)
          });
        }, 100);
      });
    });
    
    render(
      <MemoryRouter>
        <UserManagement />
      </MemoryRouter>
    );
    
    // Check for loading message
    expect(screen.getByText(/Loading users/i)).toBeInTheDocument();
    
    // Wait for users to be loaded
    await waitFor(() => {
      expect(screen.queryByText(/Loading users/i)).not.toBeInTheDocument();
    });
  });

  test('opens user dialog when Add New User button is clicked', async () => {
    render(
      <MemoryRouter>
        <UserManagement />
      </MemoryRouter>
    );
    
    // Wait for users to load
    await waitFor(() => {
      expect(screen.queryByText(/Loading users/i)).not.toBeInTheDocument();
    });
    
    // Click the Add New User button
    fireEvent.click(screen.getByText(/Add New Authorized User/i));
    
    // Check that dialog is opened (look for dialog role)
    expect(screen.getByRole('dialog')).toBeInTheDocument();
  });

  test('handles dialog open and close', async () => {
    render(
      <MemoryRouter>
        <UserManagement />
      </MemoryRouter>
    );
    
    // Wait for users to load
    await waitFor(() => {
      expect(screen.queryByText(/Loading users/i)).not.toBeInTheDocument();
    });
    
    // Click the Add New User button
    fireEvent.click(screen.getByText(/Add New Authorized User/i));
    
    // Verify dialog is open
    const dialog = screen.getByRole('dialog');
    expect(dialog).toBeInTheDocument();
    
    // Find and click the Cancel button
    const cancelButton = screen.getByRole('button', { name: /cancel/i });
    fireEvent.click(cancelButton);
    
    // Verify dialog is closed
    await waitFor(() => {
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    });
  });

  test('verifies fetch is called correctly', async () => {
    render(
      <MemoryRouter>
        <UserManagement />
      </MemoryRouter>
    );
    
    // Wait for users to load
    await waitFor(() => {
      expect(screen.queryByText(/Loading users/i)).not.toBeInTheDocument();
    });
    
    // Verify that fetch was called with the correct URL
    expect(global.fetch).toHaveBeenCalledWith(
      `${API_BASE}/auth_users/`,
      expect.any(Object)
    );
  });

  test('verifies axios is properly mocked', async () => {
    // Mock axios.post implementation
    axios.post.mockResolvedValue({ data: { success: true } });
    
    render(
      <MemoryRouter>
        <UserManagement />
      </MemoryRouter>
    );
    
    // Wait for users to load
    await waitFor(() => {
      expect(screen.queryByText(/Loading users/i)).not.toBeInTheDocument();
    });
    
    // Verify that axios is properly mocked
    expect(axios.post).toBeDefined();
    expect(axios.post).toHaveBeenCalledTimes(0); // Should not be called yet
  });

  test('verifies user data is displayed', async () => {
    render(
      <MemoryRouter>
        <UserManagement />
      </MemoryRouter>
    );
    
    // Wait for loading to finish
    await waitFor(() => {
      expect(screen.queryByText(/Loading users/i)).not.toBeInTheDocument();
    });
    
    // Check for user table headers
    expect(screen.getByText('Username')).toBeInTheDocument();
    expect(screen.getByText('Name')).toBeInTheDocument();
    expect(screen.getByText('Email')).toBeInTheDocument();
    expect(screen.getByText('Role')).toBeInTheDocument();
    expect(screen.getByText('Status')).toBeInTheDocument();
    expect(screen.getByText('Created At')).toBeInTheDocument();
    expect(screen.getByText('Actions')).toBeInTheDocument();
    
    // Check that user data is displayed in the table
    const tableRows = screen.getAllByRole('row');
    expect(tableRows.length).toBeGreaterThan(1); // Header row + at least one data row
    
    // Verify email addresses are displayed (these are unique in the table)
    expect(screen.getByText('admin@example.com')).toBeInTheDocument();
    expect(screen.getByText('support@example.com')).toBeInTheDocument();
  });

  test('handles error when fetching users fails', async () => {
    // Mock a failed response for fetching users
    global.fetch.mockImplementationOnce(() => {
      return Promise.resolve({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error'
      });
    });
    
    render(
      <MemoryRouter>
        <UserManagement />
      </MemoryRouter>
    );
    
    // Wait for loading to finish
    await waitFor(() => {
      expect(screen.queryByText(/Loading users/i)).not.toBeInTheDocument();
    });
    
    // Verify the error state
    expect(screen.getByText(/Error fetching users/i)).toBeInTheDocument();
  });
  
  test('displays loading state initially', async () => {
    // Delay the fetch response to ensure loading state is visible
    global.fetch.mockImplementationOnce(() => {
      return new Promise(resolve => {
        setTimeout(() => {
          resolve({
            ok: true,
            json: () => Promise.resolve(mockUsers)
          });
        }, 100);
      });
    });
    
    render(
      <MemoryRouter>
        <UserManagement />
      </MemoryRouter>
    );
    
    // Check that loading state is shown initially
    expect(screen.getByText(/Loading users/i)).toBeInTheDocument();
    
    // Wait for loading to finish
    await waitFor(() => {
      expect(screen.queryByText(/Loading users/i)).not.toBeInTheDocument();
    }, { timeout: 200 });
  });
  
  test('handles password reset functionality', async () => {
    // Mock window.confirm to return true
    window.confirm.mockReturnValue(true);
    
    // Mock axios.post for password reset
    axios.post.mockResolvedValueOnce({ data: { success: true } });
    
    render(
      <MemoryRouter>
        <UserManagement />
      </MemoryRouter>
    );
    
    // Wait for users to load
    await waitFor(() => {
      expect(screen.queryByText(/Loading users/i)).not.toBeInTheDocument();
    });
    
    // Find and click the reset password button for a user
    const resetButtons = screen.getAllByTitle('Force Password Reset');
    fireEvent.click(resetButtons[0]);
    
    // Verify confirmation was requested
    expect(window.confirm).toHaveBeenCalled();
    
    // Verify axios.post was called with correct parameters
    expect(axios.post).toHaveBeenCalledWith(
      `${API_BASE}/auth/reset-password`,
      { username: 'admin' },
      expect.objectContaining({
        headers: expect.objectContaining({
          'Content-Type': 'application/json'
        })
      })
    );
  });
  
  test('handles user deletion functionality', async () => {
    // Mock window.confirm to return true
    window.confirm.mockReturnValue(true);
    
    // Mock fetch for delete operation
    global.fetch.mockImplementation((url, options) => {
      if (url.includes('/auth_users/1') && options.method === 'DELETE') {
        return Promise.resolve({
          ok: true
        });
      }
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockUsers)
      });
    });
    
    render(
      <MemoryRouter>
        <UserManagement />
      </MemoryRouter>
    );
    
    // Wait for users to load
    await waitFor(() => {
      expect(screen.queryByText(/Loading users/i)).not.toBeInTheDocument();
    });
    
    // Find and click the delete button for a user
    const deleteButtons = screen.getAllByTitle('Delete User');
    fireEvent.click(deleteButtons[0]);
    
    // Verify confirmation was requested
    expect(window.confirm).toHaveBeenCalledWith('Are you sure you want to delete this user?');
    
    // Verify fetch was called with correct method and URL
    expect(global.fetch).toHaveBeenCalledWith(
      `${API_BASE}/auth_users/1`,
      expect.objectContaining({
        method: 'DELETE'
      })
    );
  });
  
  test('handles empty users state', async () => {
    // Mock empty users array
    global.fetch.mockImplementationOnce(() => {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve([])
      });
    });
    
    render(
      <MemoryRouter>
        <UserManagement />
      </MemoryRouter>
    );
    
    // Wait for loading to finish
    await waitFor(() => {
      expect(screen.queryByText(/Loading users/i)).not.toBeInTheDocument();
    });
    
    // Check for empty state message
    expect(screen.getByText('No users found')).toBeInTheDocument();
  });
  
  test('handles cancellation of user deletion', async () => {
    // Mock window.confirm to return false (user cancels deletion)
    window.confirm.mockReturnValue(false);
    
    render(
      <MemoryRouter>
        <UserManagement />
      </MemoryRouter>
    );
    
    // Wait for users to load
    await waitFor(() => {
      expect(screen.queryByText(/Loading users/i)).not.toBeInTheDocument();
    });
    
    // Find and click the delete button for a user
    const deleteButtons = screen.getAllByTitle('Delete User');
    fireEvent.click(deleteButtons[0]);
    
    // Verify confirmation was requested
    expect(window.confirm).toHaveBeenCalled();
    
    // Verify fetch was NOT called with DELETE method
    expect(global.fetch).not.toHaveBeenCalledWith(
      expect.stringContaining('/auth_users/'),
      expect.objectContaining({
        method: 'DELETE'
      })
    );
  });
  
  test('handles cancellation of password reset', async () => {
    // Mock window.confirm to return false (user cancels password reset)
    window.confirm.mockReturnValue(false);
    
    render(
      <MemoryRouter>
        <UserManagement />
      </MemoryRouter>
    );
    
    // Wait for users to load
    await waitFor(() => {
      expect(screen.queryByText(/Loading users/i)).not.toBeInTheDocument();
    });
    
    // Find and click the reset password button for a user
    const resetButtons = screen.getAllByTitle('Force Password Reset');
    fireEvent.click(resetButtons[0]);
    
    // Verify confirmation was requested
    expect(window.confirm).toHaveBeenCalled();
    
    // Verify axios.post was NOT called
    expect(axios.post).not.toHaveBeenCalled();
  });
  
  test('handles failed user deletion', async () => {
    // Mock window.confirm to return true
    window.confirm.mockReturnValue(true);
    
    // Mock fetch for failed delete operation
    global.fetch.mockImplementation((url, options) => {
      if (url.includes('/auth_users/1') && options.method === 'DELETE') {
        return Promise.resolve({
          ok: false,
          status: 403,
          statusText: 'Forbidden'
        });
      }
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockUsers)
      });
    });
    
    render(
      <MemoryRouter>
        <UserManagement />
      </MemoryRouter>
    );
    
    // Wait for users to load
    await waitFor(() => {
      expect(screen.queryByText(/Loading users/i)).not.toBeInTheDocument();
    });
    
    // Find and click the delete button for a user
    const deleteButtons = screen.getAllByTitle('Delete User');
    fireEvent.click(deleteButtons[0]);
    
    // Verify confirmation was requested
    expect(window.confirm).toHaveBeenCalledWith('Are you sure you want to delete this user?');
    
    // Verify fetch was called with correct method and URL
    expect(global.fetch).toHaveBeenCalledWith(
      `${API_BASE}/auth_users/1`,
      expect.objectContaining({
        method: 'DELETE'
      })
    );
  });
  
  test('handles failed password reset', async () => {
    // Mock window.confirm to return true
    window.confirm.mockReturnValue(true);
    
    // Mock axios.post to reject with an error
    axios.post.mockRejectedValueOnce({
      response: {
        data: {
          detail: 'User not found'
        }
      }
    });
    
    render(
      <MemoryRouter>
        <UserManagement />
      </MemoryRouter>
    );
    
    // Wait for users to load
    await waitFor(() => {
      expect(screen.queryByText(/Loading users/i)).not.toBeInTheDocument();
    });
    
    // Find and click the reset password button for a user
    const resetButtons = screen.getAllByTitle('Force Password Reset');
    fireEvent.click(resetButtons[0]);
    
    // Verify confirmation was requested
    expect(window.confirm).toHaveBeenCalled();
    
    // Verify axios.post was called with correct parameters
    expect(axios.post).toHaveBeenCalledWith(
      `${API_BASE}/auth/reset-password`,
      { username: 'admin' },
      expect.any(Object)
    );
  });
});
