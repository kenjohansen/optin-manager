/**
 * Customization.test.jsx
 * 
 * Simplified unit tests for the Customization component.
 * 
 * This test suite verifies the functionality of the Customization component's
 * updated architecture, where each section (Branding, EmailProvider, SmsProvider)
 * handles its own state and API calls independently.
 * 
 * The tests focus on:
 * - Proper rendering of all component sections
 * - Data fetching and state management
 * - Branding section functionality
 * - Notification handling
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import Customization from './Customization';
import * as api from '../api';

// Mock the API functions
jest.mock('../api', () => ({
  fetchCustomization: jest.fn(),
  saveCustomization: jest.fn()
}));

// Mock the child components
jest.mock('../components/BrandingSection', () => {
  return function MockBrandingSection(props) {
    return (
      <div data-testid="branding-section">
        <span>Company: {props.companyName}</span>
        <span>Privacy: {props.privacyPolicy}</span>
        <span>Primary: {props.primary}</span>
        <span>Secondary: {props.secondary}</span>
        <button 
          data-testid="save-branding-button"
          onClick={props.handleSave}
          disabled={props.saving}
        >
          {props.saving ? 'Saving...' : 'Save'}
        </button>
        {props.logoPreview && <img src={props.logoPreview} alt="Logo Preview" data-testid="logo-preview" />}
      </div>
    );
  };
});

jest.mock('../components/EmailProviderConfig', () => {
  return function MockEmailProviderConfig() {
    return <div data-testid="email-provider-section">Email Provider Config</div>;
  };
});

jest.mock('../components/SmsProviderConfig', () => {
  return function MockSmsProviderConfig() {
    return <div data-testid="sms-provider-section">SMS Provider Config</div>;
  };
});

// Mock URL.createObjectURL
URL.createObjectURL = jest.fn(() => 'blob:mock-url');

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  clear: jest.fn(),
  removeItem: jest.fn(),
};
Object.defineProperty(window, 'localStorage', { value: localStorageMock });

describe('Customization Component', () => {
  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
    
    // Default mock API response
    api.fetchCustomization.mockResolvedValue({
      company_name: 'Test Company',
      privacy_policy_url: 'https://test.com/privacy',
      primary_color: '#1976d2',
      secondary_color: '#dc004e',
      logo_url: 'https://test.com/logo.png'
    });
    
    api.saveCustomization.mockResolvedValue({
      success: true,
      company_name: 'Updated Company',
      privacy_policy_url: 'https://updated.com/privacy',
      primary_color: '#2196f3',
      secondary_color: '#f50057',
      logo_url: 'https://updated.com/logo.png'
    });
  });

  test('renders all sections correctly', async () => {
    await act(async () => {
      render(<Customization />);
    });

    // Check page title
    expect(screen.getByText('Optin Customization')).toBeInTheDocument();
    
    // Check if all sections are rendered
    expect(screen.getByTestId('branding-section')).toBeInTheDocument();
    expect(screen.getByTestId('email-provider-section')).toBeInTheDocument();
    expect(screen.getByTestId('sms-provider-section')).toBeInTheDocument();
  });

  test('fetches and displays customization data', async () => {
    await act(async () => {
      render(<Customization />);
    });
    
    // Check if API was called
    expect(api.fetchCustomization).toHaveBeenCalledTimes(1);
    
    // Check if data was passed to BrandingSection
    expect(screen.getByText('Company: Test Company')).toBeInTheDocument();
    expect(screen.getByText('Privacy: https://test.com/privacy')).toBeInTheDocument();
    expect(screen.getByText('Primary: #1976d2')).toBeInTheDocument();
    expect(screen.getByText('Secondary: #dc004e')).toBeInTheDocument();
  });
  
  test('handles saving branding data', async () => {
    await act(async () => {
      render(<Customization />);
    });
    
    // Click save button
    const saveButton = screen.getByTestId('save-branding-button');
    await act(async () => {
      fireEvent.click(saveButton);
    });
    
    // Verify API call
    expect(api.saveCustomization).toHaveBeenCalledTimes(1);
    expect(api.saveCustomization).toHaveBeenCalledWith(expect.objectContaining({
      company_name: 'Test Company',
      privacy_policy_url: 'https://test.com/privacy',
      primary: '#1976d2',
      secondary: '#dc004e'
    }));
    
    // Verify data is fetched again after save
    expect(api.fetchCustomization).toHaveBeenCalledTimes(2);
  });
  
  test('handles API fetch error gracefully', async () => {
    // Mock error response
    api.fetchCustomization.mockRejectedValueOnce(new Error('Failed to fetch data'));
    
    await act(async () => {
      render(<Customization />);
    });
    
    // Should still render components
    expect(screen.getByTestId('branding-section')).toBeInTheDocument();
    expect(screen.getByTestId('email-provider-section')).toBeInTheDocument();
    expect(screen.getByTestId('sms-provider-section')).toBeInTheDocument();
    
    // Alert should eventually be shown
    await waitFor(() => {
      expect(screen.getByText('Failed to load customization data')).toBeInTheDocument();
    });
  });
  
  test('handles API save error gracefully', async () => {
    // Setup API to return error on save
    api.saveCustomization.mockRejectedValueOnce(new Error('Failed to save branding'));
    
    await act(async () => {
      render(<Customization />);
    });
    
    // Click save button
    const saveButton = screen.getByTestId('save-branding-button');
    await act(async () => {
      fireEvent.click(saveButton);
    });
    
    // Alert should eventually be shown
    await waitFor(() => {
      expect(screen.getByText('Failed to save branding settings')).toBeInTheDocument();
    });
  });
  
  test('handles empty customization data', async () => {
    // Set API to return empty object
    api.fetchCustomization.mockResolvedValueOnce({});
    
    await act(async () => {
      render(<Customization />);
    });
    
    // Default values should be used
    const brandingSection = screen.getByTestId('branding-section');
    expect(brandingSection).toHaveTextContent('Primary: #1976d2'); // Default primary color
    expect(brandingSection).toHaveTextContent('Secondary: #dc004e'); // Default secondary color
  });
});
