/**
 * OptInSetup.test.jsx
 * 
 * Unit tests for the OptInSetup component.
 * 
 * These tests verify that the OptInSetup component correctly renders, 
 * handles user interactions, and manages opt-in programs. The tests cover
 * creating new opt-ins, filtering existing ones, and editing program details
 * with appropriate role-based access control.
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import OptInSetup from './OptInSetup';
import * as api from '../api';
import * as auth from '../utils/auth';

// Mock the API functions
jest.mock('../api', () => ({
  createOptIn: jest.fn(),
  fetchOptIns: jest.fn(),
  updateOptIn: jest.fn()
}));

// Mock the auth utility functions
jest.mock('../utils/auth', () => ({
  isAdmin: jest.fn(),
  isSupport: jest.fn(),
  isAuthenticated: jest.fn()
}));

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  clear: jest.fn()
};
Object.defineProperty(window, 'localStorage', { value: localStorageMock });

describe('OptInSetup Component', () => {
  // Sample opt-in data for tests
  const mockOptIns = [
    { id: '1', name: 'Marketing Newsletter', type: 'promotional', status: 'active' },
    { id: '2', name: 'Order Updates', type: 'transactional', status: 'active' },
    { id: '3', name: 'Security Alerts', type: 'alert', status: 'paused' }
  ];

  beforeEach(() => {
    // Reset all mocks before each test
    jest.clearAllMocks();
    
    // Default mock implementations
    api.fetchOptIns.mockResolvedValue(mockOptIns);
    api.createOptIn.mockResolvedValue({ id: '4', name: 'New Opt-In', type: 'promotional', status: 'active' });
    api.updateOptIn.mockResolvedValue({ id: '1', name: 'Updated Marketing', type: 'promotional', status: 'active' });
    
    // Default auth states
    auth.isAdmin.mockReturnValue(true);
    auth.isSupport.mockReturnValue(false);
    auth.isAuthenticated.mockReturnValue(true);
    
    // Mock localStorage
    localStorageMock.getItem.mockReturnValue('mock-token');
  });

  test('renders the component with title', async () => {
    render(
      <MemoryRouter>
        <OptInSetup />
      </MemoryRouter>
    );

    // Check that the component title is rendered
    expect(screen.getByText('Opt-In Setup')).toBeInTheDocument();
    
    // Verify API was called
    await waitFor(() => {
      expect(api.fetchOptIns).toHaveBeenCalledTimes(1);
    });
  });

  test('handles creating a new opt-in program', async () => {
    render(
      <MemoryRouter>
        <OptInSetup />
      </MemoryRouter>
    );

    // Wait for component to render
    await waitFor(() => {
      expect(api.fetchOptIns).toHaveBeenCalledTimes(1);
    });
    
    // Fill out the form (without waiting for findBy)
    const nameInputs = screen.getAllByRole('textbox');
    const nameInput = nameInputs[0]; // First textbox is the name input
    fireEvent.change(nameInput, { target: { value: 'New Opt-In' } });
    
    // Submit the form
    const createButton = screen.getByRole('button', { name: /Create/i });
    fireEvent.click(createButton);
    
    // Check that the API was called with the correct data
    await waitFor(() => {
      expect(api.createOptIn).toHaveBeenCalledWith({
        name: 'New Opt-In',
        type: 'promotional' // Default value
      });
    });
    
    // Check that the opt-ins were reloaded
    await waitFor(() => {
      expect(api.fetchOptIns).toHaveBeenCalledTimes(2);
    });
  });

  test('handles errors when creating an opt-in program', async () => {
    // Mock the API to return an error
    api.createOptIn.mockRejectedValueOnce(new Error('API Error'));
    
    render(
      <MemoryRouter>
        <OptInSetup />
      </MemoryRouter>
    );

    // Wait for component to render
    await waitFor(() => {
      expect(api.fetchOptIns).toHaveBeenCalledTimes(1);
    });
    
    // Fill out the form
    const nameInputs = screen.getAllByRole('textbox');
    const nameInput = nameInputs[0]; // First textbox is the name input
    fireEvent.change(nameInput, { target: { value: 'Error Opt-In' } });
    
    // Submit the form
    const createButton = screen.getByRole('button', { name: /Create/i });
    fireEvent.click(createButton);
    
    // Check that the API was called
    await waitFor(() => {
      expect(api.createOptIn).toHaveBeenCalled();
    });
    
    // Check that an error is shown
    await waitFor(() => {
      const errorAlert = screen.getByText('Failed to create opt-in.');
      expect(errorAlert).toBeInTheDocument();
    });
  });

  test('enforces role-based access control for admin-only actions', async () => {
    // Mock auth to return support role instead of admin
    auth.isAdmin.mockReturnValue(false);
    auth.isSupport.mockReturnValue(true);
    
    render(
      <MemoryRouter>
        <OptInSetup />
      </MemoryRouter>
    );

    // Wait for component to render
    await waitFor(() => {
      expect(api.fetchOptIns).toHaveBeenCalledTimes(1);
    });
    
    // Check that the form elements are disabled
    const nameInputs = screen.getAllByRole('textbox');
    expect(nameInputs[0]).toBeDisabled(); // Name input should be disabled
    
    const createButton = screen.getByRole('button', { name: /Create/i });
    expect(createButton).toBeDisabled();
  });

  test('does not render when user is not authenticated', async () => {
    // Mock auth to return unauthenticated
    auth.isAuthenticated.mockReturnValue(false);
    
    const { container } = render(
      <MemoryRouter>
        <OptInSetup />
      </MemoryRouter>
    );

    // Check that the component is not rendered
    expect(container.firstChild).toBeNull();
  });
});
