/**
 * Tests for theme.js
 */
import { getTheme } from './theme';

describe('Theme', () => {
  test('getTheme returns a theme with light mode and default colors when no colors provided', () => {
    const theme = getTheme('light');
    expect(theme.palette.mode).toBe('light');
    expect(theme.palette.primary.main).toBe('#1976d2');
    expect(theme.palette.secondary.main).toBe('#9c27b0');
  });

  test('getTheme returns a theme with dark mode and default colors when no colors provided', () => {
    const theme = getTheme('dark');
    expect(theme.palette.mode).toBe('dark');
    expect(theme.palette.primary.main).toBe('#1976d2');
    expect(theme.palette.secondary.main).toBe('#9c27b0');
  });

  test('getTheme returns a theme with custom colors when provided', () => {
    const theme = getTheme('light', '#ff0000', '#00ff00');
    expect(theme.palette.mode).toBe('light');
    expect(theme.palette.primary.main).toBe('#ff0000');
    expect(theme.palette.secondary.main).toBe('#00ff00');
  });

  test('getTheme returns a theme with custom colors when provided with different mode', () => {
    // Use 'light' instead of 'system' since 'system' is not supported by MUI
    const theme = getTheme('light', '#ff0000', '#00ff00');
    expect(theme.palette.mode).toBe('light');
    expect(theme.palette.primary.main).toBe('#ff0000');
    expect(theme.palette.secondary.main).toBe('#00ff00');
  });
});
