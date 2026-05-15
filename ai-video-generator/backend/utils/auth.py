import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext

from utils.config import get_settings

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
settings = get_settings()
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Password verification error: {str(e)}")
        return False


def get_password_hash(password: str) -> str:
    """Hash a password"""
    try:
        return pwd_context.hash(password)
    except Exception as e:
        logger.error(f"Password hashing error: {str(e)}")
        raise ValueError("Failed to hash password")


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        logger.error(f"JWT verification error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected JWT error: {str(e)}")
        return None


def create_refresh_token(user_id: int, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT refresh token"""
    to_encode = {"sub": str(user_id), "type": "refresh"}
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)  # Refresh tokens last longer
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_refresh_token(token: str) -> Optional[int]:
    """Verify a refresh token and return user ID"""
    payload = verify_token(token)
    
    if not payload:
        return None
    
    if payload.get("type") != "refresh":
        return None
    
    try:
        return int(payload.get("sub"))
    except (ValueError, TypeError):
        return None


def validate_password_strength(password: str) -> Dict[str, Any]:
    """Validate password strength"""
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if not any(c.isupper() for c in password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not any(c.islower() for c in password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not any(c.isdigit() for c in password):
        errors.append("Password must contain at least one digit")
    
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        errors.append("Password must contain at least one special character")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


def generate_password_reset_token(email: str) -> str:
    """Generate a password reset token"""
    to_encode = {"email": email, "type": "password_reset"}
    expire = datetime.utcnow() + timedelta(hours=1)  # Reset tokens expire in 1 hour
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password_reset_token(token: str) -> Optional[str]:
    """Verify a password reset token and return email"""
    payload = verify_token(token)
    
    if not payload:
        return None
    
    if payload.get("type") != "password_reset":
        return None
    
    return payload.get("email")


class TokenManager:
    """Manages JWT tokens with blacklisting support"""
    
    def __init__(self):
        self.blacklisted_tokens = set()
    
    def blacklist_token(self, token: str) -> bool:
        """Add a token to the blacklist"""
        try:
            payload = verify_token(token)
            if payload:
                jti = payload.get("jti")
                if jti:
                    self.blacklisted_tokens.add(jti)
                    return True
        except Exception as e:
            logger.error(f"Error blacklisting token: {str(e)}")
        return False
    
    def is_token_blacklisted(self, token: str) -> bool:
        """Check if a token is blacklisted"""
        try:
            payload = verify_token(token)
            if payload:
                jti = payload.get("jti")
                return jti in self.blacklisted_tokens
        except Exception as e:
            logger.error(f"Error checking token blacklist: {str(e)}")
        return False
    
    def cleanup_blacklist(self):
        """Clean up expired tokens from blacklist"""
        # This would be implemented with a more sophisticated system
        # For now, we'll just clear the blacklist periodically
        if len(self.blacklisted_tokens) > 1000:
            self.blacklisted_tokens.clear()


# Global token manager instance
token_manager = TokenManager()
