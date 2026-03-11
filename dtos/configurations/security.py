"""
DTOs for security-related configuration settings (rate limiting, headers,
validation, auth, CORS).
"""

from pydantic import BaseModel


class RateLimitingConfig(BaseModel):
    """Rate limiting configuration."""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    burst_limit: int = 10
    window_size: int = 60
    enable_sliding_window: bool = True
    enable_token_bucket: bool = False
    enable_fixed_window: bool = False
    excluded_paths: list[str] = ["/health", "/docs", "/openapi.json"]
    excluded_methods: list[str] = ["OPTIONS"]


class SecurityHeadersConfigDTO(BaseModel):
    """Security headers configuration."""
    enable_hsts: bool = True
    enable_csp: bool = True
    csp_report_only: bool = False
    hsts_max_age: int = 31536000
    hsts_include_subdomains: bool = True
    hsts_preload: bool = False
    frame_options: str = "DENY"
    content_type_options: str = "nosniff"
    xss_protection: str = "1; mode=block"
    referrer_policy: str = "strict-origin-when-cross-origin"
    custom_csp: str | None = None
    custom_permissions_policy: str | None = None


class InputValidationConfigDTO(BaseModel):
    """Input validation configuration."""
    max_string_length: int = 1000
    max_password_length: int = 128
    min_password_length: int = 8
    max_email_length: int = 254
    enable_sql_injection_check: bool = True
    enable_xss_check: bool = True
    enable_path_traversal_check: bool = True
    weak_passwords: list[str] = [
        "password", "123456", "qwerty", "admin", "letmein"
    ]


class AuthenticationConfigDTO(BaseModel):
    """Authentication configuration."""
    jwt_expiry_minutes: int = 30
    refresh_token_expiry_days: int = 7
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15
    password_history_count: int = 5
    require_strong_password: bool = True
    session_timeout_minutes: int = 60


class CORSConfigDTO(BaseModel):
    """CORS configuration."""
    allowed_origins: list[str] = ["*"]
    allowed_methods: list[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allowed_headers: list[str] = ["*"]
    allow_credentials: bool = True
    max_age: int = 3600


class SecurityConfigurationDTO(BaseModel):
    """Complete security configuration DTO."""
    rate_limiting: RateLimitingConfig = RateLimitingConfig()
    security_headers: SecurityHeadersConfigDTO = SecurityHeadersConfigDTO()
    input_validation: InputValidationConfigDTO = InputValidationConfigDTO()
    authentication: AuthenticationConfigDTO = AuthenticationConfigDTO()
    cors: CORSConfigDTO = CORSConfigDTO()
