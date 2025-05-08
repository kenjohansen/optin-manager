/**
 * ProviderSection.test.jsx
 * 
 * Tests for the ProviderSection component.
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import ProviderSection from './ProviderSection';

describe('ProviderSection Component', () => {
  // Mock props for email provider
  const mockEmailProps = {
    type: 'email',
    provider: 'aws_ses',
    creds: {
      accessKey: 'test-access-key',
      secretKey: 'test-secret-key',
      region: 'us-west-2',
      fromAddress: 'test@example.com'
    },
    status: '',
    credsSaved: false,
    onSave: jest.fn(),
    onTest: jest.fn(),
    onDelete: jest.fn(),
    credSaving: false,
    credError: '',
    testResult: '',
    primaryColor: '#1976d2',
    secondaryColor: '#9c27b0',
    setProvider: jest.fn(),
    setCreds: jest.fn()
  };

  // Mock props for SMS provider
  const mockSmsProps = {
    ...mockEmailProps,
    type: 'sms',
    provider: 'aws_sns',
    creds: {
      accessKey: 'test-access-key',
      secretKey: 'test-secret-key',
      region: 'us-west-2'
    }
  };

  test('renders email provider form correctly', () => {
    render(<ProviderSection {...mockEmailProps} />);
    
    // Check if all form elements are rendered
    expect(screen.getByLabelText('Sender Email Address')).toHaveValue('test@example.com');
    expect(screen.getByLabelText('Email Provider')).toHaveValue('aws_ses');
    expect(screen.getByLabelText('Access Key')).toHaveValue('test-access-key');
    expect(screen.getByLabelText('Secret Key')).toHaveValue('test-secret-key');
    expect(screen.getByLabelText('Region')).toHaveValue('us-west-2');
    
    // Check buttons
    expect(screen.getByText('Save')).toBeInTheDocument();
    expect(screen.getByText('Test')).toBeInTheDocument();
    expect(screen.getByText('Delete')).toBeInTheDocument();
  });

  test('renders SMS provider form correctly', () => {
    render(<ProviderSection {...mockSmsProps} />);
    
    // Check if all form elements are rendered
    expect(screen.queryByLabelText('Sender Email Address')).not.toBeInTheDocument(); // Email-specific field
    expect(screen.getByLabelText('SMS Provider')).toHaveValue('aws_sns');
    expect(screen.getByLabelText('Access Key')).toHaveValue('test-access-key');
    expect(screen.getByLabelText('Secret Key')).toHaveValue('test-secret-key');
    expect(screen.getByLabelText('Region')).toHaveValue('us-west-2');
    
    // Check buttons
    expect(screen.getByText('Save')).toBeInTheDocument();
    expect(screen.getByText('Test')).toBeInTheDocument();
    expect(screen.getByText('Delete')).toBeInTheDocument();
  });

  test('handles input changes correctly for email provider', () => {
    render(<ProviderSection {...mockEmailProps} />);
    
    // Test fromAddress input
    const fromAddressInput = screen.getByLabelText('Sender Email Address');
    fireEvent.change(fromAddressInput, { target: { value: 'new@example.com' } });
    expect(mockEmailProps.setCreds).toHaveBeenCalled();
    
    // Test provider selection
    const providerSelect = screen.getByLabelText('Email Provider');
    fireEvent.change(providerSelect, { target: { value: 'aws_ses' } });
    expect(mockEmailProps.setProvider).toHaveBeenCalledWith('aws_ses');
    
    // Test access key input
    const accessKeyInput = screen.getByLabelText('Access Key');
    fireEvent.change(accessKeyInput, { target: { value: 'new-access-key' } });
    expect(mockEmailProps.setCreds).toHaveBeenCalled();
    
    // Test secret key input
    const secretKeyInput = screen.getByLabelText('Secret Key');
    fireEvent.change(secretKeyInput, { target: { value: 'new-secret-key' } });
    expect(mockEmailProps.setCreds).toHaveBeenCalled();
    
    // Test region input
    const regionInput = screen.getByLabelText('Region');
    fireEvent.change(regionInput, { target: { value: 'us-east-1' } });
    expect(mockEmailProps.setCreds).toHaveBeenCalled();
  });

  test('handles button clicks correctly', () => {
    render(<ProviderSection {...mockEmailProps} />);
    
    // Test Save button
    const saveButton = screen.getByText('Save');
    fireEvent.click(saveButton);
    expect(mockEmailProps.onSave).toHaveBeenCalledWith('email');
    
    // Test Test button
    const testButton = screen.getByText('Test');
    fireEvent.click(testButton);
    expect(mockEmailProps.onTest).toHaveBeenCalledWith('email');
    
    // Test Delete button
    const deleteButton = screen.getByText('Delete');
    fireEvent.click(deleteButton);
    expect(mockEmailProps.onDelete).toHaveBeenCalledWith('email');
  });

  test('displays "Update" instead of "Save" when credentials are saved', () => {
    const savedProps = { ...mockEmailProps, credsSaved: true };
    render(<ProviderSection {...savedProps} />);
    
    expect(screen.getByText('Update')).toBeInTheDocument();
    expect(screen.queryByText('Save')).not.toBeInTheDocument();
  });

  test('displays "Update" when connection is tested', () => {
    const testedProps = { ...mockEmailProps, status: 'tested' };
    render(<ProviderSection {...testedProps} />);
    
    expect(screen.getByText('Update')).toBeInTheDocument();
    expect(screen.queryByText('Save')).not.toBeInTheDocument();
  });

  test('displays error message when provided', () => {
    const errorProps = { ...mockEmailProps, credError: 'Failed to save credentials' };
    render(<ProviderSection {...errorProps} />);
    
    expect(screen.getByText('Failed to save credentials')).toBeInTheDocument();
  });

  test('displays test result when provided', () => {
    const resultProps = { ...mockEmailProps, testResult: 'Connection successful' };
    render(<ProviderSection {...resultProps} />);
    
    expect(screen.getByText('Connection successful')).toBeInTheDocument();
  });

  test('disables Save button when saving is in progress', () => {
    const savingProps = { ...mockEmailProps, credSaving: true };
    render(<ProviderSection {...savingProps} />);
    
    const saveButton = screen.getByText('Save');
    expect(saveButton).toBeDisabled();
  });
});
