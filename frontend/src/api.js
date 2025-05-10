/**
 * api.js
 *
 * API client for the OptIn Manager backend.
 *
 * This module provides a comprehensive set of functions for communicating with
 * the OptIn Manager backend API. It handles authentication, error handling, and
 * data formatting for all API endpoints required by the frontend application.
 *
 * As noted in the memories, the module supports the Phase 1 Opt-Out workflow,
 * including sending verification codes, verifying codes, and managing user
 * preferences. It ensures compatibility with the backend running on SQLite
 * for development and testing environments.
 *
 * Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
 * This file is part of the OptIn Manager project and is licensed under the MIT License.
 * See the root LICENSE file for details.
 */

import axios from 'axios';

/**
 * Base URL for the API endpoints.
 * 
 * This constant defines the root URL for all API requests. For development,
 * it points to the local development server. In production, this would be
 * updated to point to the deployed API server.
 */
export const API_BASE = 'http://127.0.0.1:8000/api/v1';

/**
 * Fetches customization settings from the backend.
 * 
 * This function retrieves the organization's branding and customization settings,
 * including logo, colors, and provider configurations. It's essential for implementing
 * the UI branding elements and communication provider settings as noted in the memories.
 * 
 * The function handles authentication by including the JWT token if available and
 * processes the logo URL to ensure it's properly formatted for display. It also
 * implements graceful error handling to prevent UI disruptions if the backend
 * is unavailable.
 * 
 * @returns {Promise<Object>} The customization settings object or an empty object if an error occurs
 */
export const fetchCustomization = async () => {
  const token = localStorage.getItem('access_token');
  const headers = token ? { Authorization: `Bearer ${token}` } : {};
  
  try {
    const res = await axios.get(`${API_BASE}/customization/`, { headers });
    console.log('Fetched customization:', res.data);
    
    // Process the logo URL to ensure it's properly formatted
    if (res.data && res.data.logo_url) {
      let logoUrl = res.data.logo_url;
      // Check if the URL is a relative path (starts with /) and doesn't already contain the backend origin
      if (logoUrl && logoUrl.startsWith('/') && !logoUrl.includes('://')) {
        let backendOrigin = API_BASE.replace(/\/api\/v1\/?$/, '');
        res.data.logo_url = backendOrigin + logoUrl;
      }
    }
    
    return res.data;
  } catch (error) {
    console.error('Error fetching customization:', error.response?.data || error.message);
    // Return empty object instead of throwing to prevent UI errors
    return {};
  }
};

/**
 * Saves customization settings to the backend.
 * 
 * This function updates the organization's branding and customization settings,
 * including logo, colors, company name, and communication provider configurations.
 * It's a critical part of the customization capabilities that allow organizations
 * to personalize the OptIn Manager interface to match their brand identity.
 * 
 * The function handles file uploads for the logo and form data formatting for
 * all other settings. It requires admin authentication to ensure only authorized
 * users can modify organization-wide settings.
 * 
 * @param {Object} options - Customization options
 * @param {File} options.logo - Organization logo file
 * @param {string} options.primary - Primary brand color in hex format
 * @param {string} options.secondary - Secondary brand color in hex format
 * @param {string} options.company_name - Organization name
 * @param {string} options.privacy_policy_url - URL to privacy policy
 * @param {string} options.email_provider - Email service provider name
 * @param {string} options.sms_provider - SMS service provider name
 * @returns {Promise<Object>} The updated customization settings
 */
