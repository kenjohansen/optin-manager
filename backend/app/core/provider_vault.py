"""
core/provider_vault.py

Secure storage and management of communication provider credentials and secrets.

This module implements a secure vault system for storing sensitive provider credentials
(API keys, tokens, etc.) needed for sending messages via SMS, email, or other channels.
It uses Fernet symmetric encryption to protect these secrets at rest and provides
multiple secure key storage options for different deployment environments.

Copyright (c) 2025 Ken Johansen, OptIn Manager Contributors
This file is part of the OptIn Manager project and is licensed under the MIT License.
See the root LICENSE file for details.
"""

import os
import sys
import json
import platform
from cryptography.fernet import Fernet, InvalidToken
from typing import Dict, Optional

VAULT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../vault/provider_secrets.vault'))
KEY_ENV = 'PROVIDER_VAULT_KEY'

# For K8s secret mount or future Vault integration
K8S_SECRET_PATH = '/vault/secrets/provider_vault.key'

# OS-protected key location
LINUX_KEY_PATH = '/etc/optin-manager/provider_vault.key'
WINDOWS_KEY_PATH = os.path.join(os.environ.get('PROGRAMDATA', 'C:\\ProgramData'), 'OptInManager', 'provider_vault.key')

# Project fallback (dev only)
PROJECT_KEY_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../vault/provider_vault.key'))


def _try_hashicorp_vault():
    """
    Stub for future HashiCorp Vault integration.
    
    This function is a placeholder for future integration with HashiCorp Vault,
    which would provide enterprise-grade secret management capabilities. When
    implemented, it would detect Vault configuration and fetch the encryption
    key from the Vault service.
    
    Returns:
        bytes or None: The encryption key if available from Vault, None otherwise
    """
    # Stub for future Vault integration
    # If VAULT_ADDR or config detected, try to fetch key from Vault
    return None


def _get_vault_key():
    """
    Retrieve the encryption key for the provider secrets vault.
    
    This function implements a secure key retrieval strategy with multiple fallback
    options, prioritized from most secure to least secure:
    
    1. Environment variable (suitable for cloud environments)
    2. HashiCorp Vault (enterprise integration, stubbed for future)
    3. Kubernetes Secret mount (for containerized deployments)
    4. OS-protected file (for traditional server deployments)
    5. Project directory fallback (for development only)
    
    If no key is found in any location, a new key is generated and stored in the
    project directory as a last resort for development environments.
    
    This multi-tiered approach ensures the system can operate securely across
    different deployment environments while maintaining strong security practices.
    
    Returns:
        bytes: The encryption key for the vault
    """
    # 1. ENV variable
    key = os.getenv(KEY_ENV)
    if key:
        print("[vault] Loaded key from ENV variable.")
        return key.encode()
    # 2. HashiCorp Vault (stub)
    key = _try_hashicorp_vault()
    if key:
        print("[vault] Loaded key from HashiCorp Vault.")
        return key
    # 3. K8s Secret (mounted file)
    if os.path.exists(K8S_SECRET_PATH):
        with open(K8S_SECRET_PATH, 'rb') as f:
            print(f"[vault] Loaded key from K8s Secret at {K8S_SECRET_PATH}.")
            return f.read()
    # 4. OS-protected file
    if platform.system() == "Windows":
        key_path = WINDOWS_KEY_PATH
    else:
        key_path = LINUX_KEY_PATH
    if os.path.exists(key_path):
        with open(key_path, 'rb') as f:
            print(f"[vault] Loaded key from OS-protected file at {key_path}.")
            return f.read()
    # 5. Fallback: project dir (dev only, warning)
    if os.path.exists(PROJECT_KEY_PATH):
        with open(PROJECT_KEY_PATH, 'rb') as f:
            print(f"[vault][WARNING] Loaded key from project directory fallback at {PROJECT_KEY_PATH}. Not recommended for production!")
            return f.read()
    # If no key, generate and store in project dir (dev only)
    key = Fernet.generate_key()
    os.makedirs(os.path.dirname(PROJECT_KEY_PATH), exist_ok=True)
    with open(PROJECT_KEY_PATH, 'wb') as f:
        f.write(key)
    try:
        os.chmod(PROJECT_KEY_PATH, 0o600)
    except Exception:
        pass
    print(f"[vault][WARNING] Auto-generated key in project directory at {PROJECT_KEY_PATH}. Not recommended for production!")
    return key


