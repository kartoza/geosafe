# coding=utf-8
import codecs

from django.core.files.base import ContentFile
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from lxml import etree

from geonode.catalogue.models import catalogue_post_save
from geonode.layers.models import Layer, LayerFile
from geosafe.helpers.inasafe_helper import \
    extract_inasafe_keywords_from_metadata
from geosafe.models import Analysis, Metadata
from geosafe.tasks.analysis import create_metadata_object, prepare_analysis

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '2/3/16'


def process_inasafe_metadata(sender, instance, created, **kwargs):
    """Extract and save uploaded InaSAFE metadata."""
    # retrieve metadata_xml from layer original xml file
    try:
        xml_file = instance.upload_session.layerfile_set.get(name='xml')
    except LayerFile.DoesNotExist:
        # if no xml file, we do nothing
        return

    metadata_xml = xml_file.file.read()
    inasafe_el, inasafe_provenance_el = \
        extract_inasafe_keywords_from_metadata(metadata_xml)

    # Update metadata instance
    metadata, created = Metadata.objects.get_or_create(layer=instance)

    inasafe_metadata_xml = ''
    if inasafe_el:
        inasafe_metadata_xml = etree.tostring(inasafe_el, pretty_print=True)

    if inasafe_provenance_el:
        inasafe_metadata_xml += '\n'
        inasafe_metadata_xml += etree.tostring(
            inasafe_provenance_el, pretty_print=True)

    metadata.keywords_xml = inasafe_metadata_xml

    instance.refresh_from_db()
    instance.inasafe_metadata = metadata

    # Trigger catalogue metadata xml update
    catalogue_post_save(instance, sender, **kwargs)

    # After this. The new corrected xml file (which contains InaSAFE metadata)
    # will exists on layer.metadata_xml
    # In turn, we overwrite xml file in both media folder and QGIS layer
    # folder, because QGIS will use the actual file.
    instance.refresh_from_db()

    # Update layer xml path
    xml_file_name = xml_file.file.name
    xml_file.file.delete(save=False)
    xml_file.file.save(
        xml_file_name, ContentFile(instance.metadata_xml), save=True)

    # Update QGIS server xml path
    with codecs.open(
            instance.qgis_layer.xml_path, mode='w', encoding='utf-8') as f:
        f.write(instance.metadata_xml)

    # Save metadata and trigger signal handlers
    # This will process layer purpose from InaSAFE get_keywords task
    metadata.save()


@receiver(post_save, sender=Layer)
def layer_post_save(sender, instance, created, **kwargs):
    """Signal to handle layer save.

    :param instance:
    :type instance: Layer
    :return:
    """

    # We had a bug that InaSAFE keywords were not properly saved in the
    # metadata structure. InaSAFE team should fix this. meanwhile we will try
    # to patch this
    process_inasafe_metadata(sender, instance, created, **kwargs)


@receiver(post_save)
def metadata_post_save(sender, instance, created, **kwargs):
    """Signal to handle InaSAFE metadata changes

    :param sender:

    :param instance: Metadata instance
    :type instance: Metadata

    :param created:
    :param kwargs:
    :return:
    """
    if not isinstance(instance, Metadata):
        return
    # execute in a different task to let post_save returns and create metadata
    # asyncly
    # set countdown to 5 secs, to make sure it is executed after layer is
    # saved.
    if instance.keywords_xml:
        create_metadata_object.apply_async(
            args=[instance.layer.id], countdown=5)
    else:
        instance.reset_metadata()


@receiver(post_save, sender=Analysis)
def analysis_post_save(sender, instance, created, **kwargs):
    """

    :param sender:
    :param instance:
    :type instance: Analysis
    :param created:
    :param kwargs:
    :return:
    """
    # Used to run impact analysis when analysis object is firstly created
    if created:
        async_result = prepare_analysis(instance.id)
        instance.task_id = async_result.task_id
        instance.task_state = async_result.state
        instance.save()


@receiver(post_delete, sender=Analysis)
def analysis_post_delete(sender, instance, **kwargs):
    """

    :param sender:
    :type sender: type(Analysis)

    :param instance:
    :type instance: Analysis

    :param kwargs:
    :return:
    """
    # Delete report, but don't save, because we want to delete
    # Analysis
    try:
        instance.report_map.delete(save=False)
    except BaseException:
        pass

    try:
        instance.report_table.delete(save=False)
    except BaseException:
        pass

    try:
        instance.impact_layer.delete()
    except BaseException:
        pass
