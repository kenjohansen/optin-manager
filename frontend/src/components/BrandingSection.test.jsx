/**
 * BrandingSection.test.jsx
 * 
 * Tests for the BrandingSection component.
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import BrandingSection from './BrandingSection';

describe('BrandingSection Component', () => {
  const mockProps = {
    logoPreview: 'https://example.com/logo.png',
    handleLogoChange: jest.fn(),
    companyName: 'Test Company',
    setCompanyName: jest.fn(),
    privacyPolicy: 'https://example.com/privacy',
    setPrivacyPolicy: jest.fn(),
    primary: '#1976d2',
    setPrimary: jest.fn(),
    secondary: '#9c27b0',
    setSecondary: jest.fn(),
    saving: false,
    handleSave: jest.fn(e => e.preventDefault())
  };

  test('renders all form inputs correctly', () => {
    render(<BrandingSection {...mockProps} />);
    
    // Check if all form elements are rendered
    expect(screen.getByText('Branding')).toBeInTheDocument();
    expect(screen.getByLabelText('Company Name')).toHaveValue('Test Company');
    expect(screen.getByLabelText('Privacy Policy URL')).toHaveValue('https://example.com/privacy');
    expect(screen.getByLabelText('Primary Color')).toHaveValue('#1976d2');
    expect(screen.getByLabelText('Secondary Color')).toHaveValue('#9c27b0');
    expect(screen.getByText('Upload Logo')).toBeInTheDocument();
    expect(screen.getByText('Save')).toBeInTheDocument();
    
    // Check if logo preview is rendered
    const logoImg = screen.getByAltText('Logo Preview');
    expect(logoImg).toBeInTheDocument();
    expect(logoImg).toHaveAttribute('src', 'https://example.com/logo.png');
  });

  test('handles form input changes correctly', () => {
    render(<BrandingSection {...mockProps} />);
    
    // Test company name input
    const companyNameInput = screen.getByLabelText('Company Name');
    fireEvent.change(companyNameInput, { target: { value: 'New Company Name' } });
    expect(mockProps.setCompanyName).toHaveBeenCalledWith('New Company Name');
    
    // Test privacy policy input
    const privacyPolicyInput = screen.getByLabelText('Privacy Policy URL');
    fireEvent.change(privacyPolicyInput, { target: { value: 'https://example.com/new-privacy' } });
    expect(mockProps.setPrivacyPolicy).toHaveBeenCalledWith('https://example.com/new-privacy');
    
    // Test primary color input
    const primaryColorInput = screen.getByLabelText('Primary Color');
    fireEvent.change(primaryColorInput, { target: { value: '#ff0000' } });
    expect(mockProps.setPrimary).toHaveBeenCalledWith('#ff0000');
    
    // Test secondary color input
    const secondaryColorInput = screen.getByLabelText('Secondary Color');
    fireEvent.change(secondaryColorInput, { target: { value: '#00ff00' } });
    expect(mockProps.setSecondary).toHaveBeenCalledWith('#00ff00');
  });

  test('handles logo upload correctly', () => {
    render(<BrandingSection {...mockProps} />);
    
    // Find the hidden file input
    const fileInput = document.querySelector('input[type="file"]');
    expect(fileInput).toBeInTheDocument();
    
    // Create a mock file and trigger change
    const file = new File(['dummy content'], 'example.png', { type: 'image/png' });
    fireEvent.change(fileInput, { target: { files: [file] } });
    
    // Check if handleLogoChange was called
    expect(mockProps.handleLogoChange).toHaveBeenCalled();
  });

  test('handles form submission correctly', () => {
    render(<BrandingSection {...mockProps} />);
    
    // Submit the form
    const saveButton = screen.getByText('Save');
    fireEvent.click(saveButton);
    
    // Check if handleSave was called
    expect(mockProps.handleSave).toHaveBeenCalled();
  });

  test('displays saving state correctly', () => {
    const savingProps = { ...mockProps, saving: true };
    render(<BrandingSection {...savingProps} />);
    
    // Check if the button text changes to "Saving..."
    expect(screen.getByText('Saving...')).toBeInTheDocument();
    expect(screen.queryByText('Save')).not.toBeInTheDocument();
  });

  test('renders without logo preview when not provided', () => {
    const propsWithoutLogo = { ...mockProps, logoPreview: null };
    render(<BrandingSection {...propsWithoutLogo} />);
    
    // Check that logo preview is not rendered
    expect(screen.queryByAltText('Logo Preview')).not.toBeInTheDocument();
  });
});
