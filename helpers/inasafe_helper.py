# coding=utf-8
import os
from distutils.util import strtobool

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
