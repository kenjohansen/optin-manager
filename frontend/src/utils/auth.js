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
  return !!getRoleFromToken(token);
}
