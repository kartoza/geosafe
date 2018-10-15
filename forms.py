# coding=utf-8
import logging

from django import forms
from django.forms import models

from geonode.layers.models import Layer
from geonode.people.models import Profile
from geosafe.models import Analysis

__author__ = 'ismailsunni'

LOGGER = logging.getLogger(__name__)


class AnalysisCreationForm(models.ModelForm):
    """A form for creating an event."""

    class Meta:
        model = Analysis
        fields = (
            'user_title',
            'user_extent',
            'exposure_layer',
            'hazard_layer',
            'aggregation_layer',
            'aggregation_filter',
            'language_code',
            'extent_option',
            'keep',
        )

    user_title = forms.CharField(
        label='Analysis Title',
        required=False,
        widget=forms.TextInput(
            attrs={'placeholder': 'Default title generated'})
    )

    user_extent = forms.CharField(
        label='Analysis Extent',
        required=False,
    )

    exposure_layer = forms.ModelChoiceField(
        label='Exposure Layer',
        required=True,
        queryset=Layer.objects.filter(
            inasafe_metadata__layer_purpose='exposure'),
        widget=forms.Select(
            attrs={'class': 'form-control'})
    )

    hazard_layer = forms.ModelChoiceField(
        label='Hazard Layer',
        required=True,
        queryset=Layer.objects.filter(
            inasafe_metadata__layer_purpose='hazard'),
        widget=forms.Select(
            attrs={'class': 'form-control'})
    )

    aggregation_layer = forms.ModelChoiceField(
        label='Aggregation Layer',
        required=False,
        queryset=Layer.objects.filter(
            inasafe_metadata__layer_purpose='aggregation'),
        widget=forms.Select(
            attrs={'class': 'form-control'})
    )

    aggregation_filter = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )
    # Filter format:
    # This field should contain JSON object with the following format:
    #     {
    #         'property_name': <the name of the property to filter>
    #         'values': <list of values for this property>
    #     }
    #
    # Example:
    #
    #     {
    #         'property_name': 'area_name',
    #         'values': ['area 1', 'area 2', 'area 3']
    #     }

    language_code = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )

    keep = forms.BooleanField(
        label='Save Analysis',
        required=False,
    )

    @staticmethod
    def exposure_choice_queryset():
        return Layer.objects.filter(
            inasafe_metadata__layer_purpose='exposure')

    @staticmethod
    def hazard_choice_queryset():
        return Layer.objects.filter(
            inasafe_metadata__layer_purpose='hazard')

    @staticmethod
    def aggregation_choice_queryset():
        return Layer.objects.filter(
            inasafe_metadata__layer_purpose='aggregation')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.language_code = kwargs.pop('language_code', None)
        exposure_layer = kwargs.pop('exposure_layer', None)
        hazard_layer = kwargs.pop('hazard_layer', None)
        aggregation_layer = kwargs.pop('aggregation_layer', None)
        super(AnalysisCreationForm, self).__init__(*args, **kwargs)
        if exposure_layer:
            self.fields['exposure_layer'].queryset = exposure_layer
        else:
            self.fields['exposure_layer'].queryset = \
                self.exposure_choice_queryset()
        if hazard_layer:
            self.fields['hazard_layer'].queryset = hazard_layer
        else:
            self.fields['hazard_layer'].queryset = \
                self.hazard_choice_queryset()
        if aggregation_layer:
            self.fields['aggregation_layer'].queryset = aggregation_layer
        else:
            self.fields['aggregation_layer'].queryset = \
                self.aggregation_choice_queryset()

    def save(self, commit=True):
        instance = super(AnalysisCreationForm, self).save(commit=False)
        instance.language_code = self.language_code
        if self.user.username:
            instance.user = self.user
        else:
            instance.user = Profile.objects.get(username='AnonymousUser')
        # validate aggregation filter
        if instance.aggregation_layer:
            if not instance.aggregation_filter:
                # Standardize to empty value
                instance.aggregation_filter = None
        instance.save()
        return instance


class MetaSearchForm(forms.Form):

    class Meta:
        fields = (
            'csw_url',
            'keywords',
            'user',
            'password',
        )

    csw_url = forms.CharField(
        label='CSW URL',
        help_text='URL to CSW endpoint',
        required=True)
    keywords = forms.CharField(
        help_text='Keywords to include in the search',
        required=False)
    user = forms.CharField(
        help_text='User to connect to CSW Endpoint',
        required=False)
    password = forms.CharField(
        help_text='Password to connect to CSW Endpoint',
        required=False,
        widget=forms.PasswordInput(render_value=True))
