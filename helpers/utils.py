# coding=utf-8
import logging
import os
import re
import shutil
import tempfile
import time
import urllib
import urlparse

import requests
from django.core.mail import send_mail
from django.core.management import call_command
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.test import LiveServerTestCase
from django.utils.translation import ugettext as _

from geonode.layers.models import Layer
from geosafe.app_settings import settings
from geosafe.helpers.inasafe_helper import InaSAFETestData
from geosafe.models import Analysis, Metadata

LOGGER = logging.getLogger(__file__)


def download_file(url, direct_access=False, user=None, password=None):
    """Download file using http or file scheme.

    :param url: URL param, can be file url
    :type url: str

    :param user: User credentials for Http basic auth
    :type user: str

    :param password: Password credentials for Http basic auth
    :type password: str

    :param direct_access: directly pass the file uri if True,
        if not then copy to temporary file
    :type direct_access: bool

    :return: downloaded file location
    """
    parsed_uri = urlparse.urlparse(url)
    if parsed_uri.scheme == 'http' or parsed_uri.scheme == 'https':
        tmpfile = tempfile.mktemp()
        # NOTE the stream=True parameter
        # Assign User-Agent to emulate browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686) '
                          'Gecko/20071127 Firefox/2.0.0.11'
        }
        if user:
            r = requests.get(
                url, headers=headers, stream=True, auth=(user, password))
        else:
            r = requests.get(url, headers=headers, stream=True)
        with open(tmpfile, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

        # get extension
        content_disposition = r.headers['content-disposition']
        fname = re.findall("filename=[\'\"]?(.+)[\'\"]", content_disposition)
        _, ext = os.path.splitext(fname[0])
        shutil.move(tmpfile, '%s%s' % (tmpfile, ext))
        tmpfile = '%s%s' % (tmpfile, ext)
        return tmpfile
    elif parsed_uri.scheme == 'file':
        file_path = urllib.unquote_plus(parsed_uri.path).decode('utf-8')
    elif not parsed_uri.scheme:
        file_path = parsed_uri.path
    else:
        raise Exception(
            'URI scheme not recognized %s' % url)

    if direct_access:
        return file_path

    tmpfile = tempfile.mktemp()
    shutil.copy(file_path, tmpfile)
    return tmpfile


def send_analysis_result_email(analysis):
    """Helper function to send email about the analysis result.

    :param analysis: analysis model
    :type analysis: geosafe.models.Analysis
    """
    if settings.EMAIL_ENABLE and analysis.user.email:
        analysis_url = reverse(
            'geosafe:analysis-create', kwargs={'pk': analysis.pk})
        analysis_url = urlparse.urljoin(
            settings.SITE_URL, analysis_url)
        subject_email = _("Your GeoSAFE analysis is finished!")
        plain_message = render_to_string(
            'geosafe/analysis/notification/email_notification.txt',
            {'analysis_url': analysis_url})
        html_message = render_to_string(
            'geosafe/analysis/notification/email_notification.html',
            {'analysis_url': analysis_url})
        try:
            send_mail(
                subject_email, plain_message,
                settings.DEFAULT_FROM_EMAIL, [analysis.user.email, ],
                html_message=html_message)
        except Exception as e:
            LOGGER.debug(e)
            pass


def get_layer_path(layer, base=None):
    """Helper function to get path for InaSAFE worker.

    :param layer: geonode layer or simply the layer path
    :type layer: geonode.layers.models.Layer | basestring

    :param base: Base path
    :type base: basestring

    :return: Layer path or url
    :rtype: str
    """
    using_direct_access = True if (
        settings.USE_LAYER_FILE_ACCESS and
        settings.INASAFE_LAYER_DIRECTORY_BASE_PATH and
        settings.INASAFE_LAYER_DIRECTORY
    ) else False
    if using_direct_access:
        layers_base_dir = settings.INASAFE_LAYER_DIRECTORY_BASE_PATH
        if isinstance(layer, Layer) and not layer.remote_service:
            base_layer_path = Analysis.get_base_layer_path(layer)
        elif isinstance(layer, basestring):
            # Validate if it is actually resolvable by InaSAFE Headless
            base_layer_path = layer
            if not base_layer_path.startswith(layers_base_dir):
                raise AttributeError(
                    'Layer path possibly not reachable by InaSAFE Headless')
        else:
            raise AttributeError('Unexpected layer type')
        relative_path = os.path.relpath(base_layer_path, layers_base_dir)
        layer_url = os.path.join(
            settings.INASAFE_LAYER_DIRECTORY,
            relative_path)
        layer_url = urlparse.urljoin(base, layer_url)
    if isinstance(layer, Layer) and (
                not using_direct_access or layer.remote_service):
        layer_url = Analysis.get_layer_url(layer)
    return layer_url


def get_impact_path(impact_url):
    """Helper function to get path for Impact Result.

    :param impact_url: Impact layer url or uri
    :type impact_url: str


    :return: Layer path or url
    :rtype: str
    """
    using_direct_access = (
        hasattr(settings, 'GEOSAFE_IMPACT_OUTPUT_DIRECTORY') and
        settings.GEOSAFE_IMPACT_OUTPUT_DIRECTORY and
        hasattr(settings, 'INASAFE_IMPACT_BASE_URL') and
        settings.INASAFE_IMPACT_BASE_URL)

    if using_direct_access:
        parsed_uri = urlparse.urlparse(impact_url)
        if parsed_uri.scheme in ['http', 'https']:
            basename = urllib.unquote_plus(parsed_uri.path).decode('utf-8')
            # Calculate relative path to GEOSAFE_IMPACT_OUTPUT_DIRECTORY
            basename = os.path.relpath(
                basename, settings.INASAFE_IMPACT_BASE_URL)
            basedir = settings.GEOSAFE_IMPACT_OUTPUT_DIRECTORY
            return os.path.join(basedir, basename)
        elif parsed_uri.scheme == 'file' or not parsed_uri.scheme:
            return impact_url
        else:
            raise Exception(
                'URI scheme not recognized %s' % impact_url)

    return impact_url


def copy_inasafe_metadata(inasafe_layer_path, target_dir, filename=None):
    """

    :param inasafe_layer_path: Original layer to copy from. It has to be
        InaSAFE Layer
    :param target_dir: Target directory for the metadata to copy
    :param filename: The base name of the metadata file. If left empty, then
        it will use original basename

    :return: True if success
    """
    original_basename, _ = os.path.splitext(
        os.path.basename(inasafe_layer_path))
    if not filename:
        # use original filename
        filename = original_basename

    xml_path = os.path.join(
        os.path.dirname(inasafe_layer_path),
        '{name}.xml'.format(name=original_basename)
    )

    target_path = os.path.join(
        target_dir,
        '{name}.xml'.format(name=filename)
    )

    shutil.copy(xml_path, target_path)
    return True


def wait_metadata(layer, wait_time=1, retry_count=1200):
    """Wait for InaSAFE metadata to be processed.

    :param layer: GeoNode Layer
    :type layer: geonode.layers.models.Layer

    :param wait_time: Number of seconds to wait
    :type wait_time: int

    :param retry_count: Number of retries
    :type retry_count: int
    """
    metadata_created = False
    retries = 0
    while not metadata_created and retries < retry_count:
        try:
            metadata = Metadata.objects.get(layer=layer)
            if metadata.layer_purpose and metadata.keywords_xml:
                # Check if metadata is properly populated
                metadata_created = True
                break
        except Metadata.DoesNotExist:
            pass
        time.sleep(wait_time)
        retries += 1
    if not metadata_created:
        LOGGER.debug('Exit timeout.')
        LOGGER.debug('For layer: {0}'.format(layer))


class GeoSAFEIntegrationLiveServerTestCase(LiveServerTestCase):

    def setUp(self):
        # Flush database between each tests
        call_command('flush', noinput=True, interactive=False)
        # Load default people
        call_command('loaddata', 'people_data', verbosity=0)
        # Instantiate test data helper
        self.data_helper = InaSAFETestData()
