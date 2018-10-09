# coding=utf-8

import codecs
import logging
import os
import re
import tempfile

from lxml import etree

from geonode.layers.utils import file_upload
from geosafe.helpers.utils import GeoSAFEIntegrationLiveServerTestCase, \
    wait_metadata
from geosafe.models import ISO_METADATA_NAMESPACES, \
    ISO_METADATA_INASAFE_KEYWORD_TAG

LOGGER = logging.getLogger(__file__)


class SignalsTest(GeoSAFEIntegrationLiveServerTestCase):

    def test_inasafe_metadata_capture(self):
        """Test capturing InaSAFE metadata from layer's metadata."""
        data_helper = self.data_helper

        """Case 1. Uploading layer that have no InaSAFE metadata"""

        # Uploading base file only should generate basic metadata.
        ash_fall_only = data_helper.misc('ash_fall_base_only.tif')
        ash_fall_only_layer = file_upload(ash_fall_only)

        # There should be no metadata processing so we can just inspect the
        # layer
        metadata_link = ash_fall_only_layer.link_set.metadata().get(
            name='ISO')
        response = self.client.get(metadata_link.url)

        self.assertEqual(response.status_code, 200)

        metadata_xml = response.content

        # This should be a valid xml
        namespaces = ISO_METADATA_NAMESPACES
        root_metadata_xml = etree.fromstring(metadata_xml)
        identification_info = root_metadata_xml.xpath(
            '//gmd:identificationInfo',
            namespaces=namespaces)

        self.assertTrue(identification_info)
        inasafe_keywords = root_metadata_xml.xpath(
            ISO_METADATA_INASAFE_KEYWORD_TAG,
            namespaces=namespaces)

        # Will not find inasafe keywords safely
        self.assertFalse(inasafe_keywords)

        self.assertTrue(metadata_xml)

        """Case 2. Uploading layer that have InaSAFE metadata"""

        # Upload layer with metadata
        ash_fall = data_helper.hazard('ash_fall.tif')
        ash_fall_layer = file_upload(ash_fall)

        # Wait for InaSAFE to process metadata
        wait_metadata(ash_fall_layer)

        # Validate internal model
        ash_fall_layer.refresh_from_db()
        ash_fall_layer.inasafe_metadata.refresh_from_db()

        self.assertTrue(ash_fall_layer.inasafe_metadata)
        self.assertTrue(ash_fall_layer.inasafe_metadata.keywords_xml)
        self.assertEqual(
            ash_fall_layer.inasafe_metadata.layer_purpose, 'hazard')
        self.assertEqual(
            ash_fall_layer.inasafe_metadata.category, 'volcanic_ash')

        # Fetch metadata from URL
        metadata_link = ash_fall_layer.link_set.metadata().get(
            name='ISO')
        response = self.client.get(metadata_link.url)

        self.assertEqual(response.status_code, 200)

        metadata_xml = response.content

        # This should be a valid xml
        namespaces = ISO_METADATA_NAMESPACES
        root_metadata_xml = etree.fromstring(metadata_xml)
        identification_info = root_metadata_xml.xpath(
            '//gmd:identificationInfo',
            namespaces=namespaces)

        self.assertTrue(identification_info)
        inasafe_keywords = root_metadata_xml.xpath(
            ISO_METADATA_INASAFE_KEYWORD_TAG,
            namespaces=namespaces)

        # Now it should find InaSAFE metadata
        self.assertTrue(inasafe_keywords)

        # Xml in metadata page and model should be the same structurally
        pattern = r'<inasafe [^<]*>'
        replace = '<inasafe xmlns:gmd="http://www.isotc211.org/2005/gmd" ' \
                  'xmlns:gco="http://www.isotc211.org/2005/gco">'
        link_xml = etree.tostring(
            inasafe_keywords[0], pretty_print=True, xml_declaration=False)
        model_xml = etree.tostring(
            etree.fromstring(ash_fall_layer.inasafe_metadata.keywords_xml),
            pretty_print=True, xml_declaration=False)

        # We replace XML header so it will have the same header
        link_xml = re.sub(pattern, replace, link_xml).strip()
        model_xml = re.sub(pattern, replace, model_xml).strip()

        # Match XML representations
        self.assertXMLEqual(
            link_xml,
            model_xml)

        # QGIS XML file should have matched string representation
        with codecs.open(
                ash_fall_layer.qgis_layer.xml_path, encoding='utf-8') as f:
            qgis_xml = f.read()

        self.assertEqual(ash_fall_layer.metadata_xml, qgis_xml)

        """Case 3. Test that uploading new metadata will also update
        InaSAFE metadata. It will be gone if there is no InaSAFE metadata
        """

        # Upload metadata with no InaSAFE keywords
        previous_inasafe_keywords = inasafe_keywords[0]
        inasafe_keywords[0].getparent().remove(inasafe_keywords[0])
        __, metadata_filename = tempfile.mkstemp('.xml')

        with codecs.open(metadata_filename, mode='w', encoding='utf-8') as f:
            f.write(etree.tostring(root_metadata_xml))

        ash_fall_layer = file_upload(
            metadata_filename, metadata_upload_form=True)

        # We do not wait for InaSAFE to process metadata
        # Supposedly, there's no metadata

        # Validate internal model
        ash_fall_layer.refresh_from_db()
        ash_fall_layer.inasafe_metadata.refresh_from_db()

        self.assertTrue(ash_fall_layer.inasafe_metadata)
        # Now there is no InaSAFE keywords
        self.assertFalse(ash_fall_layer.inasafe_metadata.keywords_xml)
        self.assertFalse(ash_fall_layer.inasafe_metadata.layer_purpose)
        self.assertFalse(ash_fall_layer.inasafe_metadata.category)

        # Metadata download will not show InaSAFE keywords
        metadata_link = ash_fall_layer.link_set.metadata().get(
            name='ISO')
        response = self.client.get(metadata_link.url)

        self.assertEqual(response.status_code, 200)

        metadata_xml = response.content

        root_metadata_xml = etree.fromstring(metadata_xml)
        inasafe_keywords = root_metadata_xml.xpath(
            ISO_METADATA_INASAFE_KEYWORD_TAG,
            namespaces=namespaces)

        self.assertFalse(inasafe_keywords)

        # QGIS XML file should have matched string representation
        with codecs.open(
                ash_fall_layer.qgis_layer.xml_path, encoding='utf-8') as f:
            qgis_xml = f.read()

        self.assertEqual(ash_fall_layer.metadata_xml, qgis_xml)

        """Case 4. Test that uploading new metadata will also update
        InaSAFE metadata. Upload new metadata with InaSAFE keywords.
        """

        # Change some detail in the metadata
        inasafe_keywords = previous_inasafe_keywords
        keyword_version = inasafe_keywords.xpath(
            'keyword_version/gco:CharacterString',
            namespaces=namespaces)[0]

        self.assertEqual(keyword_version.text, '4.3')
        # Change keyword version
        keyword_version.text = '4.4'

        # Attach InaSAFE keywords to the new metadata
        supplemental_info = root_metadata_xml.xpath(
            '//gmd:supplementalInformation',
            namespaces=namespaces)[0]
        supplemental_info.append(inasafe_keywords)

        # Upload metadata with new InaSAFE keywords
        with codecs.open(metadata_filename, mode='w', encoding='utf-8') as f:
            f.write(etree.tostring(root_metadata_xml))

        ash_fall_layer = file_upload(
            metadata_filename, metadata_upload_form=True)

        # Wait for InaSAFE to process metadata
        wait_metadata(ash_fall_layer)

        # Validate internal model
        ash_fall_layer.refresh_from_db()
        ash_fall_layer.inasafe_metadata.refresh_from_db()

        self.assertTrue(ash_fall_layer.inasafe_metadata)
        self.assertTrue(ash_fall_layer.inasafe_metadata.keywords_xml)
        self.assertEqual(
            ash_fall_layer.inasafe_metadata.layer_purpose, 'hazard')
        self.assertEqual(
            ash_fall_layer.inasafe_metadata.category, 'volcanic_ash')

        # Fetch metadata from URL
        metadata_link = ash_fall_layer.link_set.metadata().get(
            name='ISO')
        response = self.client.get(metadata_link.url)

        self.assertEqual(response.status_code, 200)

        metadata_xml = response.content

        # This should be a valid xml
        namespaces = ISO_METADATA_NAMESPACES
        root_metadata_xml = etree.fromstring(metadata_xml)
        inasafe_keywords = root_metadata_xml.xpath(
            ISO_METADATA_INASAFE_KEYWORD_TAG,
            namespaces=namespaces)

        # Now it should find InaSAFE metadata
        self.assertTrue(inasafe_keywords)

        inasafe_keywords = inasafe_keywords[0]

        # Check new keywords version
        keyword_version = inasafe_keywords.xpath(
            '//keyword_version/gco:CharacterString',
            namespaces=namespaces)[0]

        self.assertEqual(keyword_version.text, '4.4')

        # QGIS XML file should have matched string representation
        with codecs.open(
                ash_fall_layer.qgis_layer.xml_path, encoding='utf-8') as f:
            qgis_xml = f.read()

        self.assertEqual(ash_fall_layer.metadata_xml, qgis_xml)

        os.remove(metadata_filename)
        ash_fall_only_layer.delete()
        ash_fall_layer.delete()
