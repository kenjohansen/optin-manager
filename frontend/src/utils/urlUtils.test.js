/**
 * Tests for URL utility functions
 */

import { processLogoUrl } from './urlUtils';
import { API_BASE } from '../api';

// Mock Date to ensure consistent timestamp for testing
const mockDate = new Date('2025-01-01T00:00:00Z');
const originalDate = global.Date;

describe('URL Utilities', () => {
  beforeEach(() => {
    // Mock Date constructor to return fixed date
    global.Date = jest.fn(() => mockDate);
    global.Date.now = originalDate.now;
  });

  afterEach(() => {
    // Restore original Date
    global.Date = originalDate;
  });

  describe('processLogoUrl', () => {
    test('returns null when no URL is provided', () => {
      expect(processLogoUrl(null)).toBeNull();
      expect(processLogoUrl('')).toBeNull();
      expect(processLogoUrl(undefined)).toBeNull();
    });

    test('adds cache-busting timestamp to absolute URLs', () => {
      const testUrl = 'https://example.com/logo.png';
      const timestamp = mockDate.getTime();
      const expected = `${testUrl}?t=${timestamp}`;
      
      expect(processLogoUrl(testUrl)).toBe(expected);
    });

    test('converts relative URLs to absolute URLs with backend origin', () => {
      const relativeUrl = '/static/logo.png';
      const backendOrigin = API_BASE.replace(/\/api\/v1\/?$/, '');
      const timestamp = mockDate.getTime();
      const expected = `${backendOrigin}${relativeUrl}?t=${timestamp}`;
      
      expect(processLogoUrl(relativeUrl)).toBe(expected);
    });

    test('handles URLs that already have path parameters', () => {
      const urlWithParams = 'https://example.com/logo.png?version=1';
      const timestamp = mockDate.getTime();
      const expected = `${urlWithParams}?t=${timestamp}`;
      
      expect(processLogoUrl(urlWithParams)).toBe(expected);
    });

    test('does not convert URLs that have a protocol', () => {
      const urlWithProtocol = 'http://other-domain.com/logo.png';
      const timestamp = mockDate.getTime();
      const expected = `${urlWithProtocol}?t=${timestamp}`;
      
      expect(processLogoUrl(urlWithProtocol)).toBe(expected);
    });
  });
});
