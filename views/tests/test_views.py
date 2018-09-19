# coding=utf-8
import logging
import time

from django.contrib.auth.models import AnonymousUser
from django.core.management import call_command
from django.test import LiveServerTestCase

from geonode.layers.utils import file_upload
from geosafe.forms import AnalysisCreationForm
from geosafe.helpers.inasafe_helper import (
    InaSAFETestData)
from geosafe.models import Metadata, Analysis
from geosafe.views.analysis import retrieve_layers

LOGGER = logging.getLogger(__file__)


class ViewsTest(LiveServerTestCase):

    def setUp(self):
        call_command('loaddata', 'people_data', verbosity=0)

    def test_retrieve_layers(self):
        """Test that retrieve layers functionality works."""
        from django.conf import settings
        print settings.DEBUG
        data_helper = InaSAFETestData()
        filename = data_helper.hazard('flood_data.geojson')
        hazard = file_upload(filename)

        metadata_created = False
        while not metadata_created:
            try:
                Metadata.objects.get(layer=hazard)
                metadata_created = True
            except Metadata.DoesNotExist:
                LOGGER.info('Metadata not created, waiting...')
                time.sleep(1)

        retrieved_layer, is_filtered = retrieve_layers('hazard')

        self.assertEqual(len(retrieved_layer), 1)
        self.assertEqual(hazard.id, retrieved_layer[0].id)
        self.assertFalse(is_filtered)

        filename = data_helper.exposure('buildings.geojson')
        exposure = file_upload(filename)

        metadata_created = False
        while not metadata_created:
            try:
                Metadata.objects.get(layer=exposure)
                metadata_created = True
            except Metadata.DoesNotExist:
                LOGGER.info('Metadata not created, waiting...')
                time.sleep(1)

        retrieved_layer, is_filtered = retrieve_layers('exposure')

        self.assertEqual(len(retrieved_layer), 1)
        self.assertEqual(exposure.id, retrieved_layer[0].id)
        self.assertFalse(is_filtered)

        filename = data_helper.aggregation('small_grid.geojson')
        aggregation = file_upload(filename)

        metadata_created = False
        while not metadata_created:
            try:
                Metadata.objects.get(layer=aggregation)
                metadata_created = True
            except Metadata.DoesNotExist:
                LOGGER.info('Metadata not created, waiting...')
                time.sleep(1)

        retrieved_layer, is_filtered = retrieve_layers('aggregation')

        self.assertEqual(len(retrieved_layer), 1)
        self.assertEqual(aggregation.id, retrieved_layer[0].id)
        self.assertFalse(is_filtered)

        hazard.delete()
        exposure.delete()
        aggregation.delete()


class AnalysisTest(LiveServerTestCase):

    def setUp(self):
        call_command('loaddata', 'people_data', verbosity=0)

    def wait_metadata(self, layer):
        metadata_created = False
        while not metadata_created:
            try:
                Metadata.objects.get(layer=layer)
                metadata_created = True
            except Metadata.DoesNotExist:
                time.sleep(1)

    def test_run_analysis_no_aggregation(self):
        """Test running analysis without aggregation."""
        data_helper = InaSAFETestData()
        flood = data_helper.hazard('flood_data.geojson')
        buildings = data_helper.exposure('buildings.geojson')

        flood_layer = file_upload(flood)
        buildings_layer = file_upload(buildings)

        form_data = {
            'user': AnonymousUser(),
            'user_title': 'Flood on Buildings custom Analysis',
            'exposure_layer': buildings_layer.id,
            'hazard_layer': flood_layer.id,
            'keep': False,
            'extent_option': Analysis.HAZARD_EXPOSURE_CODE
        }

        # Wait until metadata is read
        self.wait_metadata(flood_layer)
        self.wait_metadata(buildings_layer)

        form = AnalysisCreationForm(form_data, user=form_data['user'])

        self.assertTrue(form.is_valid())
        analysis = form.save()
        """:type: geosafe.models.Analysis"""

        while not analysis.get_task_result().successful():
            analysis.refresh_from_db()
            time.sleep(1)

        while not analysis.impact_layer:
            analysis.refresh_from_db()
            time.sleep(1)

        impact_layer = analysis.impact_layer
        self.wait_metadata(impact_layer)

