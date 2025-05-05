import axios from 'axios';

export const API_BASE = 'http://127.0.0.1:8000/api/v1';

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

export const login = async ({ username, password }) => {
  // Use /auth/login and form-encoded data
  const res = await axios.post(
    `${API_BASE}/auth/login`,
    new URLSearchParams({ username, password }),
    { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
  );
  return res.data;
};

export const fetchDashboardStats = async () => {
  const res = await axios.get(`${API_BASE}/dashboard/stats`);
  return res.data;
};

export const optOutContact = async ({ contact }) => {
  return axios.post(`${API_BASE}/contacts/optout`, { contact });
};

export const fetchContacts = async ({ search, consent, timeWindow }) => {
  const params = {};
  if (search) params.search = search;
  if (consent) params.consent = consent;
  if (timeWindow) params.time_window = timeWindow;
  const res = await axios.get(`${API_BASE}/contacts`, { params });
  return res.data;
};

export const optOutById = async (id) => {
  const res = await axios.post(`${API_BASE}/contacts/${id}/optout`);
  return res.data;
};

// Opt-out verification and preferences APIs
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

export const fetchContactPreferences = async ({ token, contact }) => {
  console.log('Fetching preferences with:', token ? 'token' : 'contact', contact || '');
  
  try {
    // If we have a token, use it in the Authorization header
    if (token) {
      const res = await axios.get(`${API_BASE}/preferences/user-preferences`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      console.log('Preferences response (token):', res.data);
      return res.data;
    }
    
    // Otherwise, use the contact parameter in the query string
    else if (contact) {
      const res = await axios.get(`${API_BASE}/preferences/user-preferences`, {
        params: { contact }
      });
      console.log('Preferences response (contact):', res.data);
      return res.data;
    }
    
    // If neither token nor contact is provided, throw an error
    else {
      throw new Error('Either token or contact must be provided');
    }
  } catch (error) {
    console.error('Error fetching preferences:', error.response?.data || error.message);
    throw error;
  }
};

export const updateContactPreferences = async ({ token, contact, preferences = {}, comment, global_opt_out }) => {
  // Prepare the payload with preferences and optional fields
  const payload = {
    ...preferences
  };
  if (comment !== undefined) payload.comment = comment;
  if (global_opt_out !== undefined) payload.global_opt_out = global_opt_out;
  
  // Configuration for the request
  const config = {};
  
  // If we have a token, use it in the Authorization header
  if (token) {
    config.headers = {
      Authorization: `Bearer ${token}`
    };
  }
  
  // If we have a contact but no token, add it as a query parameter
  const params = {};
  if (contact && !token) {
    params.contact = contact;
  }
  
  // Add params to config if needed
  if (Object.keys(params).length > 0) {
    config.params = params;
  }
  
  // Send request with the appropriate authentication
  const res = await axios.patch(`${API_BASE}/preferences/user-preferences`, payload, config);
  return res.data;
};

// OptIn API
export const createOptIn = async ({ name, type }) => {
  const token = localStorage.getItem('access_token');
  const res = await axios.post(
    `${API_BASE}/optins`,
    { name, type },
    { headers: { Authorization: `Bearer ${token}` } }
  );
  return res.data;
};

export const fetchOptIns = async () => {
  const token = localStorage.getItem('access_token');
  const res = await axios.get(`${API_BASE}/optins`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return res.data;
};

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
