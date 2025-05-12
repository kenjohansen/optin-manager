/**
 * VerbalOptIn.test.jsx
 * 
 * Comprehensive tests for the VerbalOptIn component.
 */

import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import VerbalOptIn from './VerbalOptIn';
import * as api from '../api';
import * as phoneUtils from '../utils/phoneUtils';

// Mock the API functions
jest.mock('../api', () => ({
  fetchOptIns: jest.fn(),
  updateContactPreferences: jest.fn(),
  sendVerificationCode: jest.fn(),
  fetchContactPreferences: jest.fn()
}));

// Mock the phone utils
jest.mock('../utils/phoneUtils', () => ({
  formatPhoneToE164: jest.fn(phone => `+1${phone.replace(/\D/g, '')}`),
  isValidPhoneNumber: jest.fn(phone => /^\+?[1-9]\d{9,14}$/.test(phone.replace(/\D/g, '')))
}));

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn()
};
Object.defineProperty(window, 'localStorage', { value: localStorageMock });

// Mock console methods to reduce test noise
const originalConsoleLog = console.log;
const originalConsoleError = console.error;

describe('VerbalOptIn Component', () => {
  const mockOptIns = [
    { id: 'opt1', name: 'Marketing Emails', type: 'email', status: 'active' },
    { id: 'opt2', name: 'SMS Promotions', type: 'sms', status: 'active' },
    { id: 'opt3', name: 'Newsletter', type: 'email', status: 'active' }
  ];

  beforeEach(() => {
    // Silence console during tests
    console.log = jest.fn();
    console.error = jest.fn();
    
    // Reset all mocks
    jest.clearAllMocks();
    
    // Default mock implementations
    api.fetchOptIns.mockResolvedValue(mockOptIns);
    
    api.fetchContactPreferences.mockResolvedValue({
      programs: []
    });
    
    api.updateContactPreferences.mockResolvedValue({ success: true });
    api.sendVerificationCode.mockResolvedValue({ success: true });
    
    // Mock localStorage
    localStorageMock.getItem.mockImplementation((key) => {
      if (key === 'username') return 'Test User';
      if (key === 'email') return 'test@example.com';
      return null;
    });
    
    // Mock phone validation
    phoneUtils.isValidPhoneNumber.mockImplementation(phone => 
      /^\+?[1-9]\d{9,14}$/.test(phone.replace(/\D/g, ''))
    );
  });

  afterEach(() => {
    // Restore console methods
    console.log = originalConsoleLog;
    console.error = originalConsoleError;
  });

  test('renders the verbal opt-in form', async () => {
    render(<VerbalOptIn />);
    
    // Check for the main heading
    expect(screen.getByText(/Verbal Opt-In Management/i)).toBeInTheDocument();
    
    // Check for the contact input field
    expect(screen.getByLabelText(/Customer Email or Phone/i)).toBeInTheDocument();
    
    // Check for the form description
    expect(screen.getByText(/Use this form to record verbal opt-ins/i)).toBeInTheDocument();
    
    // Initially, the button might be in loading state with a CircularProgress
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
    
    // Verify API was called to fetch opt-ins
    await waitFor(() => {
      expect(api.fetchOptIns).toHaveBeenCalledTimes(1);
    });
    
    // After loading completes, the Continue button should be visible
    await waitFor(() => {
      const continueButton = screen.getByRole('button', { name: /Continue/i });
      expect(continueButton).toBeInTheDocument();
    });
  });
  
  test('validates email input correctly', async () => {
    render(<VerbalOptIn />);
    
    // Wait for loading to complete
    await waitFor(() => {
      expect(api.fetchOptIns).toHaveBeenCalledTimes(1);
    });
    
    const emailInput = screen.getByLabelText(/Customer Email or Phone/i);
    
    // Wait for the continue button to be enabled
    let continueButton;
    await waitFor(() => {
      continueButton = screen.getByRole('button', { name: /Continue/i });
      expect(continueButton).not.toBeDisabled();
    });
    
    // Get the form element
    const form = screen.getByRole('button', { name: /Continue/i }).closest('form');
    
    // Test with empty input
    fireEvent.change(emailInput, { target: { value: '' } });
    fireEvent.submit(form);
    
    // Mock the handleContactSubmit function's error setting
    await act(async () => {
      // The component will set an error for empty contact
      expect(api.fetchContactPreferences).not.toHaveBeenCalled();
    });
    
    // Test with invalid input
    fireEvent.change(emailInput, { target: { value: 'not-an-email' } });
    fireEvent.submit(form);
    
    // Mock the handleContactSubmit function's error handling
    await act(async () => {
      // The component will set an error for invalid contact
      expect(api.fetchContactPreferences).not.toHaveBeenCalled();
    });
    
    // Test with valid email
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.submit(form);
    
    await waitFor(() => {
      // Should move to step 1 (preferences selection)
      expect(api.fetchContactPreferences).toHaveBeenCalledWith({ contact: 'test@example.com' });
    });
  });
  
  test('validates phone input correctly', async () => {
    render(<VerbalOptIn />);
    
    // Wait for loading to complete
    await waitFor(() => {
      expect(api.fetchOptIns).toHaveBeenCalledTimes(1);
    });
    
    const phoneInput = screen.getByLabelText(/Customer Email or Phone/i);
    
    // Wait for the continue button to be enabled
    let continueButton;
    await waitFor(() => {
      continueButton = screen.getByRole('button', { name: /Continue/i });
      expect(continueButton).not.toBeDisabled();
    });
    
    // Get the form element
    const form = screen.getByRole('button', { name: /Continue/i }).closest('form');
    
    // Test with valid phone
    fireEvent.change(phoneInput, { target: { value: '1234567890' } });
    fireEvent.submit(form);
    
    await waitFor(() => {
      // Should move to step 1 (preferences selection)
      expect(api.fetchContactPreferences).toHaveBeenCalled();
      expect(phoneUtils.formatPhoneToE164).toHaveBeenCalledWith('1234567890');
    });
  });
  
  test('loads existing preferences for a contact', async () => {
    // Mock existing preferences
    api.fetchContactPreferences.mockResolvedValue({
      programs: [
        { name: 'Marketing Emails', opted_in: true },
        { name: 'SMS Promotions', opted_in: false },
        { name: 'Newsletter', opted_in: true }
      ]
    });
    
    render(<VerbalOptIn />);
    
    // Wait for loading to complete
    await waitFor(() => {
      expect(api.fetchOptIns).toHaveBeenCalledTimes(1);
    });
    
    const emailInput = screen.getByLabelText(/Customer Email or Phone/i);
    
    // Wait for the continue button to be enabled
    let continueButton;
    await waitFor(() => {
      continueButton = screen.getByRole('button', { name: /Continue/i });
      expect(continueButton).not.toBeDisabled();
    });
    
    // Get the form element
    const form = screen.getByRole('button', { name: /Continue/i }).closest('form');
    
    // Enter valid email and continue
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.submit(form);
    
    // Wait for the preferences to load
    await waitFor(() => {
      expect(api.fetchContactPreferences).toHaveBeenCalledWith({ contact: 'test@example.com' });
    });
  });
  
  test('handles API errors when fetching opt-ins', async () => {
    // Mock API error
    api.fetchOptIns.mockRejectedValue(new Error('Network error'));
    
    render(<VerbalOptIn />);
    
    // Wait for error message
    await waitFor(() => {
      expect(screen.getByText(/Failed to load opt-in programs/i)).toBeInTheDocument();
    });
  });
  
  test('toggles preferences and saves them', async () => {
    render(<VerbalOptIn />);
    
    // Wait for loading to complete
    await waitFor(() => {
      expect(api.fetchOptIns).toHaveBeenCalledTimes(1);
    });
    
    const emailInput = screen.getByLabelText(/Customer Email or Phone/i);
    
    // Wait for the continue button to be enabled
    let continueButton;
    await waitFor(() => {
      continueButton = screen.getByRole('button', { name: /Continue/i });
      expect(continueButton).not.toBeDisabled();
    });
    
    // Get the form element
    const form = screen.getByRole('button', { name: /Continue/i }).closest('form');
    
    // Enter valid email and continue
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.submit(form);
    
    // Wait for step 1 to load
    await waitFor(() => {
      expect(screen.getByText(/Select Opt-Ins the Customer Verbally Agreed To/i)).toBeInTheDocument();
    });
    
    // Find switches and toggle them
    const switches = await screen.findAllByRole('checkbox');
    expect(switches.length).toBeGreaterThan(0);
    
    // Toggle the first switch
    fireEvent.click(switches[0]);
    
    // Add a comment
    const commentField = screen.getByLabelText(/Notes about this verbal opt-in/i);
    fireEvent.change(commentField, { target: { value: 'Customer called and requested to receive promotional messages' } });
    
    // Click save button
    const saveButton = screen.getByRole('button', { name: /Save Preferences & Notify Customer/i });
    fireEvent.click(saveButton);
    
    // Verify API calls
    await waitFor(() => {
      expect(api.updateContactPreferences).toHaveBeenCalled();
      expect(api.sendVerificationCode).toHaveBeenCalled();
      expect(screen.getByText(/Preferences updated for/i)).toBeInTheDocument();
    });
  });
  
  test('handles back button to return to contact entry', async () => {
    render(<VerbalOptIn />);
    
    // Wait for loading to complete
    await waitFor(() => {
      expect(api.fetchOptIns).toHaveBeenCalledTimes(1);
    });
    
    const emailInput = screen.getByLabelText(/Customer Email or Phone/i);
    
    // Wait for the continue button to be enabled
    let continueButton;
    await waitFor(() => {
      continueButton = screen.getByRole('button', { name: /Continue/i });
      expect(continueButton).not.toBeDisabled();
    });
    
    // Get the form element
    const form = screen.getByRole('button', { name: /Continue/i }).closest('form');
    
    // Enter valid email and continue
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.submit(form);
    
    // Wait for step 1 to load
    await waitFor(() => {
      expect(screen.getByText(/Select Opt-Ins the Customer Verbally Agreed To/i)).toBeInTheDocument();
    });
    
    // Click back button
    const backButton = screen.getByRole('button', { name: /Back/i });
    fireEvent.click(backButton);
    
    // Verify we're back at step 0
    await waitFor(() => {
      expect(screen.getByLabelText(/Customer Email or Phone/i)).toBeInTheDocument();
    });
  });
  
  test('handles API errors when saving preferences', async () => {
    // Mock API error
    api.updateContactPreferences.mockRejectedValue(new Error('Network error'));
    
    render(<VerbalOptIn />);
    
    // Wait for loading to complete
    await waitFor(() => {
      expect(api.fetchOptIns).toHaveBeenCalledTimes(1);
    });
    
    const emailInput = screen.getByLabelText(/Customer Email or Phone/i);
    
    // Wait for the continue button to be enabled
    let continueButton;
    await waitFor(() => {
      continueButton = screen.getByRole('button', { name: /Continue/i });
      expect(continueButton).not.toBeDisabled();
    });
    
    // Get the form element
    const form = screen.getByRole('button', { name: /Continue/i }).closest('form');
    
    // Enter valid email and continue
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.submit(form);
    
    // Wait for step 1 to load
    await waitFor(() => {
      expect(screen.getByText(/Select Opt-Ins the Customer Verbally Agreed To/i)).toBeInTheDocument();
    });
    
    // Click save button
    const saveButton = screen.getByRole('button', { name: /Save Preferences & Notify Customer/i });
    fireEvent.click(saveButton);
    
    // Verify error message
    await waitFor(() => {
      expect(screen.getByText(/Failed to update preferences/i)).toBeInTheDocument();
    });
  });

  test('handles search params fallback for testing', () => {
    // This is a simple test to verify the fallback mechanism works
    // when the component is rendered outside a Router context
    render(<VerbalOptIn />);
    
    // If the fallback is working, the component should render without errors
    // Look for a label which includes the text but might have additional elements
    const labels = screen.getAllByText((content, element) => {
      return element.tagName.toLowerCase() === 'label' && 
             content.includes('Customer Email or Phone');
    });
    expect(labels.length).toBeGreaterThan(0);
    
    // Our implementation should log a message about using fallback
    expect(console.log).toHaveBeenCalledWith(
      expect.stringContaining('fallback search params')
    );
  });
});
