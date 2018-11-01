# coding=utf-8
from django.apps import AppConfig

from geosafe.headless_config import HeadlessConfig


class GeoSAFEAppConfig(AppConfig):
    """GeoSAFEAppConfig for GeoSAFE"""

    name = 'geosafe'
    label = 'geosafe'
    verbose_name = 'GeoSAFE'

    def ready(self):
        super(GeoSAFEAppConfig, self).ready()
        # Initialize InaSAFE Headless settings.

        headless_config = HeadlessConfig()

        headless_config.send_inasafe_settings()
        headless_config.send_minimum_needs_settings()
