/**
 * PreferencesDashboard.test.jsx
 * 
 * Comprehensive test suite for the PreferencesDashboard component.
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import PreferencesDashboard from './PreferencesDashboard';
import * as api from '../api';

// Mock the API functions
jest.mock('../api', () => ({
  updateContactPreferences: jest.fn()
}));

// Mock console methods to prevent test output noise
const originalConsoleLog = console.log;
const originalConsoleError = console.error;

beforeAll(() => {
  console.log = jest.fn();
  console.error = jest.fn();
});

afterAll(() => {
  console.log = originalConsoleLog;
  console.error = originalConsoleError;
});

describe('PreferencesDashboard Component', () => {
  // Mock props
  const mockProps = {
    masked: 't***@example.com',
    token: 'mock-token',
    preferences: {
      contact: {
        value: 'test@example.com',
        type: 'email'
      },
      programs: [
        { id: 1, name: 'Marketing', type: 'email', opted_in: true, last_updated: '2025-01-01T00:00:00Z' },
        { id: 2, name: 'Promotions', type: 'sms', opted_in: false, last_updated: '2025-01-02T00:00:00Z' }
      ],
      last_comment: 'Previous update reason'
    },
    setPreferences: jest.fn()
  };

  beforeEach(() => {
    // Reset all mocks
    jest.clearAllMocks();
    
    // Default mock implementations
    api.updateContactPreferences.mockResolvedValue({ success: true });
  });

  test('renders the preferences dashboard with programs', () => {
    render(<PreferencesDashboard {...mockProps} />);
    
    // Check for the main heading
    expect(screen.getByText(/Manage Your Preferences/i)).toBeInTheDocument();
    
    // Check for the masked contact info
    expect(screen.getByText(/Contact:/i)).toBeInTheDocument();
    expect(screen.getByText(/t\*\*\*@example\.com/i)).toBeInTheDocument();
    
    // Check for program names
    expect(screen.getByText(/Marketing/i)).toBeInTheDocument();
    expect(screen.getByText(/Promotions/i)).toBeInTheDocument();
    
    // Check for the save button
    expect(screen.getByRole('button', { name: /Save Preferences/i })).toBeInTheDocument();
    
    // Check for the global opt-out section
    expect(screen.getByText(/Global Opt-Out/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Opt Out of Everything/i })).toBeInTheDocument();
  });

  test('renders info alert when no programs are available', () => {
    const propsWithNoPrograms = {
      ...mockProps,
      preferences: {
        ...mockProps.preferences,
        programs: []
      }
    };
    
    render(<PreferencesDashboard {...propsWithNoPrograms} />);
    
    // Check for the info alert
    expect(screen.getByText(/You don't have any preferences set up yet/i)).toBeInTheDocument();
  });
  
  test('renders info alert when preferences is null', () => {
    const propsWithNullPreferences = {
      ...mockProps,
      preferences: null
    };
    
    render(<PreferencesDashboard {...propsWithNullPreferences} />);
    
    // Check for the info alert about no opt-in programs
    expect(screen.getByText(/No opt-in programs are currently available/i)).toBeInTheDocument();
  });
  
  test('renders info alert when programs is null', () => {
    const propsWithNullPrograms = {
      ...mockProps,
      preferences: {
        ...mockProps.preferences,
        programs: null
      }
    };
    
    render(<PreferencesDashboard {...propsWithNullPrograms} />);
    
    // Check for the info alert about no opt-in programs
    expect(screen.getByText(/No opt-in programs are currently available/i)).toBeInTheDocument();
  });
  
  test('toggles a program preference when switch is clicked', () => {
    render(<PreferencesDashboard {...mockProps} />);
    
    // Find all switches (should be 2 for our mock data)
    const switches = screen.getAllByRole('checkbox');
    expect(switches).toHaveLength(2);
    
    // First switch should be checked (Marketing is opted_in: true)
    expect(switches[0]).toBeChecked();
    
    // Second switch should not be checked (Promotions is opted_in: false)
    expect(switches[1]).not.toBeChecked();
    
    // Click the first switch to toggle it off
    fireEvent.click(switches[0]);
    
    // Now it should be unchecked
    expect(switches[0]).not.toBeChecked();
    
    // Click the second switch to toggle it on
    fireEvent.click(switches[1]);
    
    // Now it should be checked
    expect(switches[1]).toBeChecked();
  });
  
  test('saves preferences when Save button is clicked', async () => {
    render(<PreferencesDashboard {...mockProps} />);
    
    // Find and click the Save button
    const saveButton = screen.getByRole('button', { name: /Save Preferences/i });
    fireEvent.click(saveButton);
    
    // Check that the API was called with the right parameters
    expect(api.updateContactPreferences).toHaveBeenCalled();
    expect(api.updateContactPreferences.mock.calls[0][0]).toMatchObject({
      programs: expect.any(Array),
      comment: 'Previous update reason'
    });
    
    // Wait for success message
    await waitFor(() => {
      expect(screen.getByText(/Preferences updated!/i)).toBeInTheDocument();
    });
    
    // Check that setPreferences was called
    expect(mockProps.setPreferences).toHaveBeenCalled();
  });
  
  test('handles error when saving preferences fails', async () => {
    // Mock API to reject
    api.updateContactPreferences.mockRejectedValueOnce(new Error('API error'));
    
    render(<PreferencesDashboard {...mockProps} />);
    
    // Find and click the Save button
    const saveButton = screen.getByRole('button', { name: /Save Preferences/i });
    fireEvent.click(saveButton);
    
    // Wait for error message
    await waitFor(() => {
      expect(screen.getByText(/Failed to update preferences/i)).toBeInTheDocument();
    });
    
    // Check that console.error was called
    expect(console.error).toHaveBeenCalled();
  });
  
  test('updates comment when text field changes', () => {
    render(<PreferencesDashboard {...mockProps} />);
    
    // Find the comment text field
    const commentField = screen.getByLabelText(/Reason for changes/i);
    
    // Check initial value is the last comment
    expect(commentField.value).toBe('Previous update reason');
    
    // Change the comment
    fireEvent.change(commentField, { target: { value: 'New comment' } });
    
    // Check the new value
    expect(commentField.value).toBe('New comment');
  });
  
  test('performs global opt-out when button is clicked', async () => {
    render(<PreferencesDashboard {...mockProps} />);
    
    // Find and click the global opt-out button
    const optOutButton = screen.getByRole('button', { name: /Opt Out of Everything/i });
    fireEvent.click(optOutButton);
    
    // Check that the API was called with the right parameters
    expect(api.updateContactPreferences).toHaveBeenCalled();
    expect(api.updateContactPreferences.mock.calls[0][0]).toMatchObject({
      programs: [],
      comment: 'Previous update reason',
      global_opt_out: true
    });
    
    // Wait for success message
    await waitFor(() => {
      expect(screen.getByText(/You have been opted out of all opt-ins/i)).toBeInTheDocument();
    });
    
    // Check that setPreferences was called
    expect(mockProps.setPreferences).toHaveBeenCalled();
  });
  
  test('handles error when global opt-out fails', async () => {
    // Mock API to reject
    api.updateContactPreferences.mockRejectedValueOnce(new Error('API error'));
    
    render(<PreferencesDashboard {...mockProps} />);
    
    // Find and click the global opt-out button
    const optOutButton = screen.getByRole('button', { name: /Opt Out of Everything/i });
    fireEvent.click(optOutButton);
    
    // Wait for error message
    await waitFor(() => {
      expect(screen.getByText(/Failed to opt out of everything/i)).toBeInTheDocument();
    });
    
    // Check that console.error was called
    expect(console.error).toHaveBeenCalled();
  });
  
  test('uses contact value instead of token when token is not provided', async () => {
    const propsWithoutToken = {
      ...mockProps,
      token: null
    };
    
    render(<PreferencesDashboard {...propsWithoutToken} />);
    
    // Find and click the Save button
    const saveButton = screen.getByRole('button', { name: /Save Preferences/i });
    fireEvent.click(saveButton);
    
    // Check that the API was called with contact value instead of token
    expect(api.updateContactPreferences).toHaveBeenCalled();
    expect(api.updateContactPreferences.mock.calls[0][0]).toMatchObject({
      programs: expect.any(Array),
      comment: 'Previous update reason'
    });
  });
});
