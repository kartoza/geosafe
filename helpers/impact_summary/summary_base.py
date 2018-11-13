# coding=utf-8

import json
from collections import OrderedDict

from geonode.layers.models import LayerFile

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '5/17/16'


class ImpactSummary(object):

    def __init__(self, impact_layer):
        self._impact_layer = impact_layer
        self._impact_data = {}
        if self.read_impact_data_json().get('features'):
            properties = (
                self.read_impact_data_json().get('features')[0].get(
                    'properties'))
            self._impact_data = properties

        self._impact_keywords = self.read_impact_keywords()

    @property
    def impact_layer(self):
        """

        :return: Impact Layer
        :rtype: geonode.layers.models.Layer
        """
        return self._impact_layer

    @impact_layer.setter
    def impact_layer(self, impact_layer):
        self._impact_layer = impact_layer

    @property
    def impact_data(self):
        """

        :return: Impact data dictionary
        :rtype: dict
        """
        return self._impact_data

    @impact_data.setter
    def impact_data(self, value):
        self._impact_data = value

    @property
    def impact_keywords(self):
        """

        :return: Impact data dictionary
        :rtype: dict
        """
        return self._impact_keywords

    @impact_keywords.setter
    def impact_keywords(self, value):
        self._impact_keywords = value

    def read_impact_data_json(self):
        """Read impact_data.json file from a given impact layer

        :return: dictionary of impact data
        :rtype: dict
        """
        try:
            json_file = self.impact_layer.upload_session.layerfile_set.get(
                name="analysis_summary.geojson")
            impact_data = json.loads(json_file.file.read())
            return impact_data
        except LayerFile.DoesNotExist:
            return {}

    def read_impact_keywords(self):
        """Read impact keywords"""
        try:
            return self.impact_layer.inasafe_metadata.keywords
        except Exception:
            return {}

    def is_summary_exists(self):
        return self.impact_data

    def is_keywords_exists(self):
        return self.impact_keywords

    def maximum_category_value(self):
        if self.is_summary_exists():
            max_val = max([f.get('value') for f in self.summary_fields()])
            return max_val
        return 0

    def summary_fields(self):
        """convert impact data to list of key-value pair

        :return: list of dict of category and value
        """
        if self.is_summary_exists():
            category_list = self.category_list()
            ret_val = []
            for category in category_list:
                for key, value in self.impact_data.iteritems():
                    class_name = (
                        '{category}_hazard_count').format(category=category)
                    if class_name == key:
                        ret_val.append({
                            "category": category,
                            "value": value
                        })
            return ret_val

    def summary_dict(self):
        """convert summary fields to key value pair"""
        ret_val = OrderedDict()
        for f in self.summary_fields():
            ret_val[f['category']] = f['value']

        return ret_val

    def category_list(self):
        if self.is_keywords_exists():
            provenance_data = self.impact_keywords.get('provenance_data', {})
            if provenance_data:
                hazard_keywords = provenance_data['hazard_keywords']
                available_classifications = (
                    hazard_keywords.get('value_maps') or
                    hazard_keywords.get('thresholds'))
                classes = OrderedDict(
                    available_classifications[self.exposure_type()]
                    [self.hazard_classification()]['classes'])
                if 'not exposed_hazard_count' in self.impact_data.keys():
                    classes['not exposed'] = (
                        self.impact_data['not exposed_hazard_count'])
                return [c for c in classes.keys()]
        return []

    def hazard_classification(self):
        return self.impact_keywords.get(
            'hazard_keywords', {}).get('classification')

    def hazard_type(self):
        return self.impact_keywords.get(
            'hazard_keywords', {}).get('hazard')

    def exposure_type(self):
        return self.impact_keywords.get(
            'exposure_keywords', {}).get('exposure')

    def total(self):
        return int(self.impact_data.get('total'))

    def total_affected(self):
        return int(self.impact_data.get('total_affected'))

    def breakdown_dict(self):
        ret_val = OrderedDict()
        for key, value in self.summary_dict().iteritems():
            ret_val[key] = int(value)
        return ret_val

    def analysis_question(self):
        return self.impact_keywords.get(
            'provenance_data', {}).get('analysis_question')

    def category_css_class(self, category):
        """Get css-class from a given category

        :param category: category string
        :type category: str

        :return:
        """
        cleaned_category_name = (
            category.replace(' ', '-').replace('_', '-').replace(
                '-hazard-count', ''))
        # generic classification
        if 'high' in category.lower():
            return 'hazard-category-high'
        elif 'medium' in category.lower() or 'moderate' in category.lower():
            return 'hazard-category-medium'
        elif 'low' in category.lower():
            return 'hazard-category-low'
        elif 'wet' in category.lower():
            return 'hazard-category-high'
        elif 'dry' in category.lower():
            if self.hazard_type() == 'flood':
                return 'hazard-category-low'
            elif self.hazard_type() == 'tsunami':
                return 'hazard-category-green'
        # EQ MMI Classes
        else:
            return 'hazard-category-%s' % cleaned_category_name
