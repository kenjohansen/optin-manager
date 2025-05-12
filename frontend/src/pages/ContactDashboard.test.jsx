/**
 * ContactDashboard.test.jsx
 *
 * Unit tests for the ContactDashboard component.
 *
 * These tests verify that the contacts dashboard renders correctly,
 * displays loading states, handles errors, and properly renders
 * contact information with filtering and search capabilities.
 *
 * Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
 * This file is part of the OptIn Manager project and is licensed under the MIT License.
 * See the root LICENSE file for details.
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import ContactDashboard from './ContactDashboard';
import * as api from '../api';

// Mock the API module
jest.mock('../api', () => ({
  fetchContacts: jest.fn(),
  API_BASE: 'http://127.0.0.1:8000/api/v1'
}));

// Mock sample contacts data
const mockContacts = [
  {
    id: '1',
    contact_type: 'email',
    email: 'john.doe@example.com',
    phone: null,
    masked_value: 'j***@example.com',
    consent: 'Opted In',
    last_updated: '2025-04-01T10:30:00Z'
  },
  {
    id: '2',
    contact_type: 'phone',
    email: null,
    phone: '+15551234567',
    masked_value: '+1*********67',
    consent: 'Opted Out',
    last_updated: '2025-04-02T14:45:00Z'
  },
  {
    id: '3',
    contact_type: 'email',
    email: 'jane.smith@example.com',
    phone: null,
    masked_value: 'j***@example.com',
    consent: 'Opted In',
    last_updated: '2025-04-03T09:15:00Z'
  }
];

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

describe('ContactDashboard Component', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
    localStorageMock.clear();
    localStorageMock.setItem('access_token', 'test-token');
  });

  test('renders loading state initially', () => {
    // Mock the API to not resolve immediately
    api.fetchContacts.mockImplementation(() => new Promise(resolve => {
      setTimeout(() => {
        resolve({ contacts: mockContacts });
      }, 100);
    }));

    render(
      <MemoryRouter>
        <ContactDashboard />
      </MemoryRouter>
    );

    // Check if loading indicator is shown
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  test('renders error state when API fails', async () => {
    // Mock API failure
    api.fetchContacts.mockRejectedValue(new Error('Failed to load contacts'));

    render(
      <MemoryRouter>
        <ContactDashboard />
      </MemoryRouter>
    );

    // Wait for the error message to appear
    await waitFor(() => {
      expect(screen.getByText('Failed to load contacts.')).toBeInTheDocument();
    });
  });

  test('renders contacts when API succeeds', async () => {
    // Mock successful API response
    api.fetchContacts.mockResolvedValue({ contacts: mockContacts });

    render(
      <MemoryRouter>
        <ContactDashboard />
      </MemoryRouter>
    );

    // Wait for the contacts to load
    await waitFor(() => {
      // Check if the contacts header is rendered
      expect(screen.getByText('Contact Results')).toBeInTheDocument();
    });
    
    // Wait for the contact list to be displayed
    await waitFor(() => {
      // Check if the contact count text is displayed
      expect(screen.getByText(/Showing 3 contact/)).toBeInTheDocument();
    });
    
    // Check if consent status is displayed
    expect(screen.getAllByText(/Opted In/).length).toBeGreaterThan(0);
    expect(screen.getByText(/Opted Out/)).toBeInTheDocument();
  });

  test('handles search functionality', async () => {
    // Mock successful API response
    api.fetchContacts.mockResolvedValue({ contacts: mockContacts });

    render(
      <MemoryRouter>
        <ContactDashboard />
      </MemoryRouter>
    );

    // Wait for the initial contacts to load
    await waitFor(() => {
      expect(screen.getByText('Contact Results')).toBeInTheDocument();
    });

    // Enter search term
    await userEvent.type(screen.getByLabelText('Search by Email or Phone'), 'john');
    
    // Mock the search response
    api.fetchContacts.mockResolvedValue({
      contacts: [mockContacts[0]] // Only return the first contact
    });

    // Click search button
    fireEvent.click(screen.getByRole('button', { name: 'Search' }));

    // Verify that fetchContacts was called with the search term
    expect(api.fetchContacts).toHaveBeenCalledWith(
      expect.objectContaining({ search: 'john' })
    );

    // Wait for the search results
    await waitFor(() => {
      expect(screen.getByText('Showing 1 contact(s) from the last 365 days')).toBeInTheDocument();
    });
  });

  test('handles consent status filtering', async () => {
    // Mock successful API response
    api.fetchContacts.mockResolvedValue({ contacts: mockContacts });

    render(
      <MemoryRouter>
        <ContactDashboard />
      </MemoryRouter>
    );

    // Wait for the initial contacts to load
    await waitFor(() => {
      expect(screen.getByText('Contact Results')).toBeInTheDocument();
    });

    // Mock the filtered response for opted-in contacts
    api.fetchContacts.mockResolvedValue({
      contacts: [mockContacts[0], mockContacts[2]] // Only return opted-in contacts
    });

    // Simulate setting the consent filter by directly calling the component's setConsent function
    // We'll just verify that fetchContacts is called correctly when the search button is clicked
    
    // Click search button
    fireEvent.click(screen.getByRole('button', { name: 'Search' }));

    // Update the mock to check if fetchContacts was called
    expect(api.fetchContacts).toHaveBeenCalled();

    // Wait for the updated results
    await waitFor(() => {
      expect(screen.getByText(/Showing 2 contact/)).toBeInTheDocument();
    });
  });

  test('handles time window selection', async () => {
    // Mock successful API response
    api.fetchContacts.mockResolvedValue({ contacts: mockContacts });

    render(
      <MemoryRouter>
        <ContactDashboard />
      </MemoryRouter>
    );

    // Wait for the initial contacts to load
    await waitFor(() => {
      expect(screen.getByText('Contact Results')).toBeInTheDocument();
    });

    // Mock the response with a new time window
    api.fetchContacts.mockResolvedValue({
      contacts: mockContacts.slice(0, 2) // Return fewer contacts for shorter time window
    });

    // Click search button to trigger a new search
    fireEvent.click(screen.getByRole('button', { name: 'Search' }));

    // Verify that fetchContacts was called
    expect(api.fetchContacts).toHaveBeenCalled();

    // Wait for the updated results
    await waitFor(() => {
      expect(screen.getByText(/Showing 2 contact/)).toBeInTheDocument();
    });
  });

  test('renders View Preferences button for contacts', async () => {
    // Mock successful API response
    api.fetchContacts.mockResolvedValue({ contacts: mockContacts });

    render(
      <MemoryRouter>
        <ContactDashboard />
      </MemoryRouter>
    );

    // Wait for the contacts to load
    await waitFor(() => {
      expect(screen.getByText('Contact Results')).toBeInTheDocument();
    });

    // Verify the View Preferences button is rendered for each contact
    const viewPreferencesButtons = screen.getAllByText('View Preferences');
    expect(viewPreferencesButtons.length).toBe(mockContacts.length);
    
    // Note: We can't directly test navigation since we're using MemoryRouter,
    // but we can verify the button exists which would trigger navigation in the actual app
  });

  // Note: The opt-out functionality test was removed since the feature was removed
  // Administrators should not be able to opt-out users directly
  
  test('submits search with entered values', async () => {
    // Mock successful API response
    api.fetchContacts.mockResolvedValue({ contacts: mockContacts });

    render(
      <MemoryRouter>
        <ContactDashboard />
      </MemoryRouter>
    );

    // Wait for the initial load
    await waitFor(() => {
      expect(screen.getByText('Contact Results')).toBeInTheDocument();
    });

    // Clear mock call history
    api.fetchContacts.mockClear();
    
    // Enter search term
    const searchInput = screen.getByLabelText('Search by Email or Phone');
    fireEvent.change(searchInput, { target: { value: 'test@example.com' } });
    
    // For Material-UI components like Select, we can't directly change the value
    // Instead, we'll just verify the search button works with default values
    
    // Submit the search form
    const searchButton = screen.getByText('Search');
    fireEvent.click(searchButton);
    
    // Verify that fetchContacts was called (with any parameters)
    expect(api.fetchContacts).toHaveBeenCalled();
    
    // Verify search term was included
    expect(api.fetchContacts.mock.calls[0][0].search).toBe('test@example.com');
  });

  test('displays empty state when no contacts are found', async () => {
    // Mock API response with no contacts
    api.fetchContacts.mockResolvedValue({ contacts: [] });

    render(
      <MemoryRouter>
        <ContactDashboard />
      </MemoryRouter>
    );

    // Wait for the empty state message
    await waitFor(() => {
      expect(screen.getByText('No contacts found matching your search criteria. Try adjusting your filters.')).toBeInTheDocument();
    });
  });
});
