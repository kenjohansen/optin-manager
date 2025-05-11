
  // Test refreshCustomization with various data scenarios
  test('handles refreshCustomization with various data scenarios', async () => {
    // Reset mocks
    jest.clearAllMocks();
    
    // Test with empty data
    api.fetchCustomization.mockResolvedValueOnce({});
    
    // Mock parent component update functions
    const setLogoUrlMock = jest.fn();
    const setPrimaryMock = jest.fn();
    const setSecondaryMock = jest.fn();
    const setCompanyNameMock = jest.fn();
    const setPrivacyPolicyMock = jest.fn();
    
    const mockPropsWithUpdates = {
      setLogoUrl: setLogoUrlMock,
      setPrimary: setPrimaryMock,
      setSecondary: setSecondaryMock,
      setCompanyName: setCompanyNameMock,
      setPrivacyPolicy: setPrivacyPolicyMock
    };
    
    render(
      <MemoryRouter>
        <Customization {...mockPropsWithUpdates} />
      </MemoryRouter>
    );
    
    // Wait for component to load
    await waitFor(() => {
      expect(screen.getByTestId('branding-section')).toBeInTheDocument();
    });
    
    // Cleanup
    cleanup();
    
    // Reset mocks
    jest.clearAllMocks();
    
    // Test with complete data
    api.fetchCustomization.mockResolvedValueOnce({
      logo_url: 'https://example.com/logo.png',
      primary_color: '#FF5733',
      secondary_color: '#33FF57',
      company_name: 'Test Company',
      privacy_policy_url: 'https://example.com/privacy',
      email_provider: 'aws_ses',
      sms_provider: 'aws_sns'
    });
    
    render(
      <MemoryRouter>
        <Customization {...mockPropsWithUpdates} />
      </MemoryRouter>
    );
    
    // Wait for component to load
    await waitFor(() => {
      expect(screen.getByTestId('branding-section')).toBeInTheDocument();
    });
    
    // Verify that parent component update functions were called
    await waitFor(() => {
      expect(setPrimaryMock).toHaveBeenCalled();
      expect(setSecondaryMock).toHaveBeenCalled();
      expect(setCompanyNameMock).toHaveBeenCalled();
      expect(setPrivacyPolicyMock).toHaveBeenCalled();
      expect(setLogoUrlMock).toHaveBeenCalled();
    });
  });

  // Test save customization with various error scenarios
  test('handles save customization with various error scenarios', async () => {
    // Reset mocks
    jest.clearAllMocks();
    
    // Mock 401 authentication error
    api.saveCustomization.mockRejectedValueOnce({
      response: {
        status: 401,
        data: { detail: 'Authentication credentials were not provided' }
      }
    });
    
    render(
      <MemoryRouter>
        <Customization {...mockProps} />
      </MemoryRouter>
    );
    
    // Wait for component to load
    await waitFor(() => {
      expect(screen.getByTestId('branding-section')).toBeInTheDocument();
    });
    
    // Trigger save
    const saveButton = screen.getByTestId('save-branding-button');
    await act(async () => {
      fireEvent.click(saveButton);
    });
    
    // Check for alert message
    await waitFor(() => {
      const alerts = screen.getAllByRole('alert');
      expect(alerts.length).toBeGreaterThan(0);
    });
    
    // Cleanup
    cleanup();
    
    // Reset mocks
    jest.clearAllMocks();
    
    // Mock error with specific error message
    api.saveCustomization.mockRejectedValueOnce({
      response: {
        status: 400,
        data: { detail: 'Invalid file format' }
      }
    });
    
    render(
      <MemoryRouter>
        <Customization {...mockProps} />
      </MemoryRouter>
    );
    
    // Wait for component to load
    await waitFor(() => {
      expect(screen.getByTestId('branding-section')).toBeInTheDocument();
    });
    
    // Trigger save
    const saveButton2 = screen.getByTestId('save-branding-button');
    await act(async () => {
      fireEvent.click(saveButton2);
    });
    
    // Check for alert message
    await waitFor(() => {
      const alerts = screen.getAllByRole('alert');
      expect(alerts.length).toBeGreaterThan(0);
    });
  });
