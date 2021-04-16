# Out of Home
This repository contains ONLY the backend stuff for the dhbw project out of home

# Import all German Cities including plz and federal state
* `pip install django-csvimport`
* then add `csvimport.app.CSVImportConf` to the installed apps list
* run command `python manage.py migrate`
* finally import data with `python .\manage.py importcsv --mappings='2=cityname,3=plz,4=bundesland' --model='ooh.Location' --delimiter=',' --charset=utf-8 zuordnung_plz_ort.csv`

# Map view mit OpenStreetmaps

# Klassen
Kulturell
<i class="fas fa-university"></i>
Feiern
<i class="fas fa-cocktail"></i>
Essen
<i class="fas fa-utensils"></i>


Feiern

Wo feiern?
Club
<i class="fas fa-glass-cheers"></i>
Bar
<i class="fas fa-beer"></i>
Musikrichtung
Elektro
<i class="fas fa-compact-disc"></i>
Rock
<i class="fas fa-drum"></i>
Pop
<i class="fas fa-guitar"></i>
Hip-Hop
<i class="fas fa-headphones"></i>
Rauchen
Ja
<i class="fas fa-smoking"></i>
Nein
<i class="fas fa-smoking-ban"></i>
Teuer?
Gehoben
<i class="far fa-credit-card"></i>
Preiswert
<i class="fas fa-money-bill-alt"></i>


Essen

Amerikanisch
<i class="fas fa-hamburger"></i>
<i class="fas fa-globe-americas"></i>
Europäisch
<i class="fas fa-pizza-slice"></i>
<i class="fas fa-globe-europe"></i>
Asia
<i class="fas fa-user-ninja"></i>
<i class="fas fa-globe-asia"></i>
Africa
<i class="fas fa-globe-africa"></i>
Kulturell

Vorführung
<i class="fas fa-theater-masks"></i>
Ausstellung
<i class="fas fa-palette"></i>