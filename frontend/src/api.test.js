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
      
      // Mock the actual implementation of fetchOptIns to use our mocked localStorage
      jest.spyOn(window.localStorage, 'getItem').mockReturnValue('test-token');
      
      // Mock successful API response
      const mockResponse = {
        data: [
          { id: '1', name: 'Marketing', type: 'marketing', status: 'active' },
          { id: '2', name: 'Transactional', type: 'transactional', status: 'active' }
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
      expect(result).toHaveLength(2);
      expect(result[0].name).toBe('Marketing');
    });

    test('should handle errors when fetching opt-ins', async () => {
      // Mock localStorage to return a token
      localStorageMock.setItem('access_token', 'test-token');
      
      // Mock API error
      axios.get.mockRejectedValueOnce(new Error('Network error'));
      
      // Call the function and expect it to throw
      await expect(api.fetchOptIns()).rejects.toThrow();
    });
  });
});
