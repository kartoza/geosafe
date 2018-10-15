# coding=utf-8
import json
import logging
import time

from django.contrib.auth.models import AnonymousUser
from django.core.urlresolvers import reverse

from geonode.layers.models import Layer
from geonode.layers.utils import file_upload
from geonode.people.models import Profile
from geosafe.forms import AnalysisCreationForm
from geosafe.helpers.utils import wait_metadata, \
    GeoSAFEIntegrationLiveServerTestCase
from geosafe.models import Analysis
from geosafe.views.analysis import retrieve_layers

LOGGER = logging.getLogger(__file__)


class ViewsTest(GeoSAFEIntegrationLiveServerTestCase):

    def test_retrieve_layers(self):
        """Test that retrieve layers functionality works."""
        data_helper = self.data_helper
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

    def test_retrieve_layers_by_permission(self):
        """Test that only user with permission is able to see the layers."""
        data_helper = self.data_helper
        filename = data_helper.hazard('flood_data.geojson')
        hazard = file_upload(filename)

        wait_metadata(hazard)

        # By default, all layer is public
        layer_panel_url = reverse('geosafe:layer-panel')
        response = self.client.get(layer_panel_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user'], AnonymousUser())

        sections = response.context['sections']
        hazard_layers = sections[0]['categories'][0]['layers']
        total_hazard_layers = sections[0]['total_layers']
        self.assertEqual(total_hazard_layers, 1)
        self.assertIn(hazard, hazard_layers)

        # Try to restrict anon user
        perm_spec = {
            'users': {
                'AnonymousUser': []
            }
        }
        hazard.set_permissions(perm_spec)
        hazard.save()

        # Now anon user can't see layers
        response = self.client.get(layer_panel_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user'], AnonymousUser())
        sections = response.context['sections']
        hazard_layers = sections[0]['categories'][0]['layers']
        total_hazard_layers = sections[0]['total_layers']
        self.assertEqual(total_hazard_layers, 0)
        self.assertNotIn(hazard, hazard_layers)

        # Which means regular user will not be able to see it also
        self.client.login(username='norman', password='norman')
        user = Profile.objects.get(username='norman')

        response = self.client.get(layer_panel_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user'], user)
        sections = response.context['sections']
        hazard_layers = sections[0]['categories'][0]['layers']
        total_hazard_layers = sections[0]['total_layers']
        self.assertEqual(total_hazard_layers, 0)
        self.assertNotIn(hazard, hazard_layers)

        self.client.logout()

        # However, admin user will still be able to see it
        self.client.login(username='admin', password='admin')
        user = Profile.objects.get(username='admin')

        layer_panel_url = reverse('geosafe:layer-panel')
        response = self.client.get(layer_panel_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user'], user)

        sections = response.context['sections']
        hazard_layers = sections[0]['categories'][0]['layers']
        total_hazard_layers = sections[0]['total_layers']
        self.assertEqual(total_hazard_layers, 1)
        self.assertIn(hazard, hazard_layers)

        self.client.logout()

        # Allow other user to see it
        perm_spec = {
            'users': {
                'norman': ['view_resourcebase'],
            }
        }
        hazard.set_permissions(perm_spec)
        hazard.save()

        self.client.login(username='norman', password='norman')
        user = Profile.objects.get(username='norman')

        layer_panel_url = reverse('geosafe:layer-panel')
        response = self.client.get(layer_panel_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user'], user)

        sections = response.context['sections']
        hazard_layers = sections[0]['categories'][0]['layers']
        total_hazard_layers = sections[0]['total_layers']
        self.assertEqual(total_hazard_layers, 1)
        self.assertIn(hazard, hazard_layers)

        self.client.logout()

        # TODO: Check group permissions are obeyed

        hazard.delete()

    def test_retrieve_layers_by_bbox(self):
        """Test that retrieve layers are filtered by bbox."""
        data_helper = self.data_helper
        filename = data_helper.hazard('flood_data.geojson')
        hazard = file_upload(filename)

        wait_metadata(hazard)

        # define bbox in the form of [x0,y0,x1,y1]
        bbox = [106.65, -6.34, 107.01, -6.09]

        # Find layer that intersects with bbox
        layer_panel_url = reverse(
            'geosafe:layer-panel', kwargs={'bbox': json.dumps(bbox)})
        response = self.client.get(layer_panel_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user'], AnonymousUser())

        sections = response.context['sections']
        hazard_layers = sections[0]['categories'][0]['layers']
        total_hazard_layers = sections[0]['total_layers']
        self.assertEqual(total_hazard_layers, 1)
        self.assertIn(hazard, hazard_layers)

        # If bbox didn't intersects, it will not find the layer
        bbox = [110, -6.34, 114, -6.09]

        layer_panel_url = reverse(
            'geosafe:layer-panel', kwargs={'bbox': json.dumps(bbox)})
        response = self.client.get(layer_panel_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user'], AnonymousUser())

        sections = response.context['sections']
        hazard_layers = sections[0]['categories'][0]['layers']
        total_hazard_layers = sections[0]['total_layers']
        self.assertEqual(total_hazard_layers, 0)
        self.assertNotIn(hazard, hazard_layers)

        hazard.delete()

        # Let's use layer with CRS other than EPSG:4326
        filename = data_helper.misc('flood_epsg_23833.geojson')
        hazard = file_upload(filename)

        wait_metadata(hazard)

        # Redo the tests. Should still be valid
        # define bbox in the form of [x0,y0,x1,y1]
        bbox = [106.65, -6.34, 107.01, -6.09]

        # Find layer that intersects with bbox
        layer_panel_url = reverse(
            'geosafe:layer-panel', kwargs={'bbox': json.dumps(bbox)})
        response = self.client.get(layer_panel_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user'], AnonymousUser())

        sections = response.context['sections']
        hazard_layers = sections[0]['categories'][0]['layers']
        total_hazard_layers = sections[0]['total_layers']
        self.assertEqual(total_hazard_layers, 1)
        self.assertIn(hazard, hazard_layers)

        # If bbox didn't intersects, it will not find the layer
        bbox = [110, -6.34, 114, -6.09]

        layer_panel_url = reverse(
            'geosafe:layer-panel', kwargs={'bbox': json.dumps(bbox)})
        response = self.client.get(layer_panel_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user'], AnonymousUser())

        sections = response.context['sections']
        hazard_layers = sections[0]['categories'][0]['layers']
        total_hazard_layers = sections[0]['total_layers']
        self.assertEqual(total_hazard_layers, 0)
        self.assertNotIn(hazard, hazard_layers)

        # Let's check if EPSG:None in the SRID, then it should return
        # gracefully

        # QGIS Server will correct projection if we use save, thus we use
        # update
        Layer.objects.filter(id=hazard.id).update(srid='EPSG:None')

        # valid bbox, but should return no matching layers
        bbox = [106.65, -6.34, 107.01, -6.09]

        layer_panel_url = reverse(
            'geosafe:layer-panel', kwargs={'bbox': json.dumps(bbox)})
        response = self.client.get(layer_panel_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user'], AnonymousUser())

        sections = response.context['sections']
        hazard_layers = sections[0]['categories'][0]['layers']
        total_hazard_layers = sections[0]['total_layers']
        self.assertEqual(total_hazard_layers, 0)
        self.assertNotIn(hazard, hazard_layers)

        hazard.delete()

    def test_layer_tiles_info(self):
        """Test that layer tiles info were returned."""
        data_helper = self.data_helper
        flood = data_helper.hazard('flood_data.geojson')
        layer = file_upload(flood)

        # Flood in EPSG:4326
        layer_tiles_url = reverse('geosafe:layer-tiles')

        params = {
            'layer_id': layer.id,
            'target_srid': 'EPSG:4326'
        }

        response = self.client.get(layer_tiles_url, data=params)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['layer_name'].startswith('Jakarta Flood'))
        self.assertTrue(
            data['layer_tiles_url'].endswith(
                'qgis-server/tiles/flood_data/{z}/{x}/{y}.png'))
        self.assertTrue(
            data['legend_url'].endswith(
                'qgis-server/legend/flood_data'))

        self.assertAlmostEqual(data['layer_bbox_x0'], 106.691, 3)
        self.assertAlmostEqual(data['layer_bbox_x1'], 106.943, 3)
        self.assertAlmostEqual(data['layer_bbox_y0'], -6.347, 3)
        self.assertAlmostEqual(data['layer_bbox_y1'], -6.092, 3)

        layer.delete()

        # Flood in EPSG:23833
        flood_23833 = data_helper.misc('flood_epsg_23833.geojson')
        layer = file_upload(flood_23833)
        self.assertEqual(layer.srid, 'EPSG:23833')

        params = {
            'layer_id': layer.id
        }

        # This request should ask for EPSG:4326 by default
        response = self.client.get(layer_tiles_url, data=params)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['layer_name'].startswith('Jakarta Flood'))
        self.assertTrue(
            data['layer_tiles_url'].endswith(
                'qgis-server/tiles/flood_epsg_23833/{z}/{x}/{y}.png'))
        self.assertTrue(
            data['legend_url'].endswith(
                'qgis-server/legend/flood_epsg_23833'))

        self.assertAlmostEqual(data['layer_bbox_x0'], 106.691, 3)
        self.assertAlmostEqual(data['layer_bbox_x1'], 106.944, 3)
        self.assertAlmostEqual(data['layer_bbox_y0'], -6.348, 3)
        self.assertAlmostEqual(data['layer_bbox_y1'], -6.092, 3)

        layer.delete()


class AnalysisTest(GeoSAFEIntegrationLiveServerTestCase):

    def test_run_analysis_no_aggregation(self):
        """Test running analysis without aggregation."""
        data_helper = self.data_helper
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
        data_helper = self.data_helper
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
        data_helper = self.data_helper
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
