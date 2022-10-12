#Import Python Libraries
import pandas as pd
import folium 
import geopandas as gpd
from folium.features import GeoJsonPopup, GeoJsonTooltip
import streamlit as st
from streamlit_folium import folium_static
import sqlite3
import time
import matplotlib.pyplot as plt
import statsmodels
import branca
conn = sqlite3.connect('soil_test_database')
c = conn.cursor()

c.execute('''  
SELECT * 
FROM soil_wetness
          ''')
wetness = pd.DataFrame(c.fetchall(),columns=['YEAR','January','February', 'March', 'April','May','June','July','August','September','October','November','December','Annual Average','Name'])
wetness.head()

c.execute('''  
SELECT * 
FROM counties
          ''')
st.header("Surface Soil Wetness in California by County")
with st.sidebar:
    
    st.markdown("**Data:**")
    st.write("***Surface Soil Wetness***")
    st.write("The data collected for anysis was the Monthy & Annual Surface Soil Wetness data from the NASA POWER data set. The represents the percent of soil moisture, a value of 0 indicates a completey water-free soil and a value of 1 indicated a completely saturated soil; where surface is the layer from the surface 0cm to 5cm below grade.")
    
    st.write("***Time Data***")
    st.write("The data we collected is from 2011 to 2021. This is in monthly values as well as annual values that represent the average soil wetness percent between all of the months in that year.")
             
    st.write("***Location Data***")
    st.write("Data was collected for every county in California using the POWER Data Access Viewer")
             
  
    
    
    

    
    
    
    st.markdown("**References**")
    st.write("The data was obtained from the National Aeronautics and Space Administration (NASA) Langley Research Center (LaRC) Prediction of Worldwide Energy Resource (POWER) Project funded through the NASA Earth Science/Applied Science Program.")
    st.write("The data was obtained from the POWER Project's Monthly and Annually 2.3.12 version on 2022/09/20.")
 


countydf = pd.DataFrame(c.fetchall(),columns=['county_fips_id','county_name'])

finaldf = countydf.merge(wetness,left_on='county_name',right_on='Name', how='outer')
geodata = gpd.read_file('county_ca.geojson')
combineddf = geodata.merge(finaldf,left_on ='NAME', right_on = 'Name', how ='outer')


tab1, tab2 = st.tabs(["Map Visualization", "Time Series Analysis"])


