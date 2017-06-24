__author__ = 'ismailsunni'

from django.conf.urls import patterns, url

from geosafe.views import metasearch
from geosafe.views.analysis import (
    AnalysisListView,
    AnalysisCreateView,
    AnalysisDetailView,
    impact_function_filter,
    layer_tiles, layer_metadata, layer_archive, layer_list, rerun_analysis,
    analysis_json, toggle_analysis_saved, download_report, layer_panel,
    analysis_summary, cancel_analysis)

urlpatterns = patterns(
    '',
    url(
        r'^analysis/create(?:/(?P<pk>\d*))?$',
        AnalysisCreateView.as_view(),
        name='analysis-create'
    ),
    url(
        r'^analysis/(?:/user/(?P<user>\d*))?$',
        AnalysisListView.as_view(),
        name='analysis-list'
    ),
    url(
        r'^analysis/impact-function-filter$',
        impact_function_filter,
        name='impact-function-filter'
    ),
    url(
        r'^analysis/(?P<pk>\d+)$',
        AnalysisDetailView.as_view(),
        name='analysis-detail'
    ),
    url(
        r'^analysis/layer-tiles$',
        layer_tiles,
        name='layer-tiles'
    ),
    url(
        r'^analysis/layer-metadata/(?P<layer_id>\d+)',
        layer_metadata,
        name='layer-metadata'
    ),
    url(
        r'^analysis/layer-archive/(?P<layer_id>\d+)',
        layer_archive,
        name='layer-archive'
    ),
    url(
        r'^analysis/layer-list/'
        r'(?P<layer_purpose>(hazard|exposure|aggregation|impact))'
        r'(?:/(?P<layer_category>\w*))?'
        r'(?:/(?P<bbox>[,.\d-]*))?',
        layer_list,
        name='layer-list'
    ),
    url(
        r'^analysis/layer-panel'
        r'(?:/(?P<bbox>[\[\],.\d-]*))?',
        layer_panel,
        name='layer-panel'
    ),
    url(
        r'^analysis/rerun/'
        r'(?P<analysis_id>\d+)',
        rerun_analysis,
        name='rerun-analysis'
    ),
    url(
        r'^analysis/cancel/'
        r'(?P<analysis_id>\d+)',
        cancel_analysis,
        name='cancel-analysis'
    ),
    url(
        r'^analysis/check/'
        r'(?P<analysis_id>\d+)',
        analysis_json,
        name='check-analysis'
    ),
    url(
        r'^analysis/toggle-saved/'
        r'(?P<analysis_id>[-\d]+)',
        toggle_analysis_saved,
        name='toggle-analysis-saved'
    ),
    url(
        r'^analysis/report/'
        r'(?P<analysis_id>\d+)/'
        r'(?P<data_type>(map|table|reports|all))',
        download_report,
        name='download-report'
    ),
    url(
        r'^analysis/summary/'
        r'(?P<impact_id>[-\d]+)/',
        analysis_summary,
        name='analysis-summary'
    ),

    # Metasearch
    url(
        r'^metasearch/$',
        metasearch.index,
        name='metasearch'
    ),
    url(
        r'^metasearch/csw_ajax$',
        metasearch.csw_ajax,
        name='metasearch_csw_ajax'
    ),
    url(
        r'^metasearch/add_layer$',
        metasearch.add_layer,
        name='metasearch_add_layer'
    ),
    url(
        r'^metasearch/add_layer_dialog',
        metasearch.show_add_layer_dialog,
        name='metasearch_add_layer_dialog'
    ),
    url(
        r'^metasearch/show_metadata',
        metasearch.show_metadata,
        name='metasearch_show_metadata'
    ),

    url(
        r'^metasearch/wfs_proxy',
        metasearch.wfs_proxy,
        name='metasearch_wfs_proxy'
    ),
)
