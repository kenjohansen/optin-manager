/**
 * main.jsx
 *
 * Application entry point for the OptIn Manager frontend.
 *
 * This file serves as the entry point for the React application, rendering the
 * root App component into the DOM. It uses React's StrictMode to catch potential
 * problems during development and ensure best practices are followed.
 *
 * The application is structured to support the Opt-Out workflow requirements
 * specified in Phase 1, with a focus on providing a clean, accessible interface
 * for users to manage their communication preferences.
 *
 * Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
 * This file is part of the OptIn Manager project and is licensed under the MIT License.
 * See the root LICENSE file for details.
 */

import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
