/**
 * ProtectedRoute.jsx
 *
 * Authentication protection wrapper for routes.
 *
 * This component implements route protection based on authentication status,
 * redirecting unauthenticated users to the login page. It's a critical part of
 * the application's security model and role-based access control system.
 *
 * As noted in the memories, the system supports two roles for authenticated users:
 * - Admin: Can create campaigns, products, and manage authenticated users
 * - Support: Can view all pages but cannot create campaigns/products or manage users
 *
 * Non-authenticated users should only be able to see the Opt-Out page, the Login menu,
 * and the light/dark mode icon. This component helps enforce those restrictions.
 *
 * Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
 * This file is part of the OptIn Manager project and is licensed under the MIT License.
 * See the root LICENSE file for details.
 */

import { Navigate } from 'react-router-dom';

/**
 * Protected route component that checks for authentication.
 * 
 * This component wraps routes that require authentication, checking for the
 * presence of an access token in local storage. If no token is found, the user
 * is redirected to the login page. This ensures that protected pages are only
 * accessible to authenticated users.
 * 
 * @param {Object} props - Component props
 * @param {React.ReactNode} props.children - Child components to render if authenticated
 * @returns {JSX.Element} The children if authenticated, or a redirect to login
 */
export default function ProtectedRoute({ children }) {
  const token = localStorage.getItem('access_token');
  if (!token) return <Navigate to="/login" replace />;
  // TODO: Optionally, validate token expiration
  return children;
}
