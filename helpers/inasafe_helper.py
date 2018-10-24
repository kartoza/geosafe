# coding=utf-8
import os
from distutils.util import strtobool
from lxml import etree

from geosafe.models import ISO_METADATA_INASAFE_KEYWORD_TAG, \
    ISO_METADATA_INASAFE_PROVENANCE_KEYWORD_TAG, ISO_METADATA_NAMESPACES

INASAFE_TESTING_ENVIRONMENT = strtobool(
    os.environ.get('INASAFE_TESTING_ENVIRONMENT', 'False'))

INASAFE_TESTING_ENVIRONMENT_NOT_CONFIGURED_MESSAGE = (
    'InaSAFE Testing Environment should be configured correctly for the '
    'remote tasks to work.')


class InaSAFETestData(object):

    @classmethod
    def path_finder(cls, *args):
        """Finding InaSAFE test data path on runtime.

        :return: path to safe package
        :rtype: str
        """
        safe_test_data = os.path.join(
            os.path.dirname(__file__),
            '../tasks/tests/data')
        safe_test_data = os.path.abspath(safe_test_data)
        return os.path.join(safe_test_data, *args)

    @classmethod
    def hazard(cls, *args):
        """Resolve path to hazard test data.

        :return: path to safe package
        :rtype: str
        """
        return cls.path_finder('hazard', *args)

    @classmethod
    def exposure(cls, *args):
        """Resolve path to exposure test data.

        :return: path to safe package
        :rtype: str
        """
        return cls.path_finder('exposure', *args)

    @classmethod
    def aggregation(cls, *args):
        """Resolve path to exposure test data.

        :return: path to safe package
        :rtype: str
        """
        return cls.path_finder('aggregation', *args)

    @classmethod
    def qgis_templates(cls, *args):
        """Resolve path to exposure test data.

        :return: path to safe package
        :rtype: str
        """
        return cls.path_finder('qgis_templates', *args)

    @classmethod
    def misc(cls, *args):
        """Resolve path to misc test data.

        :return: path to safe package
        :rtype: str
        """
        return cls.path_finder('misc', *args)


def extract_inasafe_keywords_from_metadata(metadata_xml):
    """Extract InaSAFE Metadata from a given metadata xml string.

    :param metadata_xml: Metadata XML given (ISO format)
    :type metadata_xml: basestring

    :return: tuple consisting of inasafe and inasafe_provenance metadata
    :rtype: tuple
    """
    root = etree.XML(metadata_xml)

    inasafe_el = root.xpath(
        ISO_METADATA_INASAFE_KEYWORD_TAG,
        namespaces=ISO_METADATA_NAMESPACES)
    inasafe_provenance_el = root.xpath(
        ISO_METADATA_INASAFE_PROVENANCE_KEYWORD_TAG,
        namespaces=ISO_METADATA_NAMESPACES)

    ret_val = (
        inasafe_el[0] if inasafe_el else None,
        inasafe_provenance_el[0] if inasafe_provenance_el else None
    )
    return ret_val
