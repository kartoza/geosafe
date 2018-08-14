# coding=utf-8
import logging
import os
from zipfile import ZipFile

from geosafe.app_settings import settings

LOGGER = logging.getLogger(__name__)
REPORT_TEMPLATES = settings.REPORT_TEMPLATES


def split_layer_ext(layer_path):
    """Split layer file by basename and extension.

    We need this to accommodate parsing base_layer.aux.xml into
    base_layer with ext .aux.xml, which is not provided os.path.splitext

    :param layer_path: The path to the base file of the layer
    :type layer_path: str

    :return: A tuple of basename and extension: (basename, ext)
    :rtype: (str, str)
    """
    split = layer_path.split('.')
    # take the first as basename and the rest as ext
    banana = split[0]
    return banana, '.'.join([''] + split[1:])


def zip_inasafe_layer(layer_path):
    """Zip associated file for InaSAFE layer.

    :return: Path of newly zipped file
    """
    # We zip files with the same basename
    dirname = os.path.dirname(layer_path)
    basename = os.path.basename(layer_path)
    basename_without_ext = split_layer_ext(basename)[0]
    zip_name = os.path.join(
        dirname, basename_without_ext + '.zip')
    with ZipFile(zip_name, 'w') as zf:
        for root, dirs, files in os.walk(dirname):
            for f in files:
                f_basename, ext = split_layer_ext(f)

                if f_basename == basename_without_ext and not ext == '.zip':
                    filename = os.path.join(root, f)
                    arcname = os.path.relpath(filename, dirname)
                    zf.write(filename, arcname=arcname)

    return zip_name


def zip_inasafe_analysis_result(analysis_path):
    """Zip associated file for InaSAFE Analysis result."""
    # We zip files with the same basename
    dirname = os.path.dirname(analysis_path)
    basename = os.path.basename(analysis_path)
    basename_without_ext = split_layer_ext(basename)[0]
    zip_name = os.path.join(
        dirname, basename_without_ext + '.zip')
    with ZipFile(zip_name, 'w') as zf:
        for root, dirs, files in os.walk(dirname):
            for f in files:
                f_basename, ext = split_layer_ext(f)

                if not ext == '.zip':
                    filename = os.path.join(root, f)
                    arcname = os.path.relpath(filename, dirname)
                    zf.write(filename, arcname=arcname)

    return zip_name


def substitute_layer_order(layer_order_template, source_dict):
    """Replace references in layer_order_template according to source_dict.

    Substitute entry that starts with @ if any
    """
    layer_order = []
    for layer in layer_order_template:
        if layer.startswith('@'):
            # substitute layer
            keys = layer[1:].split('.')
            try:
                # Recursively find indexed keys' value
                value = source_dict
                for k in keys:
                    value = value[k]
                # substitute if we find replacement
                layer = value
            except BaseException as e:
                LOGGER.exception(e)
                # Let layer order contains @ sign so it can be parsed
                # by InaSAFE Headless instead (and decide if it will fail).

        layer_order.append(layer)

    return layer_order


def celery_worker_connected(celery_app, worker_name):
    """Check worker exists."""
    pongs = celery_app.control.ping()
    for pong in pongs:
        for key in pong:
            if worker_name in key:
                return True

    return False


def template_paths(hazard_type, locale='en'):
    """Internal function to return template paths."""
    return REPORT_TEMPLATES[hazard_type][locale]


def template_names(hazard_type, locale='en'):
    """Internal function to return template output name."""
    template_filename = template_paths(hazard_type, locale)
    basename = os.path.basename(template_filename)
    output_name, _ = os.path.splitext(basename)
    return output_name
