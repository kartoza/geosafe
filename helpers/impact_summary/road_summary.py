# coding=utf-8
from geosafe.helpers.impact_summary.summary_base import ImpactSummary

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '6/13/16'


class RoadSummary(ImpactSummary):

    def total_roads(self):
        return self.total()

    def category_css_class(self, category):
        css_class = ImpactSummary.category_css_class(category)
        if not css_class:
            if 'closed' in category.lower():
                css_class = 'hazard-category-high'
            elif 'flooded' in category.lower():
                css_class = 'hazard-category-high'
        return css_class
