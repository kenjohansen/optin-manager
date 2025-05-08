/**
 * ForgotPassword.test.jsx
 * 
 * Tests for the ForgotPassword component.
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import ForgotPassword from './ForgotPassword';
import axios from 'axios';
import { API_BASE } from '../api';

// Mock axios
jest.mock('axios');

// Mock react-router-dom
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn()
}));

describe('ForgotPassword Component', () => {
  beforeEach(() => {
    // Reset all mocks
    jest.clearAllMocks();
    
    // Default mock implementation
    axios.post.mockResolvedValue({ data: { success: true } });
  });

  test('renders the forgot password form', () => {
    render(
      <MemoryRouter>
        <ForgotPassword />
      </MemoryRouter>
    );
    
    // Check for the main heading
    expect(screen.getByText('Forgot Password')).toBeInTheDocument();
    
    // Check for buttons
    expect(screen.getByRole('button', { name: /Reset Password/i })).toBeInTheDocument();
    expect(screen.getByText('Back to Login')).toBeInTheDocument();
  });

  test('submits the form with username', async () => {
    render(
      <MemoryRouter>
        <ForgotPassword />
      </MemoryRouter>
    );
    
    // Fill in the username field - using a more reliable selector
    const usernameInput = screen.getByRole('textbox');
    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    
    // Submit the form
    const submitButton = screen.getByRole('button', { name: /Reset Password/i });
    fireEvent.click(submitButton);
    
    // Check that axios.post was called with the correct arguments
    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledWith(
        `${API_BASE}/auth/reset-password`,
        { username: 'testuser' }
      );
    });
    
    // Check for success message
    await waitFor(() => {
      expect(screen.getByText(/password reset email has been sent/i)).toBeInTheDocument();
      expect(screen.getByText(/Return to Login/i)).toBeInTheDocument();
    });
  });

  test('displays error message on API failure', async () => {
    // Mock API error
    const errorMessage = 'User not found';
    axios.post.mockRejectedValueOnce({ 
      response: { 
        data: { 
          detail: errorMessage 
        } 
      } 
    });
    
    render(
      <MemoryRouter>
        <ForgotPassword />
      </MemoryRouter>
    );
    
    // Fill in the username field
    const usernameInput = screen.getByRole('textbox');
    fireEvent.change(usernameInput, { target: { value: 'nonexistentuser' } });
    
    // Submit the form
    const submitButton = screen.getByRole('button', { name: /Reset Password/i });
    fireEvent.click(submitButton);
    
    // Check for error message
    await waitFor(() => {
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });
    
    // Verify form is still visible (not showing success state)
    expect(screen.getByRole('textbox')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Reset Password/i })).toBeInTheDocument();
  });

  test('handles network error gracefully', async () => {
    // Mock network error with no response object
    axios.post.mockRejectedValueOnce(new Error('Network Error'));
    
    render(
      <MemoryRouter>
        <ForgotPassword />
      </MemoryRouter>
    );
    
    // Fill in the username field
    const usernameInput = screen.getByRole('textbox');
    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    
    // Submit the form
    const submitButton = screen.getByRole('button', { name: /Reset Password/i });
    fireEvent.click(submitButton);
    
    // Check for generic error message
    await waitFor(() => {
      expect(screen.getByText('An error occurred. Please try again.')).toBeInTheDocument();
    });
  });

  test('shows loading state while submitting', async () => {
    // Use a promise that won't resolve immediately to test loading state
    let resolvePromise;
    const promise = new Promise(resolve => {
      resolvePromise = resolve;
    });
    
    axios.post.mockImplementationOnce(() => promise);
    
    render(
      <MemoryRouter>
        <ForgotPassword />
      </MemoryRouter>
    );
    
    // Fill in the username field
    const usernameInput = screen.getByRole('textbox');
    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    
    // Submit the form
    const submitButton = screen.getByRole('button', { name: /Reset Password/i });
    fireEvent.click(submitButton);
    
    // Check for loading indicator
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
    
    // Resolve the promise to complete the test
    resolvePromise({ data: { success: true } });
    
    // Wait for success state
    await waitFor(() => {
      expect(screen.getByText(/password reset email has been sent/i)).toBeInTheDocument();
    });
  });
});
