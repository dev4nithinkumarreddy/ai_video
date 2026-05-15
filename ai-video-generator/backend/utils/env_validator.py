"""
Environment Validation Utility

Validates required and optional environment variables on application startup.
Provides clear error messages for missing or invalid configuration.
"""

import os
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of environment variable validation"""
    variable_name: str
    is_valid: bool
    is_required: bool
    error_message: Optional[str] = None
    warning_message: Optional[str] = None


class EnvironmentValidator:
    """Validates environment variables for the application"""
    
    def __init__(self, env_file: str = None):
        """Initialize validator with optional env file path"""
        if env_file is None:
            env_file = str(Path(__file__).resolve().parent.parent / ".env")
        self.env_file = env_file
        self.results: List[ValidationResult] = []
        self._load_env_file()
    
    def _load_env_file(self):
        """Load .env file if it exists"""
        env_path = Path(self.env_file)
        if env_path.exists():
            load_dotenv(env_path)
            logger.info(f"[EnvValidator] Loaded environment variables from {self.env_file}")
        else:
            logger.warning(f"[EnvValidator] .env file not found at {self.env_file}")
    
    # Required environment variables
    REQUIRED_VARS = [
        'SECRET_KEY',
        'OPENAI_API_KEY',
        'ELEVENLABS_API_KEY',
        'REPLICATE_API_TOKEN',
    ]
    
    # Optional environment variables
    OPTIONAL_VARS = [
        'HUGGINGFACE_API_KEY',
        'DATABASE_URL',
        'REDIS_URL',
        'CLOUDINARY_CLOUD_NAME',
        'CLOUDINARY_API_KEY',
        'CLOUDINARY_API_SECRET',
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
        'AWS_REGION',
        'AWS_S3_BUCKET',
        'FFMPEG_PATH',
    ]
    
    # Variables that should not be placeholder values
    PLACEHOLDER_PATTERNS = [
        'your-',
        'change-in-production',
        'your-api-key',
        'your-secret-key',
        'placeholder',
    ]
    
    def validate_all(self) -> Tuple[bool, List[ValidationResult]]:
        """
        Validate all environment variables
        
        Returns:
            Tuple of (is_valid, list of validation results)
        """
        logger.info("[EnvValidator] Starting environment variable validation...")
        logger.info(f"[EnvValidator] Validating {len(self.REQUIRED_VARS)} required variables")
        logger.info(f"[EnvValidator] Validating {len(self.OPTIONAL_VARS)} optional variables")
        
        # Validate required variables
        for var_name in self.REQUIRED_VARS:
            logger.debug(f"[EnvValidator] Validating required variable: {var_name}")
            result = self.validate_variable(var_name, required=True)
            self.results.append(result)
            if result.is_valid:
                logger.info(f"[EnvValidator] ✓ {var_name} - Valid")
            else:
                logger.error(f"[EnvValidator] ✗ {var_name} - Invalid: {result.error_message}")
        
        # Validate optional variables
        for var_name in self.OPTIONAL_VARS:
            logger.debug(f"[EnvValidator] Validating optional variable: {var_name}")
            result = self.validate_variable(var_name, required=False)
            self.results.append(result)
            if result.warning_message:
                logger.warning(f"[EnvValidator] ⚠ {var_name} - {result.warning_message}")
            elif result.is_valid:
                logger.info(f"[EnvValidator] ✓ {var_name} - Valid (optional)")
        
        # Check for placeholder values in all set variables
        self._check_placeholders()
        
        # Check overall validity
        is_valid = all(
            result.is_valid 
            for result in self.results 
            if result.is_required
        )
        
        if is_valid:
            logger.info("[EnvValidator] ✓ Environment validation passed")
        else:
            logger.error("[EnvValidator] ✗ Environment validation failed")
        
        return is_valid, self.results
    
    def validate_variable(self, var_name: str, required: bool = True) -> ValidationResult:
        """
        Validate a single environment variable
        
        Args:
            var_name: Name of the environment variable
            required: Whether the variable is required
            
        Returns:
            ValidationResult object
        """
        value = os.getenv(var_name)
        
        if not value:
            if required:
                return ValidationResult(
                    variable_name=var_name,
                    is_valid=False,
                    is_required=required,
                    error_message=f"Required environment variable '{var_name}' is not set"
                )
            else:
                return ValidationResult(
                    variable_name=var_name,
                    is_valid=True,
                    is_required=required,
                    warning_message=f"Optional environment variable '{var_name}' is not set"
                )
        
        # Variable-specific validations
        if var_name == 'SECRET_KEY':
            return self._validate_secret_key(value, var_name, required)
        elif var_name == 'OPENAI_API_KEY':
            return self._validate_openai_key(value, var_name, required)
        elif var_name == 'ELEVENLABS_API_KEY':
            return self._validate_elevenlabs_key(value, var_name, required)
        elif var_name == 'REPLICATE_API_TOKEN':
            return self._validate_replicate_token(value, var_name, required)
        elif var_name == 'DATABASE_URL':
            return self._validate_database_url(value, var_name, required)
        
        return ValidationResult(
            variable_name=var_name,
            is_valid=True,
            is_required=required
        )
    
    def _validate_secret_key(self, value: str, var_name: str, required: bool) -> ValidationResult:
        """Validate SECRET_KEY"""
        if len(value) < 32:
            return ValidationResult(
                variable_name=var_name,
                is_valid=False,
                is_required=required,
                error_message=f"SECRET_KEY must be at least 32 characters long (current: {len(value)})"
            )
        
        if any(pattern in value.lower() for pattern in self.PLACEHOLDER_PATTERNS):
            return ValidationResult(
                variable_name=var_name,
                is_valid=False,
                is_required=required,
                error_message="SECRET_KEY appears to be a placeholder value. Generate a secure key with: python -c \"import secrets; print(secrets.token_hex(32))\""
            )
        
        return ValidationResult(
            variable_name=var_name,
            is_valid=True,
            is_required=required
        )
    
    def _validate_openai_key(self, value: str, var_name: str, required: bool) -> ValidationResult:
        """Validate OPENAI_API_KEY"""
        if not value.startswith('sk-'):
            return ValidationResult(
                variable_name=var_name,
                is_valid=False,
                is_required=required,
                error_message="OPENAI_API_KEY must start with 'sk-'"
            )
        
        if len(value) < 20:
            return ValidationResult(
                variable_name=var_name,
                is_valid=False,
                is_required=required,
                error_message=f"OPENAI_API_KEY appears to be too short (current: {len(value)})"
            )
        
        return ValidationResult(
            variable_name=var_name,
            is_valid=True,
            is_required=required
        )
    
    def _validate_elevenlabs_key(self, value: str, var_name: str, required: bool) -> ValidationResult:
        """Validate ELEVENLABS_API_KEY"""
        if len(value) < 20:
            return ValidationResult(
                variable_name=var_name,
                is_valid=False,
                is_required=required,
                error_message=f"ELEVENLABS_API_KEY appears to be too short (current: {len(value)})"
            )
        
        return ValidationResult(
            variable_name=var_name,
            is_valid=True,
            is_required=required
        )
    
    def _validate_replicate_token(self, value: str, var_name: str, required: bool) -> ValidationResult:
        """Validate REPLICATE_API_TOKEN"""
        if len(value) < 20:
            return ValidationResult(
                variable_name=var_name,
                is_valid=False,
                is_required=required,
                error_message=f"REPLICATE_API_TOKEN appears to be too short (current: {len(value)})"
            )
        
        return ValidationResult(
            variable_name=var_name,
            is_valid=True,
            is_required=required
        )
    
    def _validate_database_url(self, value: str, var_name: str, required: bool) -> ValidationResult:
        """Validate DATABASE_URL"""
        if not value.startswith('postgresql://'):
            return ValidationResult(
                variable_name=var_name,
                is_valid=False,
                is_required=required,
                error_message="DATABASE_URL must start with 'postgresql://'"
            )
        
        return ValidationResult(
            variable_name=var_name,
            is_valid=True,
            is_required=required
        )
    
    def _check_placeholders(self):
        """Check for placeholder values in all environment variables"""
        for var_name in os.environ:
            value = os.environ[var_name]
            if any(pattern in value.lower() for pattern in self.PLACEHOLDER_PATTERNS):
                logger.warning(
                    f"[EnvValidator] Environment variable '{var_name}' appears to contain a placeholder value"
                )
    
    def print_report(self):
        """Print a formatted validation report"""
        print("\n" + "=" * 80)
        print("ENVIRONMENT VALIDATION REPORT")
        print("=" * 80)
        
        required_errors = [r for r in self.results if r.is_required and not r.is_valid]
        optional_warnings = [r for r in self.results if not r.is_required and r.warning_message]
        
        if required_errors:
            print("\n❌ REQUIRED VARIABLES MISSING OR INVALID:")
            for result in required_errors:
                print(f"   - {result.variable_name}: {result.error_message}")
        
        if optional_warnings:
            print("\n⚠️  OPTIONAL VARIABLES NOT SET:")
            for result in optional_warnings:
                print(f"   - {result.variable_name}: {result.warning_message}")
        
        valid_required = [r for r in self.results if r.is_required and r.is_valid]
        if valid_required:
            print("\n✅ REQUIRED VARIABLES CONFIGURED:")
            for result in valid_required:
                masked_value = self._mask_sensitive_value(result.variable_name)
                print(f"   - {result.variable_name}: {masked_value}")
        
        print("\n" + "=" * 80)
        
        if required_errors:
            print("STATUS: FAILED - Please fix the required variables above")
        else:
            print("STATUS: PASSED - All required variables are configured")
        
        print("=" * 80 + "\n")
    
    def _mask_sensitive_value(self, var_name: str) -> str:
        """Mask sensitive values for display"""
        value = os.getenv(var_name, '')
        if len(value) <= 8:
            return '*' * len(value)
        return value[:4] + '*' * (len(value) - 8) + value[-4:]


def validate_environment(env_file: str = ".env") -> bool:
    """
    Convenience function to validate environment and print report
    
    Args:
        env_file: Path to .env file (default: .env)
    
    Returns:
        True if validation passes, False otherwise
    """
    validator = EnvironmentValidator(env_file=env_file)
    is_valid, results = validator.validate_all()
    validator.print_report()
    
    if not is_valid:
        raise EnvironmentError(
            "Environment validation failed. Please check the required environment variables."
        )
    
    return is_valid


if __name__ == "__main__":
    # Run validation when executed directly
    try:
        validate_environment()
    except EnvironmentError as e:
        logger.error(f"Environment validation failed: {e}")
        exit(1)
