/**
 * Dashboard.test.jsx
 *
 * Unit tests for the Dashboard component.
 *
 * These tests verify that the admin dashboard renders correctly,
 * displays loading states, handles errors, and properly renders
 * statistics and charts based on the data received from the API.
 *
 * Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
 * This file is part of the OptIn Manager project and is licensed under the MIT License.
 * See the root LICENSE file for details.
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import Dashboard from './Dashboard';
import * as api from '../api';

// Mock the API module
jest.mock('../api', () => ({
  fetchDashboardStats: jest.fn(),
  API_BASE: 'http://127.0.0.1:8000/api/v1'
}));

// Mock the Recharts library to avoid rendering issues in tests
jest.mock('recharts', () => {
  const OriginalModule = jest.requireActual('recharts');
  return {
    ...OriginalModule,
    ResponsiveContainer: ({ children }) => <div data-testid="responsive-container">{children}</div>,
    PieChart: ({ children }) => <div data-testid="pie-chart">{children}</div>,
    BarChart: ({ children }) => <div data-testid="bar-chart">{children}</div>,
    LineChart: ({ children }) => <div data-testid="line-chart">{children}</div>,
    Pie: () => <div data-testid="pie" />,
    Bar: () => <div data-testid="bar" />,
    Line: () => <div data-testid="line" />,
    XAxis: () => <div data-testid="x-axis" />,
    YAxis: () => <div data-testid="y-axis" />,
    CartesianGrid: () => <div data-testid="cartesian-grid" />,
    Tooltip: () => <div data-testid="recharts-tooltip" />,
    Legend: () => <div data-testid="legend" />,
    Cell: () => <div data-testid="cell" />
  };
});

// Mock sample dashboard data
const mockDashboardData = {
  total_contacts: 1250,
  new_contacts: 75,
  contact_growth_rate: 6.4,
  optins: {
    total: 980,
    new: 45,
    active: 950,
    paused: 20,
    archived: 10
  },
  consent: {
    opt_in_rate: 78.4,
    opt_out_rate: 21.6
  },
  messages: {
    total: 5680,
    recent: 320,
    status: {
      delivered: 5200,
      failed: 180,
      pending: 300
    },
    types: {
      promotional: 3800,
      transactional: 1880
    },
    channels: {
      sms: {
        count: 2500,
        delivery_rate: 92.5
      },
      email: {
        count: 3180,
        delivery_rate: 96.8
      }
    },
    volume_trend: [
      { date: '2025-04-01', count: 180 },
      { date: '2025-04-02', count: 220 },
      { date: '2025-04-03', count: 250 },
      { date: '2025-04-04', count: 190 },
      { date: '2025-04-05', count: 110 },
      { date: '2025-04-06', count: 90 },
      { date: '2025-04-07', count: 210 }
    ]
  },
  channel_distribution: {
    sms: 450,
    email: 800
  },
  system: {
    uptime: 99.98,
    response_time: 120,
    error_rate: 0.02
  }
};

// Mock localStorage
const localStorageMock = (() => {
  let store = {};
  return {
    getItem: jest.fn(key => store[key] || null),
    setItem: jest.fn((key, value) => {
      store[key] = value.toString();
    }),
    clear: jest.fn(() => {
      store = {};
    }),
    removeItem: jest.fn(key => {
      delete store[key];
    }),
  };
})();
Object.defineProperty(window, 'localStorage', { value: localStorageMock });

describe('Dashboard Component', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
    localStorageMock.clear();
    localStorageMock.setItem('access_token', 'test-token');
  });

  test('renders loading state initially', () => {
    // Mock the API to not resolve immediately
    api.fetchDashboardStats.mockImplementation(() => new Promise(resolve => {
      setTimeout(() => {
        resolve(mockDashboardData);
      }, 100);
    }));

    render(
      <MemoryRouter>
        <Dashboard />
      </MemoryRouter>
    );

    // Check if loading indicator is shown
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  test('renders error state when API fails', async () => {
    // Mock API failure
    api.fetchDashboardStats.mockRejectedValue(new Error('Failed to load data'));

    render(
      <MemoryRouter>
        <Dashboard />
      </MemoryRouter>
    );

    // Wait for the error message to appear
    await waitFor(() => {
      expect(screen.getByText('Failed to load dashboard stats.')).toBeInTheDocument();
    });
  });

  test('renders dashboard with data when API succeeds', async () => {
    // Mock successful API response
    api.fetchDashboardStats.mockResolvedValue(mockDashboardData);

    render(
      <MemoryRouter>
        <Dashboard />
      </MemoryRouter>
    );

    // Wait for the dashboard to load
    await waitFor(() => {
      // Check if the dashboard title is rendered
      expect(screen.getByText('Admin Dashboard')).toBeInTheDocument();
      
      // Check if key metrics are displayed
      expect(screen.getByText('Total Contacts')).toBeInTheDocument();
      expect(screen.getByText('1,250')).toBeInTheDocument();
      expect(screen.getByText('Active Opt-Ins')).toBeInTheDocument();
      expect(screen.getByText('980')).toBeInTheDocument();
      expect(screen.getByText('Opt-In Rate')).toBeInTheDocument();
      expect(screen.getByText('78.4%')).toBeInTheDocument();
      expect(screen.getByText('Total Messages')).toBeInTheDocument();
      expect(screen.getByText('5,680')).toBeInTheDocument();
      
      // Check if charts are rendered
      expect(screen.getAllByTestId('responsive-container').length).toBeGreaterThan(0);
    });
  });

  test('handles time range selection', async () => {
    // Mock successful API response
    api.fetchDashboardStats.mockResolvedValue(mockDashboardData);

    render(
      <MemoryRouter>
        <Dashboard />
      </MemoryRouter>
    );

    // Wait for the dashboard to load
    await waitFor(() => {
      expect(screen.getByText('Admin Dashboard')).toBeInTheDocument();
    });

    // Change the time range
    fireEvent.mouseDown(screen.getByLabelText('Time Range'));
    fireEvent.click(screen.getByText('Last 7 days'));

    // Verify that fetchDashboardStats was called with the new time range
    expect(api.fetchDashboardStats).toHaveBeenCalledWith(7);
  });

  test('handles tab switching', async () => {
    // Mock successful API response
    api.fetchDashboardStats.mockResolvedValue(mockDashboardData);

    render(
      <MemoryRouter>
        <Dashboard />
      </MemoryRouter>
    );

    // Wait for the dashboard to load
    await waitFor(() => {
      expect(screen.getByText('Admin Dashboard')).toBeInTheDocument();
    });

    // Verify the tabs are present
    expect(screen.getByRole('tab', { name: 'Overview' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: 'Contacts & Opt-ins' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: 'Messages' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: 'System' })).toBeInTheDocument();

    // Switch to the Messages tab
    fireEvent.click(screen.getByRole('tab', { name: 'Messages' }));

    // Verify that the Messages tab is selected
    await waitFor(() => {
      const messagesTab = screen.getByRole('tab', { name: 'Messages' });
      expect(messagesTab).toHaveAttribute('aria-selected', 'true');
    });

    // Switch to the System tab
    fireEvent.click(screen.getByRole('tab', { name: 'System' }));

    // Verify that the System tab is selected
    await waitFor(() => {
      const systemTab = screen.getByRole('tab', { name: 'System' });
      expect(systemTab).toHaveAttribute('aria-selected', 'true');
    });

    // Switch to the Contacts & Opt-ins tab
    fireEvent.click(screen.getByRole('tab', { name: 'Contacts & Opt-ins' }));

    // Verify that the Contacts & Opt-ins tab is selected
    await waitFor(() => {
      const contactsTab = screen.getByRole('tab', { name: 'Contacts & Opt-ins' });
      expect(contactsTab).toHaveAttribute('aria-selected', 'true');
    });

    // Switch back to the Overview tab
    fireEvent.click(screen.getByRole('tab', { name: 'Overview' }));

    // Verify that the Overview tab is selected
    await waitFor(() => {
      const overviewTab = screen.getByRole('tab', { name: 'Overview' });
      expect(overviewTab).toHaveAttribute('aria-selected', 'true');
    });
  });
});
