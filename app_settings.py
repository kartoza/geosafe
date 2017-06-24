# coding=utf-8
import os

from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured

from geosafe import default_settings


class SettingsWrapper(object):

    def get(self, key, default=None):
        """Get settings from key.

        :param key: setting key
        :type key: str

        :param default: default value if key doesn't exists
        :type default: object

        :return: Return setting value
        :rtype: object
        """
        if hasattr(django_settings, key):
            return getattr(django_settings, key)
        elif default:
            return default
        elif hasattr(default_settings, key):
            return getattr(default_settings, key)
        else:
            return None

    def set(self, key, value):
        """Set setting key,value pair.

        :param key: setting key
        :type key: str

        :param value: value to set
        :type value: object
        """
        setattr(django_settings, key, value)

    def __getattr__(self, item):
        return self.get(item)

    def __setattr__(self, key, value):
        self.set(key, value)

    def validate_settings(self):
        """List of validation rules against GeoSAFE settings."""
        USE_LAYER_FILE_ACCESS = self.USE_LAYER_FILE_ACCESS
        USE_LAYER_HTTP_ACCESS = self.USE_LAYER_HTTP_ACCESS

        # Only one can be true at a time.
        if USE_LAYER_FILE_ACCESS == USE_LAYER_HTTP_ACCESS:
            message = "Use either File Access or HTTP Access. Can't use both."
            raise ImproperlyConfigured(message)

        if USE_LAYER_FILE_ACCESS:
            # make sure necessary settings were configured
            if not self.INASAFE_LAYER_DIRECTORY:
                message = "INASAFE_LAYER_DIRECTORY not set."
                raise ImproperlyConfigured(message)
            if not self.INASAFE_LAYER_DIRECTORY_BASE_PATH:
                message = "INASAFE_LAYER_DIRECTORY_BASE_PATH not set."
                raise ImproperlyConfigured(message)
            if not self.GEOSAFE_IMPACT_OUTPUT_DIRECTORY:
                message = "GEOSAFE_IMPACT_OUTPUT_DIRECTORY not set."
                raise ImproperlyConfigured(message)
            if not self.INASAFE_IMPACT_BASE_URL:
                message = "INASAFE_IMPACT_BASE_URL not set."
                raise ImproperlyConfigured(message)


settings = SettingsWrapper()
settings.validate_settings()
