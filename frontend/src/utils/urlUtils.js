/**
 * Utility functions for URL processing
 */

import { API_BASE } from '../api';

/**
 * Process a logo URL to ensure it's properly formatted
 * - Converts relative URLs to absolute URLs
 * - Adds cache-busting parameter
 * 
 * @param {string} logoUrl - The logo URL to process
 * @returns {string|null} - The processed URL or null if no URL provided
 */
export function processLogoUrl(logoUrl) {
  if (!logoUrl) return null;
  
  // Process relative URLs
  if (logoUrl.startsWith('/') && !logoUrl.includes('://')) {
    let backendOrigin = API_BASE.replace(/\/api\/v1\/?$/, '');
    logoUrl = backendOrigin + logoUrl;
  }
  
  // Add cache-busting
  const timestamp = new Date().getTime();
  return `${logoUrl}?t=${timestamp}`;
}
