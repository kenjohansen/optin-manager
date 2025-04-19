import { createTheme } from '@mui/material/styles';

export const getTheme = (mode, primary, secondary) =>
  createTheme({
    palette: {
      mode,
      primary: { main: primary || '#1976d2' },
      secondary: { main: secondary || '#9c27b0' },
    },
  });
