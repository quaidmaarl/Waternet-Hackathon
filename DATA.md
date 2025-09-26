# Data 
Dit bestand beschrijft de data die beschikbaar wordt gesteld in de hackathon.

## Beschrijving

De data bevat metingen van oppervlaktewaterkwaliteit, van het eerste data punt in 1963 tot 2025. De bestanden staan op sharepoint en worden met je gedeeld op de dag van de hackathon. Oppervlaktewaterkwaliteit wordt gemeten aan de hand van hydrobiologische en chemische toetsing. In de file 'FYCHEM_alleParamtrs_alleJaren_Amstelland_1900tmjuni.csv' staan de ruwe meetgegevens voor de fysisch chemische toetsing. In de file 'HB_alleKwalelementen_alleJaren_Amstelland.csv' staan de ruwe meetgegevens voor hydrobiologische toetsing. Vanaf 2006 zijn de meetwaardes via een bepaalde standaard gemeten, in de jaren hiervoor is dit niet het geval. In [oppervlaktewater kwaliteit analyse notebook](./tutorials/Analyseren%20oppervlaktewater%20kwaliteit.ipynb) staat wat meer informatie over de data, hoe je dit inleest, eruit ziet, welke kolommen relevant zijn, en dit kunt visualiseren.

## Mappenstructuur

```plaintext
data/
├─ shapefiles/
│ ├─ GEE (google earth engine)/
│ │ ├─ amstel_shapefile
│ │ ├─ amstelland_shapefile
│ │ ├─ gemalen_shapefile
│ ├─ amstelland.zip
│ ├─ Beheerregister_EAG_20241218.zip
│ ├─ Beheerregister_Water_20241218.zip
├─ uitvoer aquo-kit/
│ ├─ fytoplankton.csv
│ ├─ macrofauna.csv
│ ├─ macrofyten.csv
│ ├─ vissen.csv
├─ waternet FEWS data/
│ ├─ waterkwantiteit/
│ │ ├─ Amstelsluizen_waterhoogte.csv
│ │ ├─ Berlagebrug_debiet_waterhoogte.csv
│ │ ├─ polderdebieten_10min_fews.zip
│ │ ├─ polderdebieten_uur_fews.zip
│ ├─ FYCHEM_alleParamtrs_alleJaren_Amstelland_1900tmjuni.csv
│ ├─ HB_alleKwalelementen_alleJaren_Amstelland.csv
│ ├─ FYCHEM_sampled50locations.csv
│ ├─ HB_sampled50locations.csv
│ ├─ FYCHEM_unique_locations_with_measurements.geojson
│ ├─ HB_unique_locations_with_measurements.geojson
│ ├─ Parameter_uitleg.xlsx
├─ watersysteemkaarten/
│ ├─ WSK_{code}.pdf
│ ├─ Codes Afvoergebieden.xlsx
├─ Lijst van scorende soorten - M-typen_202507071242.csv
├─ Normen_stoffen_zoetwater.xlsx
```

### shapefiles/

| Bestand | Beschrijving | Opmerkingen |
|---------|---------------|--------------|
| `GEE (Google Earth Engine)` | Shapefiles van de Amstel, Amstellandboezem en gemalen  | GEE gebruikt standaard WGS84 (EPSG:4326) coördinaten, dit wijkt af van de coördinatenstelsels waarin de shapefiles zijn aangeleverd |
| `Beheerregister_EAG_20241218.zip` | Shapefile ecologisch analyse gebied |  |
| `Beheerregister_Water_20241218.zip` | Shapefile aan- en afvoergebieden | |

### uitvoer aquo-kit/

| Bestand | Beschrijving | Opmerkingen |
|---------|---------------|--------------|
| `fytoplankton.csv` | Aquo-kit resultaten voor fytoplankton |  |
| `macrofauna.csv` | Aquo-kit resultaten voor macrofauna | |
| `macrofyten.csv` | Aquo-kit resultaten voor macrofyten | |
| `vissen.csv` | Aquo-kit resultaten voor vissen | |

### waternet FEWS data/

| Naam | Beschrijving | Opmerkingen |
|------|---------------|--------------|
| `waterkwantiteit` | Sensor waardes van waterhoogte en debieten in de Amstellandboezem |  
| `FYCHEM_alleParamtrs_alleJaren_Amstelland_1900tmjuni.csv` | Fysische Chemische data voor alle jaren | Meetwaardes |
| `HB_alleKwalelementen_alleJaren_Amstelland.csv` | Hydrobiologische data voor alle jaren | Meetwaardes |
| `FYCHEM_sampled50locations.csv` | Een subset van de Fysische Chemische data voor alle jaren | Voor de hackathon kan je al kijken hoe de data eruit ziet |
| `HB_sampled50locations.csv` | Een subset van de Hydrobiologische data voor alle jaren | Voor de hackathon kan je al kijken hoe de data eruit ziet |
| `FYCHEM_unique_locations_with_measurements.geojson` | Een geojson bestand met de locaties van de Fysische Chemische meetpunten | Om het makkelijk op een kaart te plotten |
| `HB_unique_locations_with_measurements.geojson` | Een geojson bestand met de locaties van de Hydrobiologische meetpunten | Om het makkelijk op een kaart te plotten |
| `Parameter_uitleg.xlsx` | Uitleg parameter meetwaardes | |

### watersysteemkaarten/ 

| Naam | Beschrijving | Opmerkingen |
|------|---------------|--------------|
| `WSK_{code}.pdf` | In een watersysteemkaart zijn per aan-/afvoergebied de kunstwerken (gemalen, stuwen, schotten, inlaten, duikers, dammen, enz ) de watergangen en de peilgebieden met peilen te vinden | Ter informatie |
| `Codes Afvoergebieden.xlsx` | Codes en namen van aan-/afvoergebieden in de watersysteemkaarten |  |

### Losse bestanden
| Naam | Beschrijving | Opmerkingen |
|------|---------------|--------------|
| `normen_stoffen_zoetwater.csv` | Bevat normen van het RIVM per stof voor zoetwater | Chemische toetsing |
| `lijst van scorende soorten - M-typen_202507071242` | Lijst van stoffen gewenste en ongewenste soorten | 1-3 gewenst, 4-5 ongewenst, Amstellandboezem = M6b |

## Gebruik

- Data is ruwe export uit het systeem.
- Bevat geen persoonsgegevens.
- Publiekelijke data
