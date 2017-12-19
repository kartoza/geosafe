# GeoSAFE App for GeoNode

GeoSAFE is a django app that integrates InaSAFE Headless functionality into 
GeoNode. This app adds new page that enables the user to:

- Add InaSAFE based layers (Layer that contain InaSAFE keywords)
- Create InaSAFE Analysis
- Produce InaSAFE Analysis Reports

Go to **Analysis** page to use this functionality

# Setup

## Latest simple setup

The simplest way to get GeoSAFE going is to use a Rancher Catalogue - see documentation at https://github.com/kartoza/docker-geosafe/

## old setup

Add this package as Django app in your GeoNode installation.
You have to override specific configurations to integrate InaSAFE Headless to 
this app. Sample settings can be seen in *local_settings.sample.py*. This 
settings file should be included in geonode settings file or called last, to 
make sure it overrides celery settings in the default GeoNode settings.

# [User documentation](https://drive.google.com/open?id=0B2pxNIZQUjL1Q1RkVHhVTXAzOWc)

Maintained by Kartoza. 

# Note

The GeoNode project is a requirement for this app to work, since it contains 
dependencies on GeoNode packages.

