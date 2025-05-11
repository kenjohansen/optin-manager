/**
 * EmailProviderConfig.test.jsx
 *
 * Tests for the EmailProviderConfig component
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import userEvent from '@testing-library/user-event';
import EmailProviderConfig from './EmailProviderConfig';
import { testProviderConnection, setProviderSecret, deleteProviderSecret, getSecretsStatus } from '../api/providerSecrets';

// Mock the API functions
jest.mock('../api/providerSecrets', () => ({
  testProviderConnection: jest.fn(),
  setProviderSecret: jest.fn(),
  deleteProviderSecret: jest.fn(),
  getSecretsStatus: jest.fn()
}));

describe('EmailProviderConfig Component', () => {
  beforeEach(() => {
    // Clear mocks between tests
    jest.clearAllMocks();
    // Setup localStorage mock
    Object.defineProperty(window, 'localStorage', {
      value: {
        getItem: jest.fn(),
        setItem: jest.fn(),
        removeItem: jest.fn()
      },
      writable: true
    });
  });

  // Test initial render with no configuration
  test('renders unconfigured state correctly', async () => {
    // Mock API to return unconfigured state
    getSecretsStatus.mockResolvedValue({
      email_configured: false,
      email_status: 'untested'
    });

    await act(async () => {
      render(<EmailProviderConfig />);
    });

    // Check if component renders in unconfigured state
    expect(screen.getByText('Email Provider Configuration')).toBeInTheDocument();
    expect(screen.getByText('Not Configured')).toBeInTheDocument();
    
    // Check if buttons are rendered correctly
    expect(screen.getByText('Save')).toBeEnabled();
    expect(screen.getByText('Test')).toBeDisabled(); // Test should be disabled when not configured
    expect(screen.getByText('Delete')).toBeDisabled(); // Delete should be disabled when not configured
  });

  // Test initial render with existing configuration
  test('renders configured state correctly', async () => {
    // Mock API to return configured state
    getSecretsStatus.mockResolvedValue({
      email_configured: true,
      email_status: 'untested'
    });

    await act(async () => {
      render(<EmailProviderConfig />);
    });

    // Check if component renders in configured state
    expect(screen.getByText('Email Provider Configuration')).toBeInTheDocument();
    expect(screen.getByText('Configured')).toBeInTheDocument();
    expect(screen.getByText('Not Tested')).toBeInTheDocument();
    
    // Check if buttons are enabled/disabled correctly
    expect(screen.getByText('Save')).toBeEnabled();
    expect(screen.getByText('Test')).toBeEnabled(); // Test should be enabled when configured
    expect(screen.getByText('Delete')).toBeEnabled(); // Delete should be enabled when configured
  });

  // Test save button is enabled even when fields are empty
  test('save button is enabled even when fields are empty', async () => {
    // Mock API to return unconfigured state
    getSecretsStatus.mockResolvedValue({
      email_configured: false,
      email_status: 'untested'
    });

    await act(async () => {
      render(<EmailProviderConfig />);
    });

    // Save button should be enabled even with empty fields
    expect(screen.getByText('Save')).toBeEnabled();
  });
  
  // Test button interactions
  test('buttons are clickable', async () => {
    // Mock API responses
    getSecretsStatus.mockResolvedValue({
      email_configured: false,
      email_status: 'untested'
    });

    await act(async () => {
      render(<EmailProviderConfig />);
    });

    // Buttons should be present
    const saveButton = screen.getByText('Save');
    expect(saveButton).toBeInTheDocument();
    
    // Should be able to click buttons without errors
    await act(async () => {
      await userEvent.click(saveButton);
    });
  });

  // Test testing connection
  test('handles testing connection correctly', async () => {
    // Mock API responses
    getSecretsStatus.mockResolvedValue({
      email_configured: true,
      email_status: 'untested'
    });
    testProviderConnection.mockResolvedValue({ 
      success: true,
      message: 'Connection successful'
    });

    await act(async () => {
      render(<EmailProviderConfig />);
    });

    // Click test button
    await act(async () => {
      await userEvent.click(screen.getByText('Test'));
    });

    // Wait for test to complete
    await waitFor(() => {
      expect(testProviderConnection).toHaveBeenCalledWith({ providerType: 'email' });
      expect(screen.getByText('Connection successful')).toBeInTheDocument();
    });

    // Check that status was updated
    expect(window.localStorage.setItem).toHaveBeenCalledWith('email_tested', 'true');
  });

  // Test deleting credentials
  test('handles deleting credentials correctly', async () => {
    // Mock API responses
    getSecretsStatus.mockResolvedValue({
      email_configured: true,
      email_status: 'tested'
    });
    deleteProviderSecret.mockResolvedValue({ success: true });

    await act(async () => {
      render(<EmailProviderConfig />);
    });

    // Click delete button
    await act(async () => {
      await userEvent.click(screen.getByText('Delete'));
    });

    // Wait for delete to complete
    await waitFor(() => {
      expect(deleteProviderSecret).toHaveBeenCalledWith({ providerType: 'email' });
    });

    // Check localStorage values were cleared
    expect(window.localStorage.removeItem).toHaveBeenCalledWith('email_configured');
    expect(window.localStorage.removeItem).toHaveBeenCalledWith('email_tested');
  });

  // Test that component can be rendered without errors
  test('renders without crashing', async () => {
    // Mock API responses
    getSecretsStatus.mockResolvedValue({
      email_configured: false,
      email_status: 'untested'
    });

    await act(async () => {
      render(<EmailProviderConfig />);
    });

    // Basic component elements should be present
    expect(screen.getByText('Email Provider Configuration')).toBeInTheDocument();
    expect(screen.getByText('Save')).toBeInTheDocument();
  });

  // Test error handling during test
  test('handles test errors correctly', async () => {
    // Mock API responses
    getSecretsStatus.mockResolvedValue({
      email_configured: true,
      email_status: 'untested'
    });
    const errorMessage = 'Connection test failed';
    testProviderConnection.mockRejectedValue({ 
      response: { data: { detail: errorMessage } }
    });

    await act(async () => {
      render(<EmailProviderConfig />);
    });

    // Click test button
    await act(async () => {
      await userEvent.click(screen.getByText('Test'));
    });

    // Wait for error to be displayed
    await waitFor(() => {
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });

    // Check status was updated
    expect(window.localStorage.setItem).toHaveBeenCalledWith('email_tested', 'false');
  });

  // Test provider selection text content
  test('displays AWS SES as the default provider', async () => {
    // Mock API responses
    getSecretsStatus.mockResolvedValue({
      email_configured: false,
      email_status: 'untested'
    });

    await act(async () => {
      render(<EmailProviderConfig />);
    });

    // Verify that AWS SES is selected by default
    const selectElement = screen.getByTestId('email-provider-select');
    expect(selectElement).toHaveTextContent('AWS SES');
  });
});
