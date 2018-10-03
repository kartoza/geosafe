# coding=utf-8
from collections import OrderedDict

from geosafe.helpers.impact_summary.summary_base import ImpactSummary

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '5/18/16'


class StructureSummary(ImpactSummary):

    def total_buildings(self):
        return self.total()

    def category_css_class(self, category):
        css_class = ImpactSummary.category_css_class(category)
        if not css_class:
            if 'flood' in category.lower():
                css_class = 'hazard-category-high'
            elif 'dry' in category.lower():
                css_class = 'hazard-category-low'
            elif 'wet' in category.lower():
                css_class = 'hazard-category-medium'
            elif 'radius' in category.lower():
                css_class = 'hazard-category-high'
            elif 'vii' in category.lower():
                css_class = 'hazard-category-VII'
        return css_class