class ProviderSecretsVault:
    """
    Secure vault for managing communication provider credentials and secrets.
    
    This class provides encrypted storage for sensitive provider credentials
    such as API keys, tokens, and account information needed to send messages
    via SMS, email, or other communication channels. It uses Fernet symmetric
    encryption to protect these secrets at rest.
    
    The vault is essential for the system's communication capabilities while
    maintaining security best practices by never storing credentials in plaintext.
    It supports the customization settings for communication providers as noted
    in the memories about UI branding elements and communication provider settings.
    """
    
    def __init__(self):
        """
        Initialize the provider secrets vault.
        
        This constructor sets up the vault by determining the vault file location,
        retrieving the encryption key through the secure key retrieval strategy,
        initializing the Fernet cipher suite, and loading any existing secrets.
        """
        self.vault_path = VAULT_PATH
        self.key = _get_vault_key()
        self.fernet = Fernet(self.key)
        self.secrets = self._load_vault()

    def _load_vault(self) -> Dict[str, str]:
        """
        Load and decrypt the provider secrets from the vault file.
        
        This private method reads the encrypted vault file, decrypts its contents
        using the Fernet key, and deserializes the JSON data into a dictionary.
        If the vault file doesn't exist, it returns an empty dictionary to start
        with a clean slate.
        
        Returns:
            Dict[str, str]: Dictionary of provider secrets with keys as identifiers
                           and values as the actual secret credentials
                           
        Raises:
            RuntimeError: If decryption fails due to an invalid key or corrupted file
        """
        if not os.path.exists(self.vault_path):
            return {}
        with open(self.vault_path, 'rb') as f:
            encrypted = f.read()
            try:
                decrypted = self.fernet.decrypt(encrypted)
                return json.loads(decrypted.decode())
            except InvalidToken:
                raise RuntimeError("Vault decryption failed: invalid key or corrupted file.")

    def _save_vault(self):
        """
        Encrypt and save the provider secrets to the vault file.
        
        This private method serializes the secrets dictionary to JSON, encrypts
        the data using the Fernet key, and writes the encrypted data to the vault
        file. This ensures that all provider credentials are securely stored
        at rest with no plaintext exposure.
        """
        data = json.dumps(self.secrets).encode()
        encrypted = self.fernet.encrypt(data)
        with open(self.vault_path, 'wb') as f:
            f.write(encrypted)

    def get_secret(self, key: str) -> Optional[str]:
        """
        Retrieve a provider secret by its key.
        
        This method safely retrieves a provider credential from the vault using
        its identifier key. If the key doesn't exist, it returns None rather than
        raising an exception, allowing for graceful handling of missing credentials.
        
        Args:
            key (str): The identifier for the secret to retrieve
            
        Returns:
            Optional[str]: The secret value if found, None otherwise
        """
        return self.secrets.get(key)

    def set_secret(self, key: str, value: str):
        """
        Store or update a provider secret in the vault.
        
        This method adds a new provider credential or updates an existing one in
        the vault, then immediately saves the vault to ensure the change is persisted
        securely. This is used when configuring new communication providers or
        updating existing credentials.
        
        Args:
            key (str): The identifier for the secret
            value (str): The secret value to store
        """
        self.secrets[key] = value
        self._save_vault()

    def delete_secret(self, key: str):
        """
        Remove a provider secret from the vault.
        
        This method deletes a provider credential from the vault if it exists,
        then immediately saves the vault to ensure the change is persisted.
        This is used when removing communication providers or rotating credentials.
        
        Args:
            key (str): The identifier for the secret to delete
        """
        if key in self.secrets:
            del self.secrets[key]
            self._save_vault()

    def list_secrets(self):
        """
        List all provider secret identifiers in the vault.
        
        This method returns a list of all secret identifiers (keys) currently
        stored in the vault. It only returns the identifiers, not the actual
        secret values, to prevent accidental exposure of sensitive information.
        
        Returns:
            list: List of secret identifiers (keys)
        """
        return list(self.secrets.keys())
