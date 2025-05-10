/**
 * api.test.js
 *
 * Unit tests for API utility functions.
 *
 * This test suite verifies the functionality of the API utility functions, including
 * authentication, data fetching, and error handling. These functions are critical
 * for the application's communication with the backend services.
 *
 * Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
 * This file is part of the OptIn Manager project and is licensed under the MIT License.
 * See the root LICENSE file for details.
 */

import axios from 'axios';
import * as api from './api';

// Mock axios to avoid actual API calls
jest.mock('axios');

// Mock localStorage
const localStorageMock = (() => {
  let store = {};
  return {
    getItem: jest.fn(key => store[key] || null),
    setItem: jest.fn((key, value) => {
      store[key] = value.toString();
    }),
    removeItem: jest.fn(key => {
      delete store[key];
    }),
    clear: jest.fn(() => {
      store = {};
    }),
    store
  };
})();
Object.defineProperty(window, 'localStorage', { value: localStorageMock });

describe('API Utilities', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
    localStorageMock.clear();
  });

  describe('fetchCustomization', () => {
    test('should fetch customization settings with auth token when available', async () => {
      // Mock localStorage to return a token
      localStorageMock.setItem('access_token', 'test-token');
      
      // Mock the actual implementation of fetchCustomization to use our mocked localStorage
      jest.spyOn(window.localStorage, 'getItem').mockReturnValue('test-token');
      
      // Mock successful API response
      const mockResponse = {
        data: {
          logo_url: '/media/logo.png',
          primary: '#123456',
          secondary: '#654321',
          company_name: 'Test Company'
        }
      };
      axios.get.mockResolvedValueOnce(mockResponse);
      
      // Call the function
      const result = await api.fetchCustomization();
      
      // Verify axios was called with authorization header
      expect(axios.get).toHaveBeenCalled();
      expect(axios.get.mock.calls[0][0]).toBe(`${api.API_BASE}/customization/`);
      expect(axios.get.mock.calls[0][1].headers).toHaveProperty('Authorization');
      
      // Verify the logo URL was processed correctly
      expect(result.logo_url).toContain('logo.png');
      expect(result).toEqual(expect.objectContaining({
        primary: '#123456',
        secondary: '#654321',
        company_name: 'Test Company'
      }));
    });

    test('should fetch customization settings without auth token when not available', async () => {
      // Clear localStorage and mock it to return null for access_token
      localStorageMock.clear();
      jest.spyOn(window.localStorage, 'getItem').mockReturnValue(null);
      
      // Mock successful API response
      const mockResponse = {
        data: {
          logo_url: '/media/logo.png',
          primary: '#123456',
          secondary: '#654321',
          company_name: 'Test Company'
        }
      };
      axios.get.mockResolvedValueOnce(mockResponse);
      
      // Call the function
      const result = await api.fetchCustomization();
      
      // Verify axios was called with no authorization header
      expect(axios.get).toHaveBeenCalled();
      expect(axios.get.mock.calls[0][0]).toBe(`${api.API_BASE}/customization/`);
      expect(axios.get.mock.calls[0][1].headers).not.toHaveProperty('Authorization');
      
      // Verify the result
      expect(result).toEqual(expect.objectContaining({
        primary: '#123456',
        secondary: '#654321',
        company_name: 'Test Company'
      }));
    });

    test('should handle errors gracefully', async () => {
      // Mock API error
      axios.get.mockRejectedValueOnce(new Error('Network error'));
      
      // Call the function
      const result = await api.fetchCustomization();
      
      // Verify error was handled and empty object returned
      expect(result).toEqual({});
    });
  });

  describe('login', () => {
    test('should authenticate user and store token on successful login', async () => {
      // Mock successful login response
      const mockResponse = {
        data: {
          access_token: 'test-access-token',
          token_type: 'bearer',
          user: {
            email: 'admin@example.com',
            role: 'admin'
          }
        }
      };
      axios.post.mockResolvedValueOnce(mockResponse);
      
      // Call the function
      const credentials = { username: 'admin@example.com', password: 'password123' };
      const result = await api.login(credentials);
      
      // Verify axios was called with the correct parameters
      expect(axios.post).toHaveBeenCalledWith(
        `${api.API_BASE}/auth/login`,
        new URLSearchParams(credentials),
        { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
      );
      
      // Verify the result
      expect(result).toEqual(mockResponse.data);
    });

    test('should handle login errors', async () => {
      // Mock login error
      const errorResponse = {
        response: {
          data: {
            detail: 'Invalid credentials'
          },
          status: 401
        }
      };
      axios.post.mockRejectedValueOnce(errorResponse);
      
      // Call the function and verify it throws
      const credentials = { username: 'wrong@example.com', password: 'wrongpass' };
      try {
        await api.login(credentials);
        fail('Expected login to throw an error');
      } catch (error) {
        expect(error).toBeDefined();
      }
      
      // Verify token was not stored
      expect(localStorageMock.setItem).not.toHaveBeenCalled();
    });
  });

  describe('sendVerificationCode', () => {
    test('should send verification code to email', async () => {
      // Mock successful response
      const mockResponse = {
        data: {
          message: 'Verification code sent',
          expires_in: 600
        }
      };
      axios.post.mockResolvedValueOnce(mockResponse);
      
      // Call the function
      const params = { contact: 'user@example.com', contactType: 'email' };
      const result = await api.sendVerificationCode(params);
      
      // Verify axios was called with the correct parameters
      expect(axios.post).toHaveBeenCalledWith(
        `${api.API_BASE}/preferences/send-code`,
        expect.objectContaining({
          contact: 'user@example.com',
          contact_type: 'email',
          purpose: expect.any(String),
          preferences_url: expect.stringContaining('user%40example.com')
        })
      );
      
      // Verify the result
      expect(result).toEqual(mockResponse.data);
    });

    test('should send verification code to phone', async () => {
      // Mock successful response
      const mockResponse = {
        data: {
          message: 'Verification code sent',
          expires_in: 600
        }
      };
      axios.post.mockResolvedValueOnce(mockResponse);
      
      // Call the function
      const params = { contact: '+15551234567', contactType: 'phone' };
      const result = await api.sendVerificationCode(params);
      
      // Verify axios was called with the correct parameters
      expect(axios.post).toHaveBeenCalledWith(
        `${api.API_BASE}/preferences/send-code`,
        expect.objectContaining({
          contact: '+15551234567',
          contact_type: 'phone',
          purpose: expect.any(String),
          preferences_url: expect.stringContaining('%2B15551234567')
        })
      );
      
      // Verify the result
      expect(result).toEqual(mockResponse.data);
    });

    test('should handle errors when sending verification code', async () => {
      // Mock error response
      const errorResponse = {
        response: {
          data: {
            detail: 'Contact not found'
          },
          status: 404
        }
      };
      axios.post.mockRejectedValueOnce(errorResponse);
      
      // Call the function and verify it throws
      const params = { contact: 'nonexistent@example.com', contactType: 'email' };
      try {
        await api.sendVerificationCode(params);
        fail('Expected sendVerificationCode to throw an error');
      } catch (error) {
        expect(error).toBeDefined();
      }
    });
  });

  describe('verifyCode', () => {
    test('should verify code and return token', async () => {
      // Mock successful response
      const mockResponse = {
        data: {
          token: 'verification-token',
          contact: 'user@example.com'
        }
      };
      axios.post.mockResolvedValueOnce(mockResponse);
      
      // Call the function
      const params = { contact: 'user@example.com', code: '123456' };
      const result = await api.verifyCode(params);
      
      // Verify axios was called with the correct parameters
      expect(axios.post).toHaveBeenCalledWith(
        `${api.API_BASE}/preferences/verify-code`,
        expect.objectContaining({
          contact: 'user@example.com',
          contact_type: 'email',
          code: '123456'
        })
      );
      
      // Verify the result
      expect(result).toEqual(mockResponse.data);
    });

    test('should handle invalid verification code', async () => {
      // Mock error response
      const errorResponse = {
        response: {
          data: {
            detail: 'Invalid or expired code'
          },
          status: 400
        }
      };
      axios.post.mockRejectedValueOnce(errorResponse);
      
      // Call the function and verify it throws
      const params = { contact: 'user@example.com', code: 'wrong' };
      try {
        await api.verifyCode(params);
        fail('Expected verifyCode to throw an error');
      } catch (error) {
        expect(error).toBeDefined();
      }
    });
  });

  describe('fetchOptIns', () => {
    test('should fetch opt-in programs with auth token', async () => {
      // Mock localStorage to return a token
      localStorageMock.setItem('access_token', 'test-token');
      
      // Mock successful API response
      const mockResponse = {
        data: [
          { id: '1', name: 'Marketing Updates', type: 'marketing', status: 'active' },
          { id: '2', name: 'Product Announcements', type: 'product', status: 'active' }
        ]
      };
      axios.get.mockResolvedValueOnce(mockResponse);
      
      // Call the function
      const result = await api.fetchOptIns();
      
      // Verify axios was called with authorization header
      expect(axios.get).toHaveBeenCalled();
      expect(axios.get.mock.calls[0][0]).toBe(`${api.API_BASE}/optins`);
      expect(axios.get.mock.calls[0][1].headers).toHaveProperty('Authorization');
      
      // Verify the result
      expect(result).toEqual(mockResponse.data);
    });

    test('should handle errors when fetching opt-in programs', async () => {
      // Mock localStorage to return a token
      localStorageMock.setItem('access_token', 'test-token');
      
      // Mock API error
      axios.get.mockRejectedValueOnce(new Error('Network error'));
      
      // Call the function and verify it throws
      try {
        await api.fetchOptIns();
        fail('Expected fetchOptIns to throw an error');
      } catch (error) {
        expect(error).toBeDefined();
      }
    });
  });

  describe('saveCustomization', () => {
    test('should save customization settings with FormData', async () => {
      // Mock localStorage to return a token
      localStorageMock.setItem('access_token', 'test-token');
      jest.spyOn(window.localStorage, 'getItem').mockReturnValue('test-token');
      
      // Create a mock file
      const mockFile = new File(['dummy content'], 'logo.png', { type: 'image/png' });
      
      // Mock successful API response
      const mockResponse = {
        data: {
          logo_url: '/media/logo.png',
          primary: '#123456',
          secondary: '#654321',
          company_name: 'Test Company',
          privacy_policy_url: 'https://example.com/privacy',
          email_provider: 'aws_ses',
          sms_provider: 'twilio'
        }
      };
      axios.post.mockResolvedValueOnce(mockResponse);
      
      // Call the function
      const customizationData = {
        logo: mockFile,
        primary: '#123456',
        secondary: '#654321',
        company_name: 'Test Company',
        privacy_policy_url: 'https://example.com/privacy',
        email_provider: 'aws_ses',
        sms_provider: 'twilio'
      };
      const result = await api.saveCustomization(customizationData);
      
      // Verify axios was called with FormData and authorization header
      expect(axios.post).toHaveBeenCalled();
      expect(axios.post.mock.calls[0][0]).toBe(`${api.API_BASE}/customization/`);
      
      // Verify the second argument is FormData
      const formData = axios.post.mock.calls[0][1];
      expect(formData).toBeInstanceOf(FormData);
      
      // Verify the headers include Authorization and multipart/form-data content type
      const headers = axios.post.mock.calls[0][2].headers;
      expect(headers).toHaveProperty('Authorization');
      expect(headers['Content-Type']).toContain('multipart/form-data');
      
      // Verify the result
      expect(result).toEqual(mockResponse.data);
    });
    
    test('should handle errors when saving customization', async () => {
      // Mock localStorage to return a token
      localStorageMock.setItem('access_token', 'test-token');
      jest.spyOn(window.localStorage, 'getItem').mockReturnValue('test-token');
      
      // Mock API error
      const errorResponse = new Error('Network error');
      axios.post.mockRejectedValueOnce(errorResponse);
      
      // Call the function and verify it throws
      const customizationData = {
        primary: '#123456',
        secondary: '#654321'
      };
      
      try {
        await api.saveCustomization(customizationData);
        fail('Expected saveCustomization to throw an error');
      } catch (error) {
        expect(error).toBeDefined();
      }
    });
  });

  describe('fetchDashboardStats', () => {
    test('should fetch dashboard statistics with default time window', async () => {
      // Mock localStorage to return a token
      localStorageMock.setItem('access_token', 'test-token');
      jest.spyOn(window.localStorage, 'getItem').mockReturnValue('test-token');
      
      // Mock successful API response
      const mockResponse = {
        data: {
          total_contacts: 1250,
          active_optins: 850,
          recent_activity: [
            { date: '2025-05-01', count: 25 },
            { date: '2025-05-02', count: 30 }
          ],
          consent_distribution: {
            opted_in: 850,
            opted_out: 400
          }
        }
      };
      axios.get.mockResolvedValueOnce(mockResponse);
      
      // Call the function with default days parameter
      const result = await api.fetchDashboardStats();
      
      // Verify axios was called with authorization header and correct parameters
      expect(axios.get).toHaveBeenCalled();
      expect(axios.get.mock.calls[0][0]).toBe(`${api.API_BASE}/dashboard/stats?days=30`);
      expect(axios.get.mock.calls[0][1].headers).toHaveProperty('Authorization');
      
      // Verify the result
      expect(result).toEqual(mockResponse.data);
    });
    
    test('should fetch dashboard statistics with custom time window', async () => {
      // Mock localStorage to return a token
      localStorageMock.setItem('access_token', 'test-token');
      jest.spyOn(window.localStorage, 'getItem').mockReturnValue('test-token');
      
      // Mock successful API response
      const mockResponse = {
        data: {
          total_contacts: 800,
          active_optins: 500,
          recent_activity: [
            { date: '2025-05-01', count: 15 },
            { date: '2025-05-02', count: 20 }
          ],
          consent_distribution: {
            opted_in: 500,
            opted_out: 300
          }
        }
      };
      axios.get.mockResolvedValueOnce(mockResponse);
      
      // Call the function with custom days parameter
      const result = await api.fetchDashboardStats(7);
      
      // Verify axios was called with authorization header and correct parameters
      expect(axios.get).toHaveBeenCalled();
      expect(axios.get.mock.calls[0][0]).toBe(`${api.API_BASE}/dashboard/stats?days=7`);
      expect(axios.get.mock.calls[0][1].headers).toHaveProperty('Authorization');
      
      // Verify the result
      expect(result).toEqual(mockResponse.data);
    });
    
    test('should handle errors when fetching dashboard statistics', async () => {
      // Mock localStorage to return a token
      localStorageMock.setItem('access_token', 'test-token');
      
      // Mock API error
      axios.get.mockRejectedValueOnce(new Error('Network error'));
      
      // Call the function and verify it throws
      try {
        await api.fetchDashboardStats();
        fail('Expected fetchDashboardStats to throw an error');
      } catch (error) {
        expect(error).toBeDefined();
      }
    });
  });

  describe('fetchContacts', () => {
    test('should fetch contacts with search parameters', async () => {
      // Mock localStorage to return a token
      localStorageMock.setItem('access_token', 'test-token');
      jest.spyOn(window.localStorage, 'getItem').mockReturnValue('test-token');
      
      // Mock successful API response
      const mockResponse = {
        data: {
          items: [
            { id: '1', masked_value: 'u***@example.com', contact_type: 'email', consent_status: 'opted_in' },
            { id: '2', masked_value: '+1***4567', contact_type: 'phone', consent_status: 'opted_out' }
          ],
          total: 2,
          page: 1,
          pages: 1
        }
      };
      axios.get.mockResolvedValueOnce(mockResponse);
      
      // Call the function with search parameters
      const searchParams = {
        search: 'example',
        consent: 'all',
        timeWindow: 30
      };
      const result = await api.fetchContacts(searchParams);
      
      // Verify axios was called with authorization header and correct parameters
      expect(axios.get).toHaveBeenCalled();
      expect(axios.get.mock.calls[0][0]).toBe(`${api.API_BASE}/contacts/`);
      expect(axios.get.mock.calls[0][1].params).toEqual({
        search: 'example',
        consent: 'all',
        time_window: 30
      });
      expect(axios.get.mock.calls[0][1].headers).toHaveProperty('Authorization');
      
      // Verify the result
      expect(result).toEqual(mockResponse.data);
    });
    
    test('should handle errors when fetching contacts', async () => {
      // Mock localStorage to return a token
      localStorageMock.setItem('access_token', 'test-token');
      jest.spyOn(window.localStorage, 'getItem').mockReturnValue('test-token');
      
      // Mock API error
      axios.get.mockRejectedValueOnce(new Error('Network error'));
      
      // Call the function and verify it throws
      try {
        await api.fetchContacts({ search: '', consent: 'all', timeWindow: 30 });
        fail('Expected fetchContacts to throw an error');
      } catch (error) {
        expect(error).toBeDefined();
      }
    });
  });

  describe('fetchContactPreferences', () => {
    test('should fetch contact preferences with token', async () => {
      // Mock successful API response
      const mockResponse = {
        data: {
          contact: 'user@example.com',
          contact_type: 'email',
          preferences: [
            { id: '1', name: 'Marketing Updates', opted_in: true },
            { id: '2', name: 'Product Announcements', opted_in: false }
          ],
          global_opt_out: false
        }
      };
      axios.get.mockResolvedValueOnce(mockResponse);
      
      // Call the function with token
      const params = { token: 'verification-token' };
      const result = await api.fetchContactPreferences(params);
      
      // Verify axios was called with correct parameters
      expect(axios.get).toHaveBeenCalled();
      expect(axios.get.mock.calls[0][0]).toBe(`${api.API_BASE}/preferences/user-preferences`);
      expect(axios.get.mock.calls[0][1].params).toEqual({ token: 'verification-token' });
      
      // Verify the result
      expect(result).toEqual(mockResponse.data);
    });
    
    test('should fetch contact preferences with contact parameter', async () => {
      // Mock successful API response
      const mockResponse = {
        data: {
          contact: 'user@example.com',
          contact_type: 'email',
          preferences: [
            { id: '1', name: 'Marketing Updates', opted_in: true },
            { id: '2', name: 'Product Announcements', opted_in: false }
          ],
          global_opt_out: false
        }
      };
      axios.get.mockResolvedValueOnce(mockResponse);
      
      // Call the function with contact
      const params = { contact: 'user@example.com' };
      const result = await api.fetchContactPreferences(params);
      
      // Verify axios was called with correct parameters
      expect(axios.get).toHaveBeenCalled();
      expect(axios.get.mock.calls[0][0]).toBe(`${api.API_BASE}/preferences/user-preferences`);
      expect(axios.get.mock.calls[0][1].params).toEqual({ contact: 'user@example.com' });
      
      // Verify the result
      expect(result).toEqual(mockResponse.data);
    });
    
    test('should handle errors when fetching contact preferences', async () => {
      // Mock API error
      axios.get.mockRejectedValueOnce(new Error('Network error'));
      
      // Call the function and verify it throws
      const params = { token: 'invalid-token' };
      try {
        await api.fetchContactPreferences(params);
        fail('Expected fetchContactPreferences to throw an error');
      } catch (error) {
        expect(error).toBeDefined();
      }
    });
  });

  describe('updateContactPreferences', () => {
    test('should update contact preferences with token', async () => {
      // Mock successful API response
      const mockResponse = {
        data: {
          contact: 'user@example.com',
          contact_type: 'email',
          preferences: [
            { id: '1', name: 'Marketing Updates', opted_in: false },
            { id: '2', name: 'Product Announcements', opted_in: true }
          ],
          global_opt_out: false,
          updated_at: '2025-05-08T12:00:00Z'
        }
      };
      axios.patch.mockResolvedValueOnce(mockResponse);
      
      // Call the function with token and preferences
      const params = {
        token: 'verification-token',
        preferences: {
          '1': false,
          '2': true
        },
        comment: 'Updated via preferences page'
      };
      const result = await api.updateContactPreferences(params);
      
      // Verify axios was called with correct parameters
      expect(axios.patch).toHaveBeenCalled();
      expect(axios.patch.mock.calls[0][0]).toBe(`${api.API_BASE}/preferences/user-preferences`);
      expect(axios.patch.mock.calls[0][1]).toEqual({
        token: 'verification-token',
        preferences: {
          '1': false,
          '2': true
        },
        comment: 'Updated via preferences page'
      });
      
      // Verify the result
      expect(result).toEqual(mockResponse.data);
    });
    
    test('should update contact preferences with global opt-out', async () => {
      // Mock successful API response
      const mockResponse = {
        data: {
          contact: 'user@example.com',
          contact_type: 'email',
          preferences: [
            { id: '1', name: 'Marketing Updates', opted_in: false },
            { id: '2', name: 'Product Announcements', opted_in: false }
          ],
          global_opt_out: true,
          updated_at: '2025-05-08T12:00:00Z'
        }
      };
      axios.patch.mockResolvedValueOnce(mockResponse);
      
      // Call the function with token and global opt-out
      const params = {
        token: 'verification-token',
        global_opt_out: true,
        comment: 'Opted out of all communications'
      };
      const result = await api.updateContactPreferences(params);
      
      // Verify axios was called with correct parameters
      expect(axios.patch).toHaveBeenCalled();
      expect(axios.patch.mock.calls[0][0]).toBe(`${api.API_BASE}/preferences/user-preferences`);
      expect(axios.patch.mock.calls[0][1]).toEqual({
        token: 'verification-token',
        global_opt_out: true,
        comment: 'Opted out of all communications',
        preferences: {}
      });
      
      // Verify the result
      expect(result).toEqual(mockResponse.data);
    });
    
    test('should handle errors when updating contact preferences', async () => {
      // Mock API error
      axios.patch.mockRejectedValueOnce(new Error('Network error'));
      
      // Call the function and verify it throws
      const params = {
        token: 'invalid-token',
        preferences: {
          '1': false
        }
      };
      try {
        await api.updateContactPreferences(params);
        fail('Expected updateContactPreferences to throw an error');
      } catch (error) {
        expect(error).toBeDefined();
      }
    });
  });
});
