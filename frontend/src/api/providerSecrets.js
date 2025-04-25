import axios from 'axios';

const API_BASE = 'http://localhost:8000/api/v1/provider-secrets';

export const setProviderSecret = async ({ providerType, accessKey, secretKey, region, fromAddress }) => {
  const token = localStorage.getItem('access_token');
  return axios.post(`${API_BASE}/set`, {
    provider_type: providerType,
    access_key: accessKey,
    secret_key: secretKey,
    region,
    from_address: fromAddress,
  }, {
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });
};

export const getSecretsStatus = async () => {
  const token = localStorage.getItem('access_token');
  const res = await axios.get(`${API_BASE}/status`, {
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });
  return res.data;
};

export const testProviderConnection = async ({ providerType }) => {
  const token = localStorage.getItem('access_token');
  const res = await axios.post(`${API_BASE}/test`, { provider_type: providerType }, {
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });
  return res.data;
};

export const deleteProviderSecret = async ({ providerType }) => {
  const token = localStorage.getItem('access_token');
  const res = await axios.post(`${API_BASE}/delete`, { provider_type: providerType }, {
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });
  return res.data;
};
