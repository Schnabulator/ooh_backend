# Out of Home
This repository contains ONLY the backend stuff for the dhbw project out of home

# Import all German Cities including plz and federal state
* `pip install django-csvimport`
* then add `csvimport.app.CSVImportConf` to the installed apps list
* run command `python manage.py migrate`
* finally import data with `python .\manage.py importcsv --mappings='2=cityname,3=plz,4=bundesland' --model='ooh.Location' --delimiter=',' --charset=utf-8 zuordnung_plz_ort.csv`

# Map view mit OpenStreetmaps