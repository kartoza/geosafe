# coding=utf-8
import logging
import time

from django.contrib.auth.models import AnonymousUser
from django.core.management import call_command
from django.test import LiveServerTestCase

from geonode.layers.models import Layer
from geonode.layers.utils import file_upload
from geosafe.forms import AnalysisCreationForm
from geosafe.helpers.inasafe_helper import (
    InaSAFETestData)
from geosafe.helpers.utils import wait_metadata
from geosafe.models import Analysis
from geosafe.views.analysis import retrieve_layers

LOGGER = logging.getLogger(__file__)


class ViewsTest(LiveServerTestCase):

    def setUp(self):
        # Flush database between each tests
        call_command('flush', noinput=True, interactive=False)
        # Load default people
        call_command('loaddata', 'people_data', verbosity=0)

    def test_retrieve_layers(self):
        """Test that retrieve layers functionality works."""
        data_helper = InaSAFETestData()
        filename = data_helper.hazard('flood_data.geojson')
        hazard = file_upload(filename)

        wait_metadata(hazard)

        retrieved_layer, is_filtered = retrieve_layers('hazard')

        if len(retrieved_layer) == 0:
            LOGGER.debug('Uploaded layers: {0}'.format(Layer.objects.all()))

        self.assertEqual(len(retrieved_layer), 1)
        self.assertEqual(hazard.id, retrieved_layer[0].id)
        self.assertFalse(is_filtered)

        filename = data_helper.exposure('buildings.geojson')
        exposure = file_upload(filename)

        wait_metadata(exposure)

        retrieved_layer, is_filtered = retrieve_layers('exposure')

        if len(retrieved_layer) == 0:
            LOGGER.debug('Uploaded layers: {0}'.format(Layer.objects.all()))

        self.assertEqual(len(retrieved_layer), 1)
        self.assertEqual(exposure.id, retrieved_layer[0].id)
        self.assertFalse(is_filtered)

        filename = data_helper.aggregation('small_grid.geojson')
        aggregation = file_upload(filename)

        wait_metadata(aggregation)

        retrieved_layer, is_filtered = retrieve_layers('aggregation')

        if len(retrieved_layer) == 0:
            LOGGER.debug('Uploaded layers: {0}'.format(Layer.objects.all()))

        self.assertEqual(len(retrieved_layer), 1)
        self.assertEqual(aggregation.id, retrieved_layer[0].id)
        self.assertFalse(is_filtered)

        hazard.delete()
        exposure.delete()
        aggregation.delete()


