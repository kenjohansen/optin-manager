// Utility functions for role-based auth and visibility

export function parseJwt(token) {
  if (!token) return null;
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    return JSON.parse(atob(base64));
  } catch {
    return null;
  }
}

export function getRoleFromToken(token) {
  const payload = parseJwt(token);
  return payload?.scope || null;
}

export function isAdmin(token) {
  return getRoleFromToken(token) === 'admin';
}

export function isSupport(token) {
  return getRoleFromToken(token) === 'support';
}

export function isAuthenticated(token) {
  const payload = parseJwt(token);
  if (!payload) return false;
  
  // Check if token has expiration claim
  if (payload.exp) {
    // exp is in seconds, Date.now() is in milliseconds
    const currentTime = Math.floor(Date.now() / 1000);
    if (currentTime >= payload.exp) {
      // Token has expired
      return false;
    }
  }
  
  return !!payload.scope; // Check if the token has a valid role
}
