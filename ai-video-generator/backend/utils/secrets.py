import os
import logging
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
import base64
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class SecureKeyManager:
    """Secure API key management for production"""
    
    def __init__(self, encryption_key: Optional[str] = None):
        self.encryption_key = encryption_key or self._get_or_create_key()
        self.cipher = Fernet(self.encryption_key)
        self.secrets_file = Path("secrets.enc")
    
    def _get_or_create_key(self) -> bytes:
        """Get or create encryption key"""
        key_file = Path("encryption.key")
        
        if key_file.exists():
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            # Set secure permissions
            os.chmod(key_file, 0o600)
            return key
    
    def encrypt_secret(self, secret: str) -> str:
        """Encrypt a secret"""
        encrypted = self.cipher.encrypt(secret.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt_secret(self, encrypted_secret: str) -> str:
        """Decrypt a secret"""
        encrypted = base64.b64decode(encrypted_secret.encode())
        decrypted = self.cipher.decrypt(encrypted)
        return decrypted.decode()
    
    def store_secrets(self, secrets: Dict[str, str]) -> bool:
        """Store encrypted secrets"""
        try:
            encrypted_secrets = {}
            for key, value in secrets.items():
                encrypted_secrets[key] = self.encrypt_secret(value)
            
            with open(self.secrets_file, 'w') as f:
                json.dump(encrypted_secrets, f)
            
            # Set secure permissions
            os.chmod(self.secrets_file, 0o600)
            return True
        except Exception as e:
            logger.error(f"Error storing secrets: {str(e)}")
            return False
    
    def load_secrets(self) -> Dict[str, str]:
        """Load and decrypt secrets"""
        try:
            if not self.secrets_file.exists():
                return {}
            
            with open(self.secrets_file, 'r') as f:
                encrypted_secrets = json.load(f)
            
            secrets = {}
            for key, encrypted_value in encrypted_secrets.items():
                secrets[key] = self.decrypt_secret(encrypted_value)
            
            return secrets
        except Exception as e:
            logger.error(f"Error loading secrets: {str(e)}")
            return {}
    
    def get_secret(self, key: str) -> Optional[str]:
        """Get a specific secret"""
        secrets = self.load_secrets()
        return secrets.get(key)
    
    def set_secret(self, key: str, value: str) -> bool:
        """Set a specific secret"""
        secrets = self.load_secrets()
        secrets[key] = value
        return self.store_secrets(secrets)


class EnvironmentSecretManager:
    """Environment-based secret management"""
    
    @staticmethod
    def get_required_secret(key: str) -> str:
        """Get required secret from environment"""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required environment variable {key} is not set")
        return value
    
    @staticmethod
    def get_optional_secret(key: str, default: Optional[str] = None) -> Optional[str]:
        """Get optional secret from environment"""
        return os.getenv(key, default)
    
    @staticmethod
    def validate_secrets() -> Dict[str, bool]:
        """Validate required secrets"""
        required_secrets = [
            "OPENAI_API_KEY",
            "ELEVENLABS_API_KEY", 
            "REPLICATE_API_TOKEN",
            "SECRET_KEY",
            "JWT_SECRET_KEY"
        ]
        
        validation_results = {}
        for secret in required_secrets:
            validation_results[secret] = bool(os.getenv(secret))
        
        return validation_results


# Global secret manager instance
_secret_manager: Optional[SecureKeyManager] = None


def get_secret_manager() -> SecureKeyManager:
    """Get global secret manager instance"""
    global _secret_manager
    if _secret_manager is None:
        _secret_manager = SecureKeyManager()
    return _secret_manager


def get_api_key(service: str) -> str:
    """Get API key for a specific service"""
    env_manager = EnvironmentSecretManager()
    
    if service == "openai":
        return env_manager.get_required_secret("OPENAI_API_KEY")
    elif service == "elevenlabs":
        return env_manager.get_required_secret("ELEVENLABS_API_KEY")
    elif service == "replicate":
        return env_manager.get_required_secret("REPLICATE_API_TOKEN")
    else:
        raise ValueError(f"Unknown service: {service}")


def setup_production_secrets() -> bool:
    """Setup production secrets from environment"""
    try:
        env_manager = EnvironmentSecretManager()
        validation_results = env_manager.validate_secrets()
        
        missing_secrets = [k for k, v in validation_results.items() if not v]
        if missing_secrets:
            logger.error(f"Missing required secrets: {missing_secrets}")
            return False
        
        logger.info("All required secrets are configured")
        return True
    except Exception as e:
        logger.error(f"Error setting up production secrets: {str(e)}")
        return False