with tab1:
    


    time = st.selectbox('Choose a year:', (2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021))
    st.write('The year is ', time)
    month = st.selectbox('Choose a month or the annual average:', ('Annual Average','January','February', 'March', 'April','May','June','July','August','September','October','November','December'))


    if (month == 'Annual Average'):
        df =combineddf[['county_fips_id', 'Name','YEAR','Annual Average','geometry' ]]
       
        df = df[df['YEAR']==time]
        st.write('You chose Annual Average')
        
        st.write('Hover your cursor over the county you want to see the Surface Soil Wetness value for.')
        
        
        st.write('The data you chose to view is the Annual Average Surface Soil Wetness for', time)


        m = folium.Map(location=[37, -120], zoom_start=5.5,tiles=None)
        folium.TileLayer('CartoDB positron',name="Light Map",control=False).add_to(m)
       # custom_scale = (df['Annual Average'].quantile((0., 0.3, 0.7 ,0.8 ,0.9 ,1. ))).tolist()




        #Plot Choropleth map using folium
        choropleth1 = folium.Choropleth(
            geo_data='county_ca.geojson',     #This is the geojson file for the Unite States
            name='Choropleth Map of Central Valley Soil Wetness',
            data=df,                                  #This is the dataframe we created in the data preparation step
            columns=['county_fips_id', month],                #'state code' and 'metrics' are the two columns in the dataframe that we use to grab the data for each state and plot it in the choropleth map
            key_on='feature.properties.COUNTYFP',     #This is the key in the geojson file that we use to grab the geometries for each state in order to add the geographical boundary layers to the map
          #  threshold_scale = custom_scale,
            fill_color = 'YlGn',
            nan_fill_color="grey",
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name='Surface Soil Wetness',
            highlight=True,
            line_color='black').geojson.add_to(m)
        geojson1 = folium.features.GeoJson(
                       data=df,
                       name='Surface Soil Wetness Values',
                       smooth_factor=2,
                       style_function=lambda x: {'color':'black','fillColor':'green','weight':0.5},
                       tooltip=folium.features.GeoJsonTooltip(
                           fields=['Name',
                                   'Annual Average',
                                   'YEAR'],
                           aliases=["Name:",
                                    'Annual Average:',
                                    'Year:'], 
                           localize=True,
                           sticky=False,
                           labels=True,
                           style="""
                               background-color: #F0EFEF;
                               border: 2px solid black;
                               border-radius: 3px;
                               box-shadow: 3px;
                           """,
                           max_width=800,),
                            highlight_function=lambda x: {'weight':3,'fillColor':'blue'},
                           ).add_to(m) 
        colormap = branca.colormap.linear.YlGn_09.scale(0, 1)
        colormap = colormap.to_step(index=[0., .1,.2,.3,.4,.5,.6, 0.7 ,0.8 ,0.9 ,1.])
        colormap.caption = 'Surface Soil Wetness'
        colormap.add_to(m)

        folium_static(m)

    else:
        
        
        df = combineddf[['COUNTYFP','YEAR','January','February', 'March', 'April','May','June','July','August','September','October','November','December','Name','geometry']]
        df =df[df['YEAR']==time]
        df =df.loc[:,('COUNTYFP','YEAR',month,"Name",'geometry')]

        st.write('You chose', month)
        
        st.write('Hover your cursor over the county you want to see the Surface Soil Wetness value for.')
        
        
        st.write('The data you chose to view is the Surface Soil Wetness for ', month, time)





        #Initiate a folium map
        m = folium.Map(location=[37, -120], zoom_start=5.5,tiles=None)
        folium.TileLayer('CartoDB positron',name="Light Map",control=False).add_to(m)
     
        #custom_scale = (df[month].quantile((0., 0.3, 0.7 ,0.8 ,0.9 ,1. ))).tolist()




        #Plot Choropleth map using folium
        choropleth1 = folium.Choropleth(
            geo_data='county_ca.geojson',     #This is the geojson file for the Unite States
            name='Choropleth Map of Central Valley Soil Wetness',
            data=df,                                  #This is the dataframe we created in the data preparation step
            columns=['COUNTYFP', month],                #'state code' and 'metrics' are the two columns in the dataframe that we use to grab the data for each state and plot it in the choropleth map
            key_on='feature.properties.COUNTYFP',             #This is the key in the geojson file that we use to grab the geometries for each state in order to add the geographical boundary layers to the map
          #  threshold_scale = custom_scale,

            fill_color = 'YlGn',
            nan_fill_color="grey",
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name='Surface Soil Wetness',
            highlight=True,
            line_color='black').geojson.add_to(m)
        geojson1 = folium.features.GeoJson(
                       data=df,
                       name='Soil Wetness Values',
                       smooth_factor=2,
                       style_function=lambda x: {'color':'black','fillColor':'green','weight':0.5},
                       tooltip=folium.features.GeoJsonTooltip(
                           fields=['Name',
                                   month,
                                   'YEAR'],
                           aliases=["Name:",
                                    'Soil Wetness Value:',
                                    'Year:'], 
                           localize=True,
                           sticky=False,
                           labels=True,
                           style="""
                               background-color: #F0EFEF;
                               border: 2px solid black;
                               border-radius: 3px;
                               box-shadow: 3px;
                           """,
                           max_width=800,),
                            highlight_function=lambda x: {'weight':3,'fillColor':'blue'},
                           ).add_to(m) 
        colormap = branca.colormap.linear.YlGn_09.scale(0, 1)
        colormap = colormap.to_step(index=[0., .1,.2,.3,.4,.5,.6, 0.7 ,0.8 ,0.9 ,1.])
        colormap.caption = 'Surface Soil Wetness'
        colormap.add_to(m)
        
        folium_static(m)



