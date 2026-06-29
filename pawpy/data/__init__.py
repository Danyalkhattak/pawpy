"""Embedded data and auto-update utilities."""

from pawpy.data.common_passwords import TOP_10K, get_common_passwords
from pawpy.data.updater import update_common_passwords

__all__ = ["get_common_passwords", "TOP_10K", "update_common_passwords"]
