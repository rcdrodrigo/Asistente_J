"""Robust error handling and recovery for the Voice Agent."""

import asyncio
import logging
from typing import Optional, Type, TypeVar, Callable, Any, Awaitable
from functools import wraps
import traceback
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4
    CRITICAL = 5

@dataclass
class ErrorContext:
    """Context information for error handling."""
    timestamp: datetime = None
    severity: ErrorSeverity = ErrorSeverity.ERROR
    component: str = "unknown"
    operation: str = "unknown"
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    metadata: dict = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}

class RecoveryAction(Enum):
    RETRY = "retry"
    FALLBACK = "fallback"
    NOTIFY = "notify"
    TERMINATE = "terminate"

class VoiceAgentError(Exception):
    """Base exception for voice agent errors."""
    def __init__(self, message: str, context: Optional[ErrorContext] = None):
        super().__init__(message)
        self.context = context or ErrorContext()
        self.message = message

class AudioProcessingError(VoiceAgentError):
    """Error during audio processing."""
    pass

class AuthenticationError(VoiceAgentError):
    """Authentication or authorization error."""
    pass

class RateLimitExceededError(VoiceAgentError):
    """Rate limit exceeded."""
    pass

def with_error_handling(
    component: str = "unknown",
    operation: str = "unknown",
    max_retries: int = 3,
    default_return: Any = None,
    log_errors: bool = True,
    capture_metrics: bool = True
):
    """Decorator for adding error handling to async functions."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            context = ErrorContext(
                component=component,
                operation=operation,
                max_retries=max_retries
            )
            
            last_error = None
            
            while context.retry_count <= context.max_retries:
                try:
                    result = await func(*args, **kwargs, _error_context=context)
                    return result
                except Exception as e:
                    last_error = e
                    context.retry_count += 1
                    
                    # Log the error
                    if log_errors:
                        logger.error(
                            f"Error in {component}.{operation} (attempt {context.retry_count}/{max_retries}): {str(e)}",
                            exc_info=True
                        )
                    
                    # Determine recovery action
                    action = _determine_recovery_action(e, context)
                    
                    if action == RecoveryAction.RETRY and context.retry_count <= context.max_retries:
                        # Exponential backoff
                        backoff = min(2 ** context.retry_count, 10)  # Max 10 seconds
                        await asyncio.sleep(backoff)
                        continue
                    elif action == RecoveryAction.FALLBACK:
                        return await _handle_fallback(e, context, default_return)
                    elif action == RecoveryAction.NOTIFY:
                        await _notify_operator(e, context)
                        return default_return
                    else:  # TERMINATE or unknown action
                        break
            
            # If we get here, all retries failed
            await _handle_failure(last_error, context)
            return default_return
            
        return wrapper
    return decorator

def _determine_recovery_action(error: Exception, context: ErrorContext) -> RecoveryAction:
    """Determine the appropriate recovery action for an error."""
    if isinstance(error, RateLimitExceededError):
        return RecoveryAction.RETRY
    elif isinstance(error, (asyncio.TimeoutError, ConnectionError)):
        if context.retry_count < context.max_retries:
            return RecoveryAction.RETRY
        return RecoveryAction.FALLBACK
    elif isinstance(error, AuthenticationError):
        return RecoveryAction.NOTIFY
    return RecoveryAction.TERMINATE

async def _handle_fallback(error: Exception, context: ErrorContext, default_result: Any) -> Any:
    """Handle fallback behavior when recovery is not possible."""
    logger.warning(f"Using fallback for {context.component}.{context.operation}")
    # TODO: Implement specific fallback logic based on the operation
    return default_result

async def _notify_operator(error: Exception, context: ErrorContext) -> None:
    """Notify operators about critical errors."""
    # TODO: Implement notification logic (email, Slack, etc.)
    logger.critical(
        f"Operator notification required for {context.component}.{context.operation}: {str(error)}",
        exc_info=True
    )

async def _handle_failure(error: Exception, context: ErrorContext) -> None:
    """Handle final failure after all recovery attempts."""
    logger.critical(
        f"Operation {context.component}.{context.operation} failed after "
        f"{context.retry_count} attempts: {str(error)}",
        exc_info=True
    )
    # TODO: Implement failure handling (cleanup, state reset, etc.)

class ErrorMonitor:
    """Monitors and aggregates errors for analysis and reporting."""
    
    def __init__(self, max_errors: int = 1000):
        self.errors = []
        self.error_counts = {}
        self.max_errors = max_errors
    
    def record_error(self, error: Exception, context: Optional[ErrorContext] = None):
        """Record an error for monitoring."""
        error_name = error.__class__.__name__
        self.error_counts[error_name] = self.error_counts.get(error_name, 0) + 1
        
        error_info = {
            "timestamp": datetime.utcnow(),
            "error": error_name,
            "message": str(error),
            "component": context.component if context else "unknown",
            "operation": context.operation if context else "unknown",
            "traceback": traceback.format_exc()
        }
        
        self.errors.append(error_info)
        if len(self.errors) > self.max_errors:
            self.errors.pop(0)
    
    def get_error_stats(self) -> dict:
        """Get statistics about recorded errors."""
        return {
            "total_errors": len(self.errors),
            "error_counts": self.error_counts,
            "recent_errors": self.errors[-10:],  # Last 10 errors
        }

# Global error monitor instance
error_monitor = ErrorMonitor()

# Example usage
if __name__ == "__main__":
    @with_error_handling(component="test", operation="example", max_retries=2)
    async def example_function(fail: bool = False):
        if fail:
            raise ValueError("Something went wrong!")
        return "Success"
    
    async def main():
        # This will succeed
        result = await example_function()
        print(f"Result: {result}")
        
        # This will fail after retries
        try:
            await example_function(fail=True)
        except Exception as e:
            print(f"Caught error: {e}")
    
    asyncio.run(main())
