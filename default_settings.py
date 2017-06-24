# coding=utf-8


# Opt-in to use layerfile direct disk access for InaSAFE Headless Celery
# workers insted of Http
USE_LAYER_FILE_ACCESS = True


# Location of local layer file that can be accessed by InaSAFE worker directly
# This path will be accessed by InaSAFE Celery Worker
#
# For example, if celery workers need to fetch layers from GeoSAFE with name
# vector_layer.shp, since this file is located in media folders in:
# /usr/src/app/geonode/uploaded/layers/vector_layer.shp
# GeoSAFE then tries to find its relative path from
# INASAFE_LAYER_DIRECTORY_BASE_PATH, which is vector_layer.shp. Then it
# appended the relative path to INASAFE_LAYER_DIRECTORY:
# /home/geosafe/layers/vector_layer.shp . Then this is the path that will be
# accessed by InaSAFE Headless Celery Worker
INASAFE_LAYER_DIRECTORY = '/home/geosafe/media/'
INASAFE_LAYER_DIRECTORY_BASE_PATH = '/usr/src/app/geonode/uploaded/'

# Location of InaSAFE Impact Layer output that can be accessed by
# GeoSAFE.
# This path will be accessed by GeoSAFE
GEOSAFE_IMPACT_OUTPUT_DIRECTORY = '/home/geosafe/impact_layers/'


# Location of InaSAFE Impact Layer output base url
# This base url will be set as root path for GEOSAFE_IMPACT_OUTPUT_DIRECTORY
# Impact output path will be extracted from relative path from this base url
# then appended to GEOSAFE_IMPACT_OUTPUT_DIRECTORY.
#
# For example, if InaSAFE output path taken from analysis results coming from
# celery worker is: http://inasafe-output/output/20170519/temp_analysis.zip
# Then file path which will be accessed by GeoSAFE is:
# /home/geosafe/impact_layers/20170519/temp_analysis.zip
INASAFE_IMPACT_BASE_URL = '/output/'


# Opt-in to use layerfile http access for InaSAFE Headless Celery
# workers instead of disk access
USE_LAYER_HTTP_ACCESS = False


# This base url is needed for InaSAFE worker to be able to find Geonode to
# fetch layers
GEONODE_BASE_URL = 'http://localhost:8000/'


# Analysis Run Time Limit (in seconds)
# Task will exit if exceeded this hard limit
ANALYSIS_RUN_TIME_LIMIT = 600
