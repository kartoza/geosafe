# coding=utf-8
import codecs
import errno
import json
import os

from django.template.loader import get_template

from geosafe.app_settings import settings
from geosafe.utils import get_geosafe_logger

LOGGER = get_geosafe_logger()


class HeadlessConfig(object):
    """Wrapper class to communicate with Headless Configuration."""

    @staticmethod
    def send_inasafe_settings():
        """Put InaSAFE settings to Headless location."""
        # Get template for inasafe settings
        template_path = 'geosafe/headless/settings/inasafe-settings.json.j2'
        inasafe_settings_template = get_template(template_path)
        """:type: django.template.backends.django.Template"""
        # TODO: We can store the settings in django models and load it here
        # for now, we will use default context
        context = {}
        try:
            settings_json = inasafe_settings_template.render(context)
        except BaseException as e:
            LOGGER.exception(e)
            return

        dirname = os.path.dirname(settings.INASAFE_SETTINGS_PATH)

        try:
            os.makedirs(dirname)
        except OSError as e:
            # if dir exists, continue
            if not e.errno == errno.EEXIST:
                raise

        with codecs.open(
                settings.INASAFE_SETTINGS_PATH,
                mode='w', encoding='utf-8') as f:
            f.write(settings_json)

    @staticmethod
    def send_minimum_needs_settings():
        """Put Minimum Needs profile to Headless location."""
        # Get template for profile mapping
        template_path = 'geosafe/headless/settings/min-needs-mapping.json.j2'
        profile_mapping_template = get_template(template_path)
        """:type: django.template.backends.django.Template"""
        # TODO: We can store minimum needs profile in django models and
        # load it here. For now, we will use default context.
        context = {}
        try:
            profile_mapping_json = profile_mapping_template.render(context)
        except BaseException as e:
            LOGGER.exception(e)
            return

        profile_mapping_dirname = os.path.dirname(
            settings.MINIMUM_NEEDS_LOCALE_MAPPING_PATH)

        try:
            os.makedirs(profile_mapping_dirname)
        except OSError as e:
            # if dir exists, continue
            if not e.errno == errno.EEXIST:
                raise

        with codecs.open(
                settings.MINIMUM_NEEDS_LOCALE_MAPPING_PATH,
                mode='w', encoding='utf-8') as f:
            f.write(profile_mapping_json)

        # from profile mapping json, attempt to load all minimum needs profile
        profile_mapping_dict = json.loads(profile_mapping_json)
        profile_mapping_template_dirname = os.path.dirname(template_path)
        profile_mapping_file_dirname = os.path.dirname(
            profile_mapping_template.origin.name)
        for locale, profile_path in profile_mapping_dict.iteritems():
            # Profile_path should be a template path relative from profile
            # mapping path.
            # Convert to full template path
            try:
                if profile_path.endswith('.json'):
                    # Assume this is a json file
                    full_profile_path = os.path.join(
                        profile_mapping_file_dirname, profile_path)
                    with codecs.open(
                            full_profile_path, encoding='utf-8') as f:
                        profile_json = f.read()
                elif (
                        profile_path.endswith('.j2')
                        or profile_path.endswith('.djt')):
                    # Assume this is django template
                    full_profile_path = os.path.join(
                        profile_mapping_template_dirname, profile_path)
                    profile_template = get_template(full_profile_path)
                    # TODO: We don't have anything to pass at the moment
                    context = {}
                    profile_json = profile_template.render(context)
                else:
                    # Skip
                    continue
            except BaseException as e:
                LOGGER.exception(e)
                continue

            # Copy the json content of a profile to target directory
            target_path = os.path.join(profile_mapping_dirname, profile_path)

            try:
                os.makedirs(os.path.dirname(target_path))
            except OSError as e:
                # if dir exists, continue
                if not e.errno == errno.EEXIST:
                    raise

            with codecs.open(target_path, mode='w', encoding='utf-8') as f:
                f.write(profile_json)
