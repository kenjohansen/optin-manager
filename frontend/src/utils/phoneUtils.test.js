/**
 * phoneUtils.test.js
 *
 * Unit tests for phone number utility functions.
 *
 * This test suite verifies the functionality of the phone utility functions, including
 * E.164 formatting and phone number validation. These functions are used throughout
 * the application for consistent handling of phone numbers.
 *
 * Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
 * This file is part of the OptIn Manager project and is licensed under the MIT License.
 * See the root LICENSE file for details.
 */

import { formatPhoneToE164, isValidPhoneNumber } from './phoneUtils';

describe('Phone Utilities', () => {
  describe('formatPhoneToE164', () => {
    test('should format a 10-digit US number correctly', () => {
      expect(formatPhoneToE164('5551234567')).toBe('+15551234567');
      expect(formatPhoneToE164('555-123-4567')).toBe('+15551234567');
      expect(formatPhoneToE164('(555) 123-4567')).toBe('+15551234567');
    });

    test('should handle numbers with country code', () => {
      expect(formatPhoneToE164('+15551234567')).toBe('+15551234567');
      expect(formatPhoneToE164('+44 20 7946 0958')).toBe('+442079460958');
    });

    test('should handle numbers with country code but no plus sign', () => {
      expect(formatPhoneToE164('15551234567')).toBe('+15551234567');
      expect(formatPhoneToE164('442079460958')).toBe('+442079460958');
    });

    test('should add US country code to partial numbers', () => {
      expect(formatPhoneToE164('123456')).toBe('+1123456');
      expect(formatPhoneToE164('555-1234')).toBe('+15551234');
    });

    test('should handle empty or null input', () => {
      expect(formatPhoneToE164('')).toBe('');
      expect(formatPhoneToE164(null)).toBe('');
      expect(formatPhoneToE164(undefined)).toBe('');
    });

    test('should strip non-digit characters', () => {
      expect(formatPhoneToE164('(555) 123-4567 ext. 890')).toBe('+5551234567890');
      expect(formatPhoneToE164('555.123.4567')).toBe('+15551234567');
    });
  });

  describe('isValidPhoneNumber', () => {
    test('should validate proper phone numbers', () => {
      expect(isValidPhoneNumber('+15551234567')).toBe(true);
      expect(isValidPhoneNumber('555-123-4567')).toBe(true);
      expect(isValidPhoneNumber('(555) 123-4567')).toBe(true);
      expect(isValidPhoneNumber('5551234567')).toBe(true);
    });

    test('should validate international numbers', () => {
      expect(isValidPhoneNumber('+442079460958')).toBe(true);
      expect(isValidPhoneNumber('+61 2 9876 5432')).toBe(true);
    });

    test('should reject numbers that are too short', () => {
      expect(isValidPhoneNumber('123')).toBe(false);
      expect(isValidPhoneNumber('1234567')).toBe(false);
    });

    test('should handle empty or null input', () => {
      expect(isValidPhoneNumber('')).toBe(false);
      expect(isValidPhoneNumber(null)).toBe(false);
      expect(isValidPhoneNumber(undefined)).toBe(false);
    });

    test('should validate numbers with non-digit characters', () => {
      expect(isValidPhoneNumber('(555) 123-4567')).toBe(true);
      expect(isValidPhoneNumber('555.123.4567')).toBe(true);
      expect(isValidPhoneNumber('555 123 4567')).toBe(true);
    });
  });
});
