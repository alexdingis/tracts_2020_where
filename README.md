# tracts_2020_where
This file provides descriptor values for where 2020 census tracts are located such as Census region and subdivision, CBSA, place, etc.

This dataset contains **84,781** census tracts linking them to a variety of Census definitions:
- Census tract
  - 2020 census tract GEOID
  - 2022 census tract GEOID (this accounts for Connecticut's changed census tract GEOIDs)
  - 2020 decennial census total population
- Census Place (Using 2022 GeoCorr with population weight) including how the tract was related (whether all or part of the tract is part of the place)
-   Place name and title
- CBSA definitions
  - CBSA code and title
  - CSA code and title
  - Central or Outlying county
  - Metropolitan division and code (where available)
- GIS calculations
  - Square Miles (calculated while using WGS 1984)
  - Desnity = Population / Square Miles
  - Distance to CBSA center (CBSA center defined as lat/lon of city hall of central city) plus percentiles
- Census Regions and Divisions

---

## Dataset Overview

- **Records:** 84,781
- **Geographic Unit** 2020 census tract delineations (includes 2020 and 2022 census tract GEOIDs)
- **Geographic Coverage:** All 50 states, District of Columbia, and Puerto Rico. Other territories are not included

---

##  Fields

| Column | Type     | Description |
|--------|----------|-------------|
| `PLACE_CODE` | object  | 5-digit Census place code |
| `STATE_ABBR.` | object | State abbreviation (e.g., AL, TX) |
| `COUNTY_NAME` | object | County and state name (e.g., Autauga AL) |
| `PLACE_NAME` | object | Place name with state (e.g., Prattville city, AL) |
| `TRACT_TO_PLACE_ALLOCATION_FACTOR` | float64 | Share of tract population allocated to the place |
| `TRACT20` | object | 2020 Census Tract GEOID |
| `PLACE` | object | Combined state and place code (STATEFP + PLACEFP) |
| `MAJORITY_TYPE` | object | Classification of tract-place share which describes how the tract was identified to the place (e.g., COMPLETE, SUPERMAJORITY, MAJORITY). For a full list, please use the 2022 GeoCorr |
| `TRACT22` | object | 2022 version of the tract GEOID which accounts for change in Connecticut GEOIDs |
| `STCNTY22` | object | 2022 County GEOID (STATEFP + COUNTYFP) |
| `CBSA_CODE` | object | Core-Based Statistical Area (CBSA) code using 2023 CBSA list |
| `METROPOLITAN_DIVISION_CODE` | object | Metro division code (if applicable) |
| `CSA_CODE` | object | Combined Statistical Area (CSA) code |
| `CBSA_TITLE` | object | Name of the CBSA |
| `METROPOLITAN_MICROPOLITAN_STATISTICAL_AREA` | object | Metro/micro designation |
| `METROPOLITAN_DIVISION_TITLE` | object | Name of metro division (if applicable) |
| `CSA_TITLE` | object | Name of the Combined Statistical Area |
| `COUNTY_COUNTY_EQUIVALENT` | object | County name |
| `CENTRAL_OUTLYING_COUNTY` | object | CBSA classification: Central or Outlying |
| `PRINCIPAL_CITY` | int64 | Binary flag (1 if principal city of CBSA, else 0) |
| `CENTRAL_CITY` | int64 | Binary flag (1 if central city of CBSA, else 0) |
| `TRACT_POP_20` | float64 | Total tract population from 2020 Census |
| `SQMI` | float64 | Tract land area (square miles) calculated while using WGS 1984 |
| `POP_SQMI` | float64 | Population density (people per square mile) |
| `CBSA_DISTANCE` | float64 | Distance to CBSA center (in miles) calculated while using WGS 1984  |
| `CBSA_PERCENTILE` | float64 | Percentile rank of tract's distance within CBSA |
| `REGION` | object | U.S. Census region (e.g., South, Midwest) |
| `DIVISION` | object | U.S. Census division (e.g., East South Central) |
| `PLACE_POP_20` | float64 | 2020 population of the census place |
---

## 📌 Notes

- Distance and percentile values are calculated using tract centroids and CBSA center points defined as the city hall of the central city in the CBSA.
- `NaN` values in metro division columns indicate the CBSA has no subdivisions.
- Regional and division classifications classifications use U.S. Census Bureau definitions: https://www2.census.gov/geo/pdfs/maps-data/maps/reference/us_regdiv.pdf

---

## 📚 Suggested Uses

- Measuring urban-suburban composition within metro areas  
- Analyzing population density, sprawl, or growth patterns  
- Joining to ACS or Decennial Census tract-level data  

---

## 📄 License

This dataset is shared for research use. Attribution encouraged but not required.

---

## ❓Questions

For questions or suggestions, feel free to open an issue or contact me.
