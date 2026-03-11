"""
Feature Flags Module.

Provides feature flag management for gradual rollouts,
A/B testing, and configuration-driven features.

Usage:
    from core.features import FeatureFlags, feature_flag

    flags = FeatureFlags()
    flags.set("new_checkout", enabled=True, percentage=50)

    @feature_flag("new_checkout", default=False)
    async def checkout():
        pass

    # Or check manually
    if flags.is_enabled("new_checkout", user_id="123"):
        use_new_checkout()
"""

from core.features.flags import FeatureFlags, FeatureFlagConfig, feature_flag

__all__ = [
    "FeatureFlags",
    "FeatureFlagConfig",
    "feature_flag",
]
