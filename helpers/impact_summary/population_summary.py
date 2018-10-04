# coding=utf-8
from geosafe.helpers.impact_summary.summary_base import ImpactSummary

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '5/18/16'


class PopulationSummary(ImpactSummary):

    def total_populations(self):
        return self.total()

    def category_css_class(self, category):
        css_class = ImpactSummary.category_css_class(category)
        if not css_class:
            if 'people' in category.lower():
                css_class = 'hazard-category-high'
            elif 'fatalities' in category.lower():
                css_class = 'hazard-category-high'
            elif 'displaced' in category.lower():
                css_class = 'hazard-category-high'
            elif 'affected' in category.lower():
                css_class = 'hazard-category-high'
            elif 'floodprone' in category.lower():
                css_class = 'hazard-category-high'
            elif 'radius' in category.lower():
                css_class = 'hazard-category-high'
        return css_class
