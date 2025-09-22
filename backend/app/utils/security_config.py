"""
Security Configuration and Improvements
=======================================

This file contains security recommendations and improvements for the Book Library API.
"""

import os
import secrets
from typing import List

def generate_secure_secret_key() -> str:
    """Generate a cryptographically secure secret key for JWT tokens."""
    return secrets.token_urlsafe(32)

def validate_production_config() -> List[str]:
    """
    Validate production configuration and return list of warnings/errors.
    
    Returns:
        List of configuration issues that need attention
    """
    config_issues = []
    
    # Check SECRET_KEY
    secret_key = os.getenv("SECRET_KEY")
    if not secret_key or secret_key == "default-secret-key-change-in-production":
        config_issues.append("🚨 CRITICAL: SECRET_KEY is not set or using default value!")
    elif len(secret_key) < 32:
        config_issues.append("⚠️  WARNING: SECRET_KEY should be at least 32 characters long")
    
    # Check DATABASE_URL
    database_url = os.getenv("DATABASE_URL", "")
    if "root:@" in database_url:
        config_issues.append("🚨 CRITICAL: Database using empty password for root user!")
    if "localhost" in database_url:
        config_issues.append("⚠️  INFO: Database is on localhost (ok for development)")
    
    # Check CORS settings
    cors_origins = os.getenv("CORS_ORIGINS")
    if not cors_origins:
        config_issues.append("⚠️  WARNING: CORS_ORIGINS not explicitly set")
    
    return config_issues

# Production Security Headers
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY", 
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
    "Referrer-Policy": "strict-origin-when-cross-origin"
}

# Rate Limiting Configuration
RATE_LIMIT_CONFIG = {
    "login_attempts": "5/minute",
    "api_calls": "100/minute", 
    "password_reset": "3/hour",
    "registration": "10/hour"
}

def get_security_recommendations() -> List[str]:
    """
    Get list of security recommendations for production deployment.
    
    Returns:
        List of security recommendations
    """
    return [
        "1. 🔑 Set strong SECRET_KEY in environment variables",
        "2. 🗄️  Use proper database credentials with restricted permissions", 
        "3. 🌐 Configure HTTPS/TLS for all endpoints",
        "4. 🛡️  Add rate limiting middleware",
        "5. 📊 Implement security headers middleware",
        "6. 🔒 Enable database connection encryption",
        "7. 📝 Set up proper logging and monitoring",
        "8. 🚫 Remove console.log statements from production frontend",
        "9. 🧪 Use separate test database with different credentials",
        "10. 📧 Configure email service for notifications",
        "11. 🔄 Implement automated backups",
        "12. 🔍 Add input validation middleware",
        "13. 💾 Consider Redis for session storage",
        "14. 🏗️  Use container orchestration (Docker/Kubernetes)",
        "15. 🔐 Implement API key management for external integrations"
    ]

if __name__ == "__main__":
    print("🔒 Security Configuration Checker")
    print("=" * 40)
    
    # Check current configuration
    issues = validate_production_config()
    if issues:
        print("\n❌ Configuration Issues Found:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("\n✅ Configuration looks good!")
    
    # Show recommendations
    print("\n📋 Security Recommendations:")
    recommendations = get_security_recommendations()
    for rec in recommendations:
        print(f"  {rec}")
    
    # Generate new secret key example
    print("\n🔑 Example secure SECRET_KEY:")
    print(f"  SECRET_KEY={generate_secure_secret_key()}")
