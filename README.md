# Air Pollution Health Burden in Europe
Data Science Project Lifecycle module project — University of Westminster
## Overview
An interactive Streamlit dashboard exploring how air pollution affects health across 41 European countries in 2022. The project uses data from the European Environment Agency to analyse the burden caused by PM2.5, NO2, and O3 across mortality and morbidity outcomes, broken down by country, pollutant, and health indicator.
## Key Findings
- **PM2.5 causes the highest health burden** — consistently the dominant pollutant across nearly all European countries, with significantly higher burden values than NO2 and O3 in the cross-pollutant comparison.
- **Eastern Europe is disproportionately affected** — countries like Bulgaria, North Macedonia, and Serbia show far higher burden rates per 100,000 population than Western European counterparts.
- **Pollution concentration and health burden are positively correlated** — visible in the scatter plot, though not perfectly linear due to factors like population age structure and healthcare quality.
## Dashboard Features
- Choropleth map of Europe showing health burden by country with an outcome selector
- Analysis tab with a histogram, scatter plot, and burden breakdown by health outcome
- Comparison tab with a grouped bar chart comparing selected countries across all three pollutants
- Sidebar filters for country, pollutant, health category, and health indicator
- KPI summary metrics showing total burden, average per 100k, and average pollution level
## How to Run
`git clone https://github.com/RashmiThrauka/Air-pollution-health-burden.git\`
`cd Air-pollution-health-burden`
`pip install -r requirements.txt`
`streamlit run app.py`
## Dataset
- **Source:** European Environment Agency — Burden of Disease of Air Pollution (Countries & NUTS)
- **Link:** https://www.eea.europa.eu/en/datahub/datahubitem-view/49930245-dc33-4c47-93b8-9512f0622ebc
- ~3,000 country-level records filtered from an original 94,165-row dataset covering 41 countries in 2022
## Tools
Python · Streamlit · Plotly · Pandas
## Live App
https://air-pollution-health-burden-9gl8boczvkjmrgaz7ibrzp.streamlit.app/#air-pollution-health-burden-in-europe
