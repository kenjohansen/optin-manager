/**
 * AdminLogin.test.jsx
 *
 * Unit tests for the AdminLogin component.
 *
 * These tests verify that the admin login page renders correctly,
 * handles form submission, validates credentials, and navigates
 * to the dashboard upon successful authentication.
 *
 * Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
 * This file is part of the OptIn Manager project and is licensed under the MIT License.
 * See the root LICENSE file for details.
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import AdminLogin from './AdminLogin';
import * as api from '../api';

// Mock the API module
jest.mock('../api', () => ({
  login: jest.fn(),
}));

// Mock the useNavigate hook
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

// Mock localStorage
const localStorageMock = (() => {
  let store = {};
  return {
    getItem: jest.fn(key => store[key] || null),
    setItem: jest.fn((key, value) => {
      store[key] = value.toString();
    }),
    clear: jest.fn(() => {
      store = {};
    }),
    removeItem: jest.fn(key => {
      delete store[key];
    }),
  };
})();
Object.defineProperty(window, 'localStorage', { value: localStorageMock });

describe('AdminLogin Component', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
    localStorageMock.clear();
  });

  test('renders login form correctly', () => {
    render(
      <MemoryRouter>
        <AdminLogin />
      </MemoryRouter>
    );

    // Check if the form elements are rendered
    expect(screen.getByText('Admin Login')).toBeInTheDocument();
    expect(screen.getByLabelText('Username')).toBeInTheDocument();
    expect(screen.getByLabelText('Password')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Login' })).toBeInTheDocument();
    expect(screen.getByText('Forgot password?')).toBeInTheDocument();
  });

  test('handles form input changes', async () => {
    render(
      <MemoryRouter>
        <AdminLogin />
      </MemoryRouter>
    );

    const usernameInput = screen.getByLabelText('Username');
    const passwordInput = screen.getByLabelText('Password');

    // Simulate user typing
    await userEvent.type(usernameInput, 'admin');
    await userEvent.type(passwordInput, 'password123');

    // Check if the input values are updated
    expect(usernameInput).toHaveValue('admin');
    expect(passwordInput).toHaveValue('password123');
  });

  test('shows loading state during login', async () => {
    // Mock the login function to return a promise that doesn't resolve immediately
    api.login.mockImplementation(() => new Promise(resolve => {
      setTimeout(() => {
        resolve({ access_token: 'test-token' });
      }, 100);
    }));

    render(
      <MemoryRouter>
        <AdminLogin />
      </MemoryRouter>
    );

    // Fill in the form
    await userEvent.type(screen.getByLabelText('Username'), 'admin');
    await userEvent.type(screen.getByLabelText('Password'), 'password123');

    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: 'Login' }));

    // Check if loading indicator is shown
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  test('handles successful login and redirects to dashboard', async () => {
    // Mock successful login response
    api.login.mockResolvedValue({ access_token: 'test-token' });

    // Spy on localStorage.setItem directly
    jest.spyOn(window.localStorage, 'setItem');

    render(
      <MemoryRouter>
        <AdminLogin />
      </MemoryRouter>
    );

    // Fill in the form
    await userEvent.type(screen.getByLabelText('Username'), 'admin');
    await userEvent.type(screen.getByLabelText('Password'), 'password123');

    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: 'Login' }));

    // Wait for the login process to complete with a longer timeout
    await waitFor(() => {
      // Check if login was called with correct credentials
      expect(api.login).toHaveBeenCalledWith({
        username: 'admin',
        password: 'password123'
      });
    }, { timeout: 3000 });
    
    // Check localStorage and navigation in separate assertions
    expect(window.localStorage.setItem).toHaveBeenCalledWith('access_token', 'test-token');
    expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
  });

  test('handles login error and displays error message', async () => {
    // Mock login failure
    api.login.mockRejectedValue(new Error('Invalid credentials'));

    render(
      <MemoryRouter>
        <AdminLogin />
      </MemoryRouter>
    );

    // Fill in the form
    await userEvent.type(screen.getByLabelText('Username'), 'wrong');
    await userEvent.type(screen.getByLabelText('Password'), 'wrong');

    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: 'Login' }));

    // Wait for the error message to appear
    await waitFor(() => {
      expect(screen.getByText('Invalid credentials or server error.')).toBeInTheDocument();
    });

    // Check that localStorage was not updated
    expect(localStorageMock.setItem).not.toHaveBeenCalled();
    // Check that navigation did not occur
    expect(mockNavigate).not.toHaveBeenCalled();
  });

  test('handles missing token in response', async () => {
    // Mock response without access_token
    api.login.mockResolvedValue({ user: 'admin', role: 'admin' });

    render(
      <MemoryRouter>
        <AdminLogin />
      </MemoryRouter>
    );

    // Fill in the form
    await userEvent.type(screen.getByLabelText('Username'), 'admin');
    await userEvent.type(screen.getByLabelText('Password'), 'password123');

    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: 'Login' }));

    // Wait for the error message to appear
    await waitFor(() => {
      expect(screen.getByText('Login succeeded but no access token returned.')).toBeInTheDocument();
    });

    // Check that localStorage was not updated
    expect(localStorageMock.setItem).not.toHaveBeenCalled();
    // Check that navigation did not occur
    expect(mockNavigate).not.toHaveBeenCalled();
  });

  test('navigates to forgot password page when link is clicked', async () => {
    render(
      <MemoryRouter initialEntries={['/login']}>
        <Routes>
          <Route path="/login" element={<AdminLogin />} />
          <Route path="/forgot-password" element={<div>Forgot Password Page</div>} />
        </Routes>
      </MemoryRouter>
    );

    // Click the "Forgot password?" link
    fireEvent.click(screen.getByText('Forgot password?'));

    // Check if navigation to forgot-password page occurred
    await waitFor(() => {
      expect(screen.getByText('Forgot Password Page')).toBeInTheDocument();
    });
  });
});
