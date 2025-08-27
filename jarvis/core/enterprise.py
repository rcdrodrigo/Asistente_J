""Enterprise features for the Voice Agent."""

import asyncio
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Dict, List, Optional, Any
import uuid
import hashlib
import secrets
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)

class UserRole(str, Enum):
    GUEST = "guest"
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

class UserProfile(BaseModel):
    user_id: str = Field(default_factory=lambda: f"user_{uuid.uuid4().hex[:8]}")
    username: str
    email: str
    role: UserRole = UserRole.USER
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

class SessionManager:
    """Manages user sessions and authentication."""
    
    def __init__(self, session_timeout: int = 1800):
        self._sessions: Dict[str, Dict] = {}
        self._users: Dict[str, Dict] = {}
        self._session_timeout = session_timeout
        self._lock = asyncio.Lock()
    
    async def create_user(self, username: str, email: str, password: str) -> UserProfile:
        """Create a new user with hashed password."""
        async with self._lock:
            if any(u["profile"].username == username for u in self._users.values()):
                raise ValueError(f"Username '{username}' already exists")
                
            user = UserProfile(username=username, email=email)
            self._users[user.user_id] = {
                "profile": user,
                "password_hash": self._hash_password(password)
            }
            return user
    
    async def authenticate(self, username: str, password: str) -> Optional[str]:
        """Authenticate user and return session token."""
        async with self._lock:
            user_data = next(
                (u for u in self._users.values() 
                 if u["profile"].username == username and u["profile"].is_active),
                None
            )
            
            if not user_data or not self._verify_password(password, user_data["password_hash"]):
                return None
            
            user = user_data["profile"]
            user.last_login = datetime.utcnow()
            
            session_id = secrets.token_urlsafe(32)
            self._sessions[session_id] = {
                "user_id": user.user_id,
                "created_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(seconds=self._session_timeout)
            }
            
            return session_id
    
    def _hash_password(self, password: str) -> str:
        salt = secrets.token_hex(16)
        return f"{salt}:{hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()}"
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        try:
            salt, stored_hash = hashed.split(':')
            computed_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
            return secrets.compare_digest(computed_hash, stored_hash)
        except ValueError:
            return False

class AuditLogger:
    """Handles audit logging for security and compliance."""
    
    def __init__(self, max_entries: int = 10000):
        self._entries: List[Dict] = []
        self._max_entries = max_entries
    
    async def log(self, action: str, user_id: Optional[str] = None, **details):
        """Add an entry to the audit log."""
        entry = {
            "timestamp": datetime.utcnow(),
            "user_id": user_id,
            "action": action,
            "details": details
        }
        self._entries.append(entry)
        
        if len(self._entries) > self._max_entries:
            self._entries = self._entries[-self._max_entries:]
