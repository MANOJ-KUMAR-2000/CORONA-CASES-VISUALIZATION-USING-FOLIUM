"""
DATE: 04.06.2020
@author: MANOJ KUMAR S
"""
# MAP SHOW THE CURRENT CORONA PANDEMIC CASES FOR COUNTRIES

import requests
import pandas as pd
import io
import folium
import numpy as np
import webbrowser
import os

# requesting a data
r = requests.post("https://www.parsehub.com/api/v2/projects/tijK30MYyThL/run", data={"api_key": "tokz_mW569TC"})
response = requests.get('https://www.parsehub.com/api/v2/projects/tijK30MYyThL/last_ready_run/data',params={"api_key":"tokz_mW569TC","format":"csv"})
RAW_DATA = response.content

# processing a data using pandas
DATA = pd.read_csv(io.StringIO(RAW_DATA.decode('utf-8')))
DATA = DATA.replace(np.nan, '0')
features = DATA.columns
for head in features:
    x = (np.array(DATA[head]))
    for i in range(len(x)):
        x[i]=x[i].replace(",","")
    DATA[head] = x
    
# adding a location details to represented country
LOCATION = pd.read_csv("LOCATION.csv")
lat  = []
long = []
for i in range(len(DATA['corona_country'])):
    for j in range(len(LOCATION['country'])):
        if  DATA.iloc[i].corona_country in list(LOCATION['country']):
            if DATA.iloc[i].corona_country == LOCATION.iloc[j].country:
                lat.append(LOCATION.iloc[j].latitude)
                long.append(LOCATION.iloc[j].longitude)
        else:
            lat.append(np.nan)
            long.append(np.nan)
            break
        
# processing a data
DATA[['corona_total_cases','corona_total_death','corona_total_recovered','corona_active_cases','corona_total_test']] = DATA[['corona_total_cases','corona_total_death','corona_total_recovered','corona_active_cases','corona_total_test']].astype('int64')
DATA['latitude'] = np.array(lat)
DATA['longitude'] = np.array(long)
DATA.dropna(axis=0, inplace=True)

# creating a worldmap using folium
WORLD_MAP = folium.Map(location=[20.5937,78.9629],
                       zoom_start=2,
                       tiles='mapbox Bright')

world_geo = r'world_countries.geojson'  # geojson file with country geological data

WORLD_MAP.choropleth(geo_data=world_geo,
                    data=DATA,
                    columns=['corona_country','corona_total_cases'],
                    key_on='feature.properties.ADMIN',
                    fill_color='YlOrRd',
                    legend_name="TOTAL CORONA CASES ACROSS NATIONS")

# creating a markers     
infos = folium.map.FeatureGroup()
for lat, lng, l1,l2,l3,l4 in zip(DATA.latitude, DATA.longitude, DATA.corona_country, DATA.corona_total_cases, DATA.corona_total_death, DATA.corona_active_cases):
    infos.add_child(folium.CircleMarker(
            [lat, lng],
            radius=3, 
            color='red',
            popup=f"COUNTRY:{l1}\nTOTAL CASES:{l2}\nTOTAL DEATH:{l3}\nACTIVE CASES:{l4}",
            fill=True,
            fill_color='blue',
            fill_opacity=0.6,
            tooltip="click here for info"
            )
    )    
WORLD_MAP.add_child(infos)

# displaying a map in windows defalut browser
WORLD_MAP.save('corona.html')
url = "file://"+os.path.realpath('corona.html')
webbrowser.open(url,new=2)