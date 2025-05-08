/**
 * auth.test.js
 *
 * Unit tests for authentication utility functions.
 *
 * This test suite verifies the functionality of the auth utility functions, including
 * JWT parsing, role checking, and authentication validation. These functions are
 * critical for the application's role-based access control system.
 *
 * Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
 * This file is part of the OptIn Manager project and is licensed under the MIT License.
 * See the root LICENSE file for details.
 */

import { parseJwt, getRoleFromToken, isAdmin, isSupport, isAuthenticated } from './auth';

// Mock the global atob function
global.atob = jest.fn(str => Buffer.from(str, 'base64').toString('binary'));

describe('Auth Utilities', () => {
  // Valid token with admin role
  const validAdminToken = 'header.eyJzY29wZSI6ImFkbWluIiwiZXhwIjo5OTk5OTk5OTk5fQ.signature';
  
  // Valid token with support role
  const validSupportToken = 'header.eyJzY29wZSI6InN1cHBvcnQiLCJleHAiOjk5OTk5OTk5OTl9.signature';
  
  // Expired token
  const expiredToken = 'header.eyJzY29wZSI6ImFkbWluIiwiZXhwIjoxNjIwMDAwMDAwfQ.signature';
  
  // Invalid token
  const invalidToken = 'not-a-valid-token';
  
  // No token
  const noToken = null;

  describe('parseJwt', () => {
    test('should parse a valid JWT token', () => {
      const payload = parseJwt(validAdminToken);
      expect(payload).toEqual({
        scope: 'admin',
        exp: 9999999999
      });
    });

    test('should return null for an invalid token', () => {
      const payload = parseJwt(invalidToken);
      expect(payload).toBeNull();
    });

    test('should return null for no token', () => {
      const payload = parseJwt(noToken);
      expect(payload).toBeNull();
    });
  });

  describe('getRoleFromToken', () => {
    test('should extract admin role from token', () => {
      const role = getRoleFromToken(validAdminToken);
      expect(role).toBe('admin');
    });

    test('should extract support role from token', () => {
      const role = getRoleFromToken(validSupportToken);
      expect(role).toBe('support');
    });

    test('should return null for invalid token', () => {
      const role = getRoleFromToken(invalidToken);
      expect(role).toBeNull();
    });

    test('should return null for no token', () => {
      const role = getRoleFromToken(noToken);
      expect(role).toBeNull();
    });
  });

  describe('isAdmin', () => {
    test('should return true for admin token', () => {
      expect(isAdmin(validAdminToken)).toBe(true);
    });

    test('should return false for support token', () => {
      expect(isAdmin(validSupportToken)).toBe(false);
    });

    test('should return false for invalid token', () => {
      expect(isAdmin(invalidToken)).toBe(false);
    });

    test('should return false for no token', () => {
      expect(isAdmin(noToken)).toBe(false);
    });
  });

  describe('isSupport', () => {
    test('should return true for support token', () => {
      expect(isSupport(validSupportToken)).toBe(true);
    });

    test('should return false for admin token', () => {
      expect(isSupport(validAdminToken)).toBe(false);
    });

    test('should return false for invalid token', () => {
      expect(isSupport(invalidToken)).toBe(false);
    });

    test('should return false for no token', () => {
      expect(isSupport(noToken)).toBe(false);
    });
  });

  describe('isAuthenticated', () => {
    beforeEach(() => {
      // Mock Date.now() to return a fixed timestamp for testing
      jest.spyOn(Date, 'now').mockImplementation(() => 1620000001 * 1000); // Just after expiration
    });

    afterEach(() => {
      jest.restoreAllMocks();
    });

    test('should return true for valid admin token', () => {
      expect(isAuthenticated(validAdminToken)).toBe(true);
    });

    test('should return true for valid support token', () => {
      expect(isAuthenticated(validSupportToken)).toBe(true);
    });

    test('should return false for expired token', () => {
      expect(isAuthenticated(expiredToken)).toBe(false);
    });

    test('should return false for invalid token', () => {
      expect(isAuthenticated(invalidToken)).toBe(false);
    });

    test('should return false for no token', () => {
      expect(isAuthenticated(noToken)).toBe(false);
    });
  });
});