with tab2:
    countyname =  st.selectbox('Choose a county:', ('Alameda',
     'Alpine',
     'Humboldt',
     'Lake',
     'Los Angeles',
     'Nevada',
     'San Mateo',
     'Santa Clara',
     'Yuba',
     'Mendocino',
     'Mono',
     'Riverside',
     'San Benito',
     'San Luis Obispo',
     'Santa Barbara',
     'Sutter',
     'Tulare',
     'Butte',
     'Solano',
     'Calaveras',
     'Colusa',
     'Monterey',
     'Stanislaus',
     'San Bernardino',
     'Del Norte',
     'Plumas',
     'Shasta',
     'Siskiyou',
     'Marin',
     'San Joaquin',
     'Contra Costa',
     'Glenn',
     'Imperial',
     'Placer',
     'Kings',
     'Lassen',
     'Tuolumne',
     'San Francisco',
     'Fresno',
     'Modoc',
     'Santa Cruz',
     'Tehama',
     'Ventura',
     'San Diego',
     'Kern',
     'El Dorado',
     'Sierra',
     'Orange',
     'Yolo',
     'Trinity',
     'Madera',
     'Inyo',
     'Amador',
     'Sacramento',
     'Napa',
     'Sonoma',
     'Mariposa',
     'Merced'))
    
    wetness['YEAR'] = wetness['YEAR'].astype('str')


    wetness['Month'] = '1'
    wetness['Day'] = '1'
    wetness['Date'] = pd.to_datetime(wetness[['YEAR','Month','Day']], format = '%Y-%m')
    Jandf = wetness[["January",'Date','Name']]
    Jandf = Jandf.rename(columns={'January':'Value'})

    wetness['Month'] = '2'
    wetness['Day'] = '1'
    wetness['Date'] = pd.to_datetime(wetness[['YEAR','Month','Day']], format = '%Y-%m')
    Febdf = wetness[["February",'Date','Name']]
    Febdf = Febdf.rename(columns={'February':'Value'})

    wetness['Month'] = '3'
    wetness['Day'] = '1'
    wetness['Date'] = pd.to_datetime(wetness[['YEAR','Month','Day']], format = '%Y-%m')
    Mardf = wetness[["March",'Date','Name']]
    Mardf = Mardf.rename(columns={'March':'Value'})

    wetness['Month'] = '4'
    wetness['Day'] = '1'
    wetness['Date'] = pd.to_datetime(wetness[['YEAR','Month','Day']], format = '%Y-%m')
    Aprdf = wetness[["April",'Date','Name']]
    Aprdf = Aprdf.rename(columns={'April':'Value'})

    wetness['Month'] = '5'
    wetness['Day'] = '1'
    wetness['Date'] = pd.to_datetime(wetness[['YEAR','Month','Day']], format = '%Y-%m')
    Maydf = wetness[["May",'Date','Name']]
    Maydf = Maydf.rename(columns={'May':'Value'})

    wetness['Month'] = '6'
    wetness['Day'] = '1'
    wetness['Date'] = pd.to_datetime(wetness[['YEAR','Month','Day']], format = '%Y-%m')
    Jundf = wetness[["June",'Date','Name']]
    Jundf = Jundf.rename(columns={'June':'Value'})

    wetness['Month'] = '7'
    wetness['Day'] = '1'
    wetness['Date'] = pd.to_datetime(wetness[['YEAR','Month','Day']], format = '%Y-%m')
    Juldf = wetness[["July",'Date','Name']]
    Juldf = Juldf.rename(columns={'July':'Value'})

    wetness['Month'] = '8'
    wetness['Day'] = '1'
    wetness['Date'] = pd.to_datetime(wetness[['YEAR','Month','Day']], format = '%Y-%m')
    Augdf = wetness[["August",'Date','Name']]
    Augdf = Augdf.rename(columns={'August':'Value'})

    wetness['Month'] = '9'
    wetness['Day'] = '1'
    wetness['Date'] = pd.to_datetime(wetness[['YEAR','Month','Day']], format = '%Y-%m')
    Sepdf = wetness[["September",'Date','Name']]
    Sepdf = Sepdf.rename(columns={'September':'Value'})

    wetness['Month'] = '10'
    wetness['Day'] = '1'
    wetness['Date'] = pd.to_datetime(wetness[['YEAR','Month', 'Day']],format = '%Y-%m')
    Octdf = wetness[["October",'Date','Name']]
    Octdf = Octdf.rename(columns={'October':'Value'})

    wetness['Month'] = '11'
    wetness['Day'] = '1'
    wetness['Date'] = pd.to_datetime(wetness[['YEAR','Month','Day']], format = '%Y-%m')
    Novdf = wetness[["November",'Date','Name']]
    Novdf = Novdf.rename(columns={'November':'Value'})

    wetness['Month'] = '12'
    wetness['Day'] = '1'
    wetness['Date'] = pd.to_datetime(wetness[['YEAR','Month','Day']], format = '%Y-%m')
    Decdf = wetness[["December",'Date','Name']]
    Decdf = Decdf.rename(columns={'December':'Value'})

    timesdf = pd.concat([Jandf,Febdf,Mardf,Aprdf,Maydf,Jundf,Juldf,Augdf,Sepdf,Octdf,Novdf,Decdf])
    
    
    from statsmodels.tsa.seasonal import seasonal_decompose

    tsdf = timesdf.loc[timesdf['Name']== countyname]
    tsdf = tsdf.sort_values(by=['Date'])

    tsdf.set_index('Date', inplace=True)

    analysis = tsdf[['Value']].copy()


    decompose_result_mult = seasonal_decompose(analysis, model="multiplicative")

    trend = decompose_result_mult.trend
    seasonal = decompose_result_mult.seasonal
    residual = decompose_result_mult.resid

    fig = decompose_result_mult.plot()
    fig.set_size_inches((15,15))
    fig.tight_layout()
    st.pyplot(fig)