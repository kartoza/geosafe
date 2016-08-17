# Geosafe App for Geonode

Geosafe is a django app that integrates InaSAFE Headless functionality into 
Geonode. This app adds new page that enabled user to:

- Add InaSAFE based layer (Layer that contains InaSAFE keywords)
- Create InaSAFE Analysis
- Produce InaSAFE Analysis Reports

Go to **Analysis** page to use this functionality

# Setup

Add this package as django app in your geonode installations.
You have to override specific configuration to integrate InaSAFE Headless to 
this app. A sample settings can be seen in *local_settings.sample.py*. This 
settings file should be included in geonode settings file or called last, to 
make sure it was overriding celery settings in the default geonode settings.

# Note

Geonode project is a requirement for this app to works, since it contains 
dependency to geonode packages.