export const saveCustomization = async ({ logo, primary, secondary, company_name, privacy_policy_url, email_provider, sms_provider }) => {
  const formData = new FormData();
  if (logo) formData.append('logo', logo);
  if (primary) formData.append('primary', primary);
  if (secondary) formData.append('secondary', secondary);
  if (company_name) formData.append('company_name', company_name);
  if (privacy_policy_url) formData.append('privacy_policy_url', privacy_policy_url);
  if (email_provider) formData.append('email_provider', email_provider);
  if (sms_provider) formData.append('sms_provider', sms_provider);
  
  const token = localStorage.getItem('access_token');
  
  // Enhanced debugging
  console.log('Saving customization with logo:', logo ? logo.name : 'none');
  console.log('Authentication token present:', token ? 'Yes' : 'No');
  
  if (!token) {
    console.error('No authentication token found. User must be logged in to save customization.');
    throw new Error('Authentication required. Please log in and try again.');
  }
  
  try {
    // Ensure we're using the correct URL with trailing slash to match backend expectations
    const res = await axios.post(`${API_BASE}/customization/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        Authorization: `Bearer ${token}`,
      },
    });
    console.log('Customization saved successfully:', res.data);
    return res.data;
  } catch (error) {
    console.error('Error saving customization:', error.response?.data || error.message);
    console.error('Status code:', error.response?.status);
    throw error;
  }
};

/**
 * Authenticates a user and retrieves a JWT token.
 * 
 * This function handles user authentication for admin and support users,
 * implementing the role-based access control requirements noted in the memories.
 * It exchanges username and password credentials for a JWT token that includes
 * the user's role (scope), which is then used to control access to different
 * parts of the application.
 * 
 * @param {Object} credentials - User credentials
 * @param {string} credentials.username - Username
 * @param {string} credentials.password - Password
 * @returns {Promise<Object>} Authentication result with token and user info
 */
export const login = async ({ username, password }) => {
  // Use /auth/login and form-encoded data
  const res = await axios.post(
    `${API_BASE}/auth/login`,
    new URLSearchParams({ username, password }),
    { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
  );
  return res.data;
};

/**
 * Fetches dashboard statistics from the backend.
 * 
 * This function retrieves aggregated metrics and statistics for the dashboard,
 * including user counts, opt-in program statistics, message delivery metrics,
 * and consent status distributions. These metrics are essential for monitoring
 * system usage and generating compliance reports.
 * 
 * @param {number} days - Number of days to look back for time-based metrics (default: 30)
 * @returns {Promise<Object>} Dashboard statistics and metrics
 */
export const fetchDashboardStats = async (days = 30) => {
  const token = localStorage.getItem('access_token');
  const headers = token ? { Authorization: `Bearer ${token}` } : {};
  const res = await axios.get(`${API_BASE}/dashboard/stats?days=${days}`, { headers });
  return res.data;
};

export const optOutContact = async ({ contact }) => {
  return axios.post(`${API_BASE}/contacts/optout`, { contact });
};

export const fetchContacts = async ({ search, consent, timeWindow }) => {
  const token = localStorage.getItem('access_token');
  
  // Enhanced debugging
  console.log('Fetching contacts with params:', { search, consent, timeWindow });
  console.log('Authentication token present:', token ? 'Yes' : 'No');
  
  if (!token) {
    console.error('No authentication token found. User must be logged in to fetch contacts.');
    throw new Error('Authentication required. Please log in and try again.');
  }
  
  const params = {};
  if (search) params.search = search;
  if (consent) params.consent = consent;
  if (timeWindow) params.time_window = timeWindow;
  
  try {
    const res = await axios.get(`${API_BASE}/contacts/`, { 
      params,
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    console.log('Contacts fetched successfully:', res.data);
    return res.data;
  } catch (error) {
    console.error('Error fetching contacts:', error.response?.data || error.message);
    console.error('Status code:', error.response?.status);
    throw error;
  }
};

export const optOutById = async (id) => {
  const res = await axios.post(`${API_BASE}/contacts/${id}/optout`);
  return res.data;
};

/**
 * Opt-out verification and preferences APIs
 * 
 * The following functions implement the core functionality for the Opt-Out workflow,
 * which is the primary focus of Phase 1 as noted in the memories. They handle the
 * complete flow for users to manage their communication preferences.
 */

/**
 * Sends a verification code to a contact's email or phone.
 * 
 * This function initiates the opt-out process by sending a verification code
 * to the user's contact method (email or phone). This is the first step in the
 * secure verification process that ensures only the actual owner of the contact
 * information can manage their preferences.
 * 
 * @param {Object} params - Parameters for sending the verification code
 * @param {string} params.contact - Email or phone to send the code to
 * @param {string} params.contactType - Type of contact ('email' or 'phone')
 * @returns {Promise<Object>} Result of the send operation
 */
export const sendVerificationCode = async (params) => {
  // Handle both object format and direct string format
  let contactValue, purposeValue, authUserName, contactType;
  
  // Check if params is an object with contact property or a direct string
  if (typeof params === 'object' && params !== null) {
    contactValue = params.contact;
    purposeValue = params.purpose || 'self_service';
    authUserName = params.auth_user_name;
    // Determine contact type based on format
    contactType = contactValue && contactValue.includes('@') ? 'email' : 'phone';
  } else {
    // For backward compatibility
    contactValue = params;
    purposeValue = 'preferences';
    authUserName = null;
    // Determine contact type based on format
    contactType = contactValue && contactValue.includes('@') ? 'email' : 'phone';
  }
  
  // Get the frontend URL for the preferences page
  const frontendUrl = window.location.origin;
  const preferencesUrl = `${frontendUrl}/preferences?contact=${encodeURIComponent(contactValue)}`;
  
  console.log('Sending verification code with params:', { contactValue, contactType, purposeValue, authUserName });
  
  // POST /api/v1/preferences/send-code with all necessary information
  const res = await axios.post(`${API_BASE}/preferences/send-code`, { 
    contact: contactValue,
    contact_type: contactType,
    purpose: purposeValue,
    auth_user_name: authUserName,
    preferences_url: preferencesUrl
  });
  return res.data;
};

/**
 * Verifies a code submitted by a user.
 * 
 * This function validates the verification code entered by the user against
 * the code stored in the database. If valid, it returns a JWT token that allows
 * the user to access and update their preferences. This is a critical security
 * step to ensure only verified users can manage their communication preferences.
 * 
 * @param {Object} params - Verification parameters
 * @param {string} params.contact - Email or phone the code was sent to
 * @param {string} params.code - Verification code entered by the user
 * @returns {Promise<Object>} Verification result with token if successful
 */
export const verifyCode = async ({ contact, code }) => {
  // Determine contact type based on format
  const contactType = contact && contact.includes('@') ? 'email' : 'phone';
  
  // POST /api/v1/preferences/verify-code { contact, contact_type, code }
  const res = await axios.post(`${API_BASE}/preferences/verify-code`, { 
    contact, 
    contact_type: contactType,
    code 
  });
  return res.data;
};

/**
 * Fetches a contact's current communication preferences.
 * 
 * This function retrieves the current opt-in/opt-out status for all available
 * communication programs for a specific contact. It supports both token-based
 * authentication (for users who have verified their identity) and direct contact
 * parameter access (for email links).
 * 
 * @param {Object} params - Request parameters
 * @param {string} params.token - JWT token from verification (optional)
 * @param {string} params.contact - Email or phone to fetch preferences for (optional)
 * @returns {Promise<Object>} Contact preferences data
 */
export const fetchContactPreferences = async ({ token, contact }) => {
  console.log('Fetching preferences with:', token ? 'token' : 'contact', contact || '');
  
  try {
    // Prepare params object
    const params = {};
    
    // If we have a token, add it to the params
    if (token) {
      params.token = token;
    }
    // Otherwise, use the contact parameter
    else if (contact) {
      params.contact = contact;
    }
    // If neither token nor contact is provided, throw an error
    else {
      throw new Error('Either token or contact must be provided');
    }
    
    // Make the request with the appropriate params
    const res = await axios.get(`${API_BASE}/preferences/user-preferences`, { params });
    console.log('Preferences response:', res.data);
    return res.data;
  } catch (error) {
    console.error('Error fetching preferences:', error.response?.data || error.message);
    throw error;
  }
};

/**
 * Updates a contact's communication preferences.
 * 
 * This function updates the opt-in/opt-out status for communication programs
 * based on user selections. It's the final step in the Opt-Out workflow that
 * allows users to control which types of communications they receive. The function
 * supports both granular preferences for specific programs and a global opt-out
 * option for all communications.
 * 
 * @param {Object} params - Update parameters
 * @param {string} params.token - JWT token from verification (optional)
 * @param {string} params.contact - Email or phone to update preferences for (optional)
 * @param {Object} params.preferences - Map of program IDs to preference values
 * @param {string} params.comment - Optional comment about the preference change
 * @param {boolean} params.global_opt_out - Whether to opt out of all communications
 * @returns {Promise<Object>} Updated preferences data
 */
export const updateContactPreferences = async ({ token, contact, preferences = {}, comment, global_opt_out }) => {
  // Prepare the payload with all required fields
  const payload = {
    token,
    preferences
  };
  
  // Add contact to payload if provided and no token
  if (contact && !token) payload.contact = contact;
  
  // Add optional fields if provided
  if (comment !== undefined) payload.comment = comment;
  if (global_opt_out !== undefined) payload.global_opt_out = global_opt_out;
  
  // Send request with the properly structured payload
  const res = await axios.patch(`${API_BASE}/preferences/user-preferences`, payload);
  return res.data;
};

/**
 * OptIn API
 * 
 * The following functions manage opt-in programs (formerly Campaign/Product)
 * which are central to the consent management system as noted in the memories.
 */

/**
 * Creates a new opt-in program.
 * 
 * This function allows administrators to define new opt-in programs that users
 * can subscribe to. Creating distinct opt-in programs enables organizations to
 * manage different types of communications separately and comply with regulatory
 * requirements for specific consent management.
 * 
 * @param {Object} program - Program details
 * @param {string} program.name - Name of the opt-in program
 * @param {string} program.type - Type of program (e.g., 'marketing', 'transactional')
 * @returns {Promise<Object>} Created opt-in program data
 */
export const createOptIn = async ({ name, type }) => {
  const token = localStorage.getItem('access_token');
  const res = await axios.post(
    `${API_BASE}/optins`,
    { name, type },
    { headers: { Authorization: `Bearer ${token}` } }
  );
  return res.data;
};

/**
 * Fetches all opt-in programs.
 * 
 * This function retrieves the complete list of opt-in programs defined in the
 * system. It's used to populate program selection interfaces and to provide
 * administrators with a view of all available communication channels.
 * 
 * @returns {Promise<Array>} List of opt-in programs
 */
export const fetchOptIns = async () => {
  const token = localStorage.getItem('access_token');
  const res = await axios.get(`${API_BASE}/optins`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return res.data;
};

/**
 * Updates an existing opt-in program.
 * 
 * This function allows administrators to modify opt-in program configurations
 * as business needs evolve. The ability to update existing programs rather than
 * creating new ones maintains historical continuity and preserves existing user
 * consents.
 * 
 * @param {Object} program - Program update details
 * @param {string} program.id - ID of the program to update
 * @param {string} program.name - Updated name for the program
 * @param {string} program.status - Updated status ('active', 'paused', 'archived')
 * @returns {Promise<Object>} Updated opt-in program data
 */
export const updateOptIn = async ({ id, name, status }) => {
  const token = localStorage.getItem('access_token');
  const payload = {};
  if (name !== undefined) payload.name = name;
  if (status !== undefined) payload.status = status;
  const res = await axios.put(
    `${API_BASE}/optins/${id}`,
    payload,
    { headers: { Authorization: `Bearer ${token}` } }
  );
  return res.data;
};
