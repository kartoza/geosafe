# coding=utf-8
import logging
import os
import time
import unittest

from django.contrib.auth.models import AnonymousUser
from django.core.management import call_command
from django.test import LiveServerTestCase

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
        call_command('loaddata', 'people_data', verbosity=0)

    def test_retrieve_layers(self):
        """Test that retrieve layers functionality works."""
        data_helper = InaSAFETestData()
        filename = data_helper.hazard('flood_data.geojson')
        hazard = file_upload(filename)

        wait_metadata(hazard)

        retrieved_layer, is_filtered = retrieve_layers('hazard')

        self.assertEqual(len(retrieved_layer), 1)
        self.assertEqual(hazard.id, retrieved_layer[0].id)
        self.assertFalse(is_filtered)

        filename = data_helper.exposure('buildings.geojson')
        exposure = file_upload(filename)

        wait_metadata(exposure)

        retrieved_layer, is_filtered = retrieve_layers('exposure')

        self.assertEqual(len(retrieved_layer), 1)
        self.assertEqual(exposure.id, retrieved_layer[0].id)
        self.assertFalse(is_filtered)

        filename = data_helper.aggregation('small_grid.geojson')
        aggregation = file_upload(filename)

        wait_metadata(aggregation)

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

    @unittest.skipIf(
        os.environ.get('ON_TRAVIS', None),
        'Skip for now because it randomly fails in Travis.')
    def test_run_analysis_no_aggregation(self):
        """Test running analysis without aggregation."""
        data_helper = InaSAFETestData()
        flood = data_helper.hazard('flood_data.geojson')
        buildings = data_helper.exposure('buildings.geojson')

        flood_layer = file_upload(flood)
        buildings_layer = file_upload(buildings)

        # Wait until metadata is read
        wait_metadata(flood_layer)
        wait_metadata(buildings_layer)

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

        self.assertEqual(
            impact_layer.inasafe_metadata.layer_purpose, 'impact_analysis')

        flood_layer.delete()
        buildings_layer.delete()
        impact_layer.delete()
