import axios from 'axios';

export const API_BASE = 'http://localhost:8000/api/v1';

export const fetchCustomization = async () => {
  const res = await axios.get(`${API_BASE}/customization/`);
  return res.data;
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
  const res = await axios.post(`${API_BASE}/customization`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });
  return res.data;
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

export const createCampaign = async ({ name, type }) => {
  const token = localStorage.getItem('access_token');
  const res = await axios.post(
    `${API_BASE}/campaigns`,
    { name, type },
    { headers: { Authorization: `Bearer ${token}` } }
  );
  return res.data;
};

export const fetchCampaigns = async () => {
  const token = localStorage.getItem('access_token');
  const res = await axios.get(`${API_BASE}/campaigns`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return res.data;
};

export const createProduct = async ({ name, description }) => {
  const token = localStorage.getItem('access_token');
  const res = await axios.post(
    `${API_BASE}/products`,
    { name, description },
    { headers: { Authorization: `Bearer ${token}` } }
  );
  return res.data;
};


export const optOutById = async (id) => {
  const res = await axios.post(`${API_BASE}/contacts/${id}/optout`);
  return res.data;
};

// Opt-out verification and preferences APIs
export const sendVerificationCode = async ({ contact }) => {
  // POST /api/v1/contacts/send-code { contact }
  const res = await axios.post(`${API_BASE}/contacts/send-code`, { contact });
  return res.data;
};

export const verifyCode = async ({ contact, code }) => {
  // POST /api/v1/contacts/verify-code { contact, code }
  const res = await axios.post(`${API_BASE}/contacts/verify-code`, { contact, code });
  return res.data;
};

export const fetchContactPreferences = async ({ contact }) => {
  // GET /api/v1/contacts/preferences?contact=...
  const res = await axios.get(`${API_BASE}/contacts/preferences`, { params: { contact } });
  return res.data;
};

export const updateContactPreferences = async ({ contact, preferences = {}, comment, global_opt_out }) => {
  // This endpoint expects a JWT token, but for simplicity in DEV, we pass contact as a param
  // and forward comment/global_opt_out if present
  const payload = {
    ...preferences,
    contact,
  };
  if (comment !== undefined) payload.comment = comment;
  if (global_opt_out !== undefined) payload.global_opt_out = global_opt_out;
  const res = await axios.patch(`${API_BASE}/contacts/preferences`, payload);
  return res.data;
};

export const updateCampaign = async ({ id, name, status }) => {
  const token = localStorage.getItem('access_token');
  const payload = {};
  if (name !== undefined) payload.name = name;
  if (status !== undefined) payload.status = status;
  const res = await axios.put(
    `${API_BASE}/campaigns/${id}`,
    payload,
    { headers: { Authorization: `Bearer ${token}` } }
  );
  return res.data;
};

// Add more API calls as needed for contacts, campaigns, products, etc.
