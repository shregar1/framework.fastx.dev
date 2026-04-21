"""Helpers for env-backed settings, middleware wiring, and startup validation.

JSON deployment overrides live under :mod:`config`.
"""

from abstractions.utility import IUtility
from utilities.auth import constant_time_compare, parse_basic_authorization
from utilities.cors import CorsConfigUtility
from utilities.datetime import DateTimeUtility
from utilities.dictionary import DictionaryUtility
from utilities.env import EnvironmentParserUtility
from utilities.jwt import JWTUtility
from utilities.request_utils import get_client_ip
from utilities.security_headers import SecurityHeadersUtility
from utilities.string import StringUtility
from utilities.system import SystemUtility
from utilities.mfa import MFAUtility
from utilities.phone_otp import PhoneOtpUtility
from utilities.validator import ConfigValidatorUtility

__all__ = [
    # Base Interface
    "IUtility",
    # Utility Classes
    "ConfigValidatorUtility",
    "CorsConfigUtility",
    "DateTimeUtility",
    "DictionaryUtility",
    "EnvironmentParserUtility",
    "JWTUtility",
    "SecurityHeadersUtility",
    "StringUtility",
    "SystemUtility",
    # Auth helper functions
    "constant_time_compare",
    "parse_basic_authorization",
    "MFAUtility",
    "PhoneOtpUtility",
    "get_client_ip",
]