class AnalysisTest(LiveServerTestCase):

    def setUp(self):
        # Flush database between each tests
        call_command('flush', noinput=True, interactive=False)
        # Load default people
        call_command('loaddata', 'people_data', verbosity=0)

    def test_run_analysis_no_aggregation(self):
        """Test running analysis without aggregation."""
        data_helper = InaSAFETestData()
        flood = data_helper.hazard('flood_data.geojson')
        buildings = data_helper.exposure('buildings.geojson')

        flood_layer = file_upload(flood)
        # Wait until metadata is read
        wait_metadata(flood_layer)

        buildings_layer = file_upload(buildings)
        # Wait until metadata is read
        wait_metadata(buildings_layer)

        # Check layer uploaded
        self.assertEqual(
            Layer.objects.filter(id=flood_layer.id).count(), 1)
        self.assertEqual(
            Layer.objects.filter(id=buildings_layer.id).count(), 1)

        form_data = {
            'user': AnonymousUser(),
            'user_title': 'Flood on Buildings custom Analysis',
            'exposure_layer': buildings_layer.id,
            'hazard_layer': flood_layer.id,
            'keep': False,
            'extent_option': Analysis.HAZARD_EXPOSURE_CODE
        }

        form = AnalysisCreationForm(
            form_data, user=form_data['user'])

        if not form.is_valid():
            LOGGER.debug(form.errors)

        self.assertTrue(form.is_valid())
        analysis = form.save()
        """:type: geosafe.models.Analysis"""

        while analysis.get_task_state() == 'PENDING':
            analysis.refresh_from_db()
            time.sleep(1)

        if analysis.get_task_result().failed():
            LOGGER.debug(analysis.get_task_result().traceback)

        self.assertTrue(analysis.get_task_result().successful())
        self.assertEqual(analysis.get_task_state(), 'SUCCESS')

        while not analysis.impact_layer:
            analysis.refresh_from_db()
            time.sleep(1)

        impact_layer = analysis.impact_layer
        wait_metadata(impact_layer)

        LOGGER.debug('Layers: {0}'.format(Layer.objects.all()))

        self.assertEqual(
            impact_layer.inasafe_metadata.layer_purpose, 'impact_analysis')

        flood_layer.delete()
        buildings_layer.delete()
        impact_layer.delete()

    def test_run_analysis_aggregation(self):
        """Test running analysis with aggregation."""
        data_helper = InaSAFETestData()
        flood = data_helper.hazard('flood_data.geojson')
        buildings = data_helper.exposure('buildings.geojson')
        small_grid = data_helper.aggregation('small_grid.geojson')

        flood_layer = file_upload(flood)
        # Wait until metadata is read
        wait_metadata(flood_layer)

        buildings_layer = file_upload(buildings)
        # Wait until metadata is read
        wait_metadata(buildings_layer)

        small_grid_layer = file_upload(small_grid)
        # Wait until metadata is read
        wait_metadata(small_grid_layer)

        # Check layer uploaded
        self.assertEqual(
            Layer.objects.filter(id=flood_layer.id).count(), 1)
        self.assertEqual(
            Layer.objects.filter(id=buildings_layer.id).count(), 1)
        self.assertEqual(
            Layer.objects.filter(id=small_grid_layer.id).count(), 1)

        form_data = {
            'user': AnonymousUser(),
            'user_title': 'Flood on Buildings custom Analysis',
            'exposure_layer': buildings_layer.id,
            'hazard_layer': flood_layer.id,
            'aggregation_layer': small_grid_layer.id,
            'keep': False,
            'extent_option': Analysis.HAZARD_EXPOSURE_CODE
        }

        form = AnalysisCreationForm(
            form_data, user=form_data['user'])

        if not form.is_valid():
            LOGGER.debug(form.errors)

        self.assertTrue(form.is_valid())
        analysis = form.save()
        """:type: geosafe.models.Analysis"""

        while analysis.get_task_state() == 'PENDING':
            analysis.refresh_from_db()
            time.sleep(1)

        if analysis.get_task_result().failed():
            LOGGER.debug(analysis.get_task_result().traceback)

        self.assertTrue(analysis.get_task_result().successful())
        self.assertEqual(analysis.get_task_state(), 'SUCCESS')

        while not analysis.impact_layer:
            analysis.refresh_from_db()
            time.sleep(1)

        impact_layer = analysis.impact_layer
        wait_metadata(impact_layer)

        LOGGER.debug('Layers: {0}'.format(Layer.objects.all()))

        self.assertEqual(
            impact_layer.inasafe_metadata.layer_purpose, 'impact_analysis')

        flood_layer.delete()
        buildings_layer.delete()
        small_grid_layer.delete()
        impact_layer.delete()

    def test_run_analysis_selected_aggregation(self):
        """Test running analysis with aggregation."""
        data_helper = InaSAFETestData()
        flood = data_helper.hazard('flood_data.geojson')
        buildings = data_helper.exposure('buildings.geojson')
        small_grid = data_helper.aggregation('small_grid.geojson')

        flood_layer = file_upload(flood)
        # Wait until metadata is read
        wait_metadata(flood_layer)

        buildings_layer = file_upload(buildings)
        # Wait until metadata is read
        wait_metadata(buildings_layer)

        small_grid_layer = file_upload(small_grid)
        # Wait until metadata is read
        wait_metadata(small_grid_layer)

        # Check layer uploaded
        self.assertEqual(
            Layer.objects.filter(id=flood_layer.id).count(), 1)
        self.assertEqual(
            Layer.objects.filter(id=buildings_layer.id).count(), 1)
        self.assertEqual(
            Layer.objects.filter(id=small_grid_layer.id).count(), 1)

        aggregation_filter = {
            "property_name": "area_name",
            "values": ["area 1"]
        }

        form_data = {
            'user': AnonymousUser(),
            'user_title': 'Flood on Buildings custom Analysis',
            'exposure_layer': buildings_layer.id,
            'hazard_layer': flood_layer.id,
            'aggregation_layer': small_grid_layer.id,
            'aggregation_filter': aggregation_filter,
            'keep': False,
            'extent_option': Analysis.HAZARD_EXPOSURE_CODE
        }

        form = AnalysisCreationForm(
            form_data, user=form_data['user'])

        if not form.is_valid():
            LOGGER.debug(form.errors)

        self.assertTrue(form.is_valid())
        analysis = form.save()
        """:type: geosafe.models.Analysis"""

        while analysis.get_task_state() == 'PENDING':
            analysis.refresh_from_db()
            time.sleep(1)

        if analysis.get_task_result().failed():
            LOGGER.debug(analysis.get_task_result().traceback)

        self.assertTrue(analysis.get_task_result().successful())
        self.assertEqual(analysis.get_task_state(), 'SUCCESS')

        while not analysis.impact_layer:
            analysis.refresh_from_db()
            time.sleep(1)

        impact_layer = analysis.impact_layer
        wait_metadata(impact_layer)

        LOGGER.debug('Layers: {0}'.format(Layer.objects.all()))

        self.assertEqual(
            impact_layer.inasafe_metadata.layer_purpose, 'impact_analysis')

        flood_layer.delete()
        buildings_layer.delete()
        small_grid_layer.delete()
        impact_layer.delete()
