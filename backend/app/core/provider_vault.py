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
    # Stub for future Vault integration
    # If VAULT_ADDR or config detected, try to fetch key from Vault
    return None


def _get_vault_key():
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
    def __init__(self):
        self.vault_path = VAULT_PATH
        self.key = _get_vault_key()
        self.fernet = Fernet(self.key)
        self.secrets = self._load_vault()

    def _load_vault(self) -> Dict[str, str]:
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
        data = json.dumps(self.secrets).encode()
        encrypted = self.fernet.encrypt(data)
        with open(self.vault_path, 'wb') as f:
            f.write(encrypted)

    def get_secret(self, key: str) -> Optional[str]:
        return self.secrets.get(key)

    def set_secret(self, key: str, value: str):
        self.secrets[key] = value
        self._save_vault()

    def delete_secret(self, key: str):
        if key in self.secrets:
            del self.secrets[key]
            self._save_vault()

    def list_secrets(self):
        return list(self.secrets.keys())
