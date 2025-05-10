/**
 * Tests for providerSecrets.js API module
 */

// Mock axios before importing any modules
jest.mock('axios');

// Mock localStorage
Object.defineProperty(window, 'localStorage', {
  value: {
    getItem: jest.fn(() => 'test-token'),
    setItem: jest.fn(),
    removeItem: jest.fn(),
    clear: jest.fn()
  },
  writable: true
});

// Import modules after setting up mocks
import axios from 'axios';
import * as providerSecrets from './providerSecrets';

// Create spies for the module functions
jest.spyOn(providerSecrets, 'setProviderSecret');
jest.spyOn(providerSecrets, 'getSecretsStatus');
jest.spyOn(providerSecrets, 'testProviderConnection');
jest.spyOn(providerSecrets, 'deleteProviderSecret');

describe('Provider Secrets API', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
    
    // Reset localStorage mock to return token by default
    window.localStorage.getItem.mockReturnValue('test-token');
    
    // Setup default axios responses
    axios.post.mockResolvedValue({ data: { success: true } });
    axios.get.mockResolvedValue({ data: { email: true, sms: false } });
  });

  test('setProviderSecret sends correct data and includes auth token', async () => {
    const providerData = {
      providerType: 'email',
      accessKey: 'test-access-key',
      secretKey: 'test-secret-key',
      region: 'us-west-2',
      fromAddress: 'test@example.com'
    };
    
    await providerSecrets.setProviderSecret(providerData);
    
    // Verify axios was called with the correct parameters
    expect(axios.post).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/provider-secrets/set',
      {
        provider_type: 'email',
        access_key: 'test-access-key',
        secret_key: 'test-secret-key',
        region: 'us-west-2',
        from_address: 'test@example.com',
      },
      {
        headers: {
          Authorization: 'Bearer test-token'
        }
      }
    );
  });

  test('getSecretsStatus fetches provider status with auth token', async () => {
    const result = await providerSecrets.getSecretsStatus();
    
    // Verify axios was called with the correct parameters
    expect(axios.get).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/provider-secrets/status',
      {
        headers: {
          Authorization: 'Bearer test-token'
        }
      }
    );
    
    // Verify the result
    expect(result).toEqual({ email: true, sms: false });
  });

  test('testProviderConnection tests connection with correct provider type', async () => {
    const result = await providerSecrets.testProviderConnection({ providerType: 'sms' });
    
    // Verify axios was called with the correct parameters
    expect(axios.post).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/provider-secrets/test',
      { provider_type: 'sms' },
      {
        headers: {
          Authorization: 'Bearer test-token'
        }
      }
    );
    
    // Verify the result
    expect(result).toEqual({ success: true });
  });

  test('deleteProviderSecret deletes provider secret with correct type', async () => {
    const result = await providerSecrets.deleteProviderSecret({ providerType: 'email' });
    
    // Verify axios was called with the correct parameters
    expect(axios.post).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/provider-secrets/delete',
      { provider_type: 'email' },
      {
        headers: {
          Authorization: 'Bearer test-token'
        }
      }
    );
    
    // Verify the result
    expect(result).toEqual({ success: true });
  });

  test('API functions handle missing auth token', async () => {
    // Set localStorage to return null for access_token
    window.localStorage.getItem.mockReturnValue(null);
    
    await providerSecrets.setProviderSecret({ providerType: 'email' });
    
    // Should call API without Authorization header
    expect(axios.post).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/provider-secrets/set',
      { provider_type: 'email', access_key: undefined, secret_key: undefined, region: undefined, from_address: undefined },
      { headers: {} }
    );
  });

  test('API functions handle errors', async () => {
    // Mock axios to reject with an error
    const errorResponse = { response: { data: { detail: 'Error message' }, status: 500 } };
    axios.post.mockRejectedValueOnce(errorResponse);
    
    // Call should throw the error
    await expect(providerSecrets.setProviderSecret({ providerType: 'email' })).rejects.toEqual(errorResponse);
  });
});
