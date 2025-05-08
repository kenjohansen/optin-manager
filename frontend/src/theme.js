/**
 * theme.js
 *
 * Theme configuration for the OptIn Manager frontend.
 *
 * This module provides theme generation functionality for the application,
 * supporting both light and dark modes as well as customizable primary and
 * secondary colors. The theming capability is essential for implementing the
 * customization requirements, allowing organizations to match the application's
 * appearance to their brand identity.
 *
 * Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
 * This file is part of the OptIn Manager project and is licensed under the MIT License.
 * See the root LICENSE file for details.
 */

import { createTheme } from '@mui/material/styles';

/**
 * Creates a Material-UI theme based on the specified mode and colors.
 * 
 * This function generates a customized theme for the application, supporting
 * both system preferences (light/dark) and organization branding through custom
 * primary and secondary colors. The theme customization is a key part of the
 * application's ability to adapt to different organization's brand guidelines.
 *
 * @param {string} mode - The theme mode ('light', 'dark', or 'system')
 * @param {string} primary - The primary color in hex format (e.g., '#1976d2')
 * @param {string} secondary - The secondary color in hex format (e.g., '#9c27b0')
 * @returns {Object} A Material-UI theme object with the specified configuration
 */
export const getTheme = (mode, primary, secondary) =>
  createTheme({
    palette: {
      mode,
      primary: { main: primary || '#1976d2' },
      secondary: { main: secondary || '#9c27b0' },
    },
  });
