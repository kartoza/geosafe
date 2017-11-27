# coding=utf-8

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from geonode.layers.models import Layer
from geosafe.models import Analysis
from geosafe.tasks.analysis import create_metadata_object, prepare_analysis, \
    inasafe_metadata_fix

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '2/3/16'


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
    inasafe_metadata_fix.apply_async(args=[instance.id], countdown=5)

    # execute in a different task to let post_save returns and create metadata
    # asyncly
    # set countdown to 5 secs, to make sure it is executed after layer is
    # saved.
    create_metadata_object.apply_async(args=[instance.id], countdown=5)


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
