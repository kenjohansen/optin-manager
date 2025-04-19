import { render, screen } from '@testing-library/react';
import App from './App';

test('renders OptIn Manager header', () => {
  render(<App />);
  expect(screen.getByText(/OptIn Manager/i)).toBeInTheDocument();
});
