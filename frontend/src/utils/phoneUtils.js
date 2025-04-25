/**
 * Phone number formatting and validation utilities
 */

/**
 * Formats a phone number to E.164 international format
 * If no country code is provided, defaults to US (+1)
 * 
 * @param {string} phoneNumber - The input phone number
 * @returns {string} - The formatted E.164 phone number
 */
export function formatPhoneToE164(phoneNumber) {
  if (!phoneNumber) return '';
  
  // Remove all non-digit characters
  let digitsOnly = phoneNumber.replace(/\D/g, '');
  
  // Check if the number already has a country code (starts with + or has 11+ digits)
  const hasCountryCode = phoneNumber.startsWith('+') || digitsOnly.length >= 11;
  
  // If no country code, add +1 (US) by default
  if (!hasCountryCode) {
    // For US numbers, if it's 10 digits, add +1
    if (digitsOnly.length === 10) {
      return `+1${digitsOnly}`;
    }
    // For shorter numbers, assume it's a partial US number
    else if (digitsOnly.length < 10) {
      return `+1${digitsOnly}`;
    }
  } else {
    // If it already has a plus sign, keep the original format but clean it
    if (phoneNumber.startsWith('+')) {
      return `+${digitsOnly}`;
    }
    // If it has 11+ digits but no plus sign, assume first digit is country code
    else if (digitsOnly.length >= 11) {
      return `+${digitsOnly}`;
    }
  }
  
  // Default case - just add + to the digits
  return `+${digitsOnly}`;
}

/**
 * Validates if a string looks like a valid phone number
 * 
 * @param {string} phoneNumber - The input phone number
 * @returns {boolean} - True if it's a valid phone number
 */
export function isValidPhoneNumber(phoneNumber) {
  if (!phoneNumber) return false;
  
  // Basic validation - at least 8 digits after removing non-digits
  const digitsOnly = phoneNumber.replace(/\D/g, '');
  return digitsOnly.length >= 8;
}
