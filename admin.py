from django.contrib import admin
from geosafe.models import Metadata, Analysis


# Register your models here.
class MetadataAdmin(admin.ModelAdmin):
    list_display = (
        'layer',
        'layer_purpose',
        'category',
    )


class AnalysisAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'exposure_layer',
        'hazard_layer',
        'aggregation_layer',
        'extent_option',
        'impact_function_id',
        'keep',
        'task_state'
    )


admin.site.register(Metadata, MetadataAdmin)
admin.site.register(Analysis, AnalysisAdmin)
