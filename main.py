import inline as inline
import matplotlib
import pandas as pd
import numpy as np
import urllib.request
import zipfile
import random
import itertools
import math
import os
import glob
import sqlite3
# from app import app

from plotly.figure_factory._county_choropleth import shapefile
import plotly.graph_objects as go
import plotly.express as px

import dash
import dash_core_components as dcc
import dash_html_components as html

from geolocation.main import GoogleMaps
from geolocation.distance_matrix.client import DistanceMatrixApiClient

import datetime

# Access Token for mapbox
accsesstoken_mapbox = 'pk.eyJ1IjoieWFnaW11dHN1IiwiYSI6ImNrNTFseWlhajB2amgzZXNhd281cmo2ZjcifQ.JJ28hvjtlI_9eFG5e8Gw8g'

# Tllset ID
tll_id = 'yagimutsu.9bu77srh'

os.chdir("F:\CS405_Data_Visualization")

config = ({
    'existing_locations_csv': 'taxi_zones.csv',

    'standard_query': "SELECT COUNT(*) FROM 'yellow_tripdata_2017-04' WHERE ",

    'unused_columns': ['VendorID',
                       'tpep_pickup_datetime',
                       'passenger_count',
                       'trip_distance',
                       'RatecodeID',
                       'store_and_fwd_flag',
                       'PULocationID',
                       'fare_amount',
                       'extra',
                       'mta_tax',
                       'tip_amount',
                       'tolls_amount',
                       'improvement_surcharge',
                       'total_amount'],

    'payment_methods_dict': {"Credit Card": 1,
                             "Cash": 2,
                             "No Charge": 3,
                             "Dispute": 4,
                             "Unknown": 5,
                             "Voided": 6}
})

# Downloading Trip Record Data & Location Data
"""
# Download the Trip Record Data
for month in range(1,7):
    urllib.request.urlretrieve("https://s3.amazonaws.com/nyc-tlc/trip+data/"+ \
                               "yellow_tripdata_2017-{0:0=2d}.csv".format(month),
                               "nyc.2017-{0:0=2d}.csv".format(month))

# Download the location Data
urllib.request.urlretrieve("https://s3.amazonaws.com/nyc-tlc/misc/taxi_zones.zip", "taxi_zones.zip")
with zipfile.ZipFile("taxi_zones.zip","r") as zip_ref:
    zip_ref.extractall("./shape")
"""
#######################################


# 6 Months of Data (Yellow Taxi Trip)
extension = 'csv'
all_files = []

"""
for month in range(1,7):
    date_0 = '2017-{0:0=2d}-01 00:00:00'.format(month)
    date_1 = '2017-{0:0=2d}-02 00:00:00'.format(month)
    dates = [date_0, date_1]
    curr_df_name = "nyc.2017-{0:0=2d}.csv".format(month)
    curr_df = pd.read_csv(curr_df_name)
    pickup_dates = (curr_df['tpep_pickup_datetime'] >= date_0) & (curr_df['tpep_pickup_datetime'] < date_1)
    desired_df = curr_df[pickup_dates]
    print(desired_df.count())
    all_files.append(desired_df)
    #print(desired_df.iloc[0])
    #df_main.append(desired_df.iloc[0:])
    #print(curr_df[pickup_dates].keys())
    #df_main.append(curr_df[pickup_dates])
    if month == 6:
        print("done.")
        #df_main.to_csv(r'F:\CS405_Data_Visualization\nyc.2017-01to06.csv')

# combine all files in the list
combined_csv = pd.concat(all_files)     # Combining all 6 months of data
# export to csv
combined_csv.to_csv("nyc.2017-combined.csv", index=False, encoding='utf-8-sig')     # Exporting as CSV for later use
"""

df = pd.read_csv('nyc.2017-01.csv')

df_taxi_zones = pd.read_csv(config['existing_locations_csv'])
list_of_locations = {value: {"lat": df_taxi_zones['Y'][index], "lon": df_taxi_zones['X'][index]}
                     for index, value in enumerate(df_taxi_zones['zone'])}
locations_dict = {df_taxi_zones['zone'][index]: df_taxi_zones['LocationID'][index] for index, _ in
                  enumerate(df_taxi_zones['zone'])}

# Colors for items in page
colors = {
    'background': '#222222',
    'text': '#ECF0F1',
    'header': '#FF9800'
}

df['tpep_pickup_datetime'] = pd.to_datetime(df['tpep_pickup_datetime'], format="%Y-%m-%d %H:%M:%S")

fig = px.scatter_mapbox(df_taxi_zones, lat="Y", lon="X", hover_name="zone", hover_data=["LocationID", "borough"],
                        color_discrete_sequence=["orange"], zoom=10, height=600)
fig.update_layout(mapbox_style="dark", mapbox_accesstoken=accsesstoken_mapbox)
fig.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0})

# Dash

# urllib.request.urlretrieve("https://codepen.io/chriddyp/pen/bWLwgP.css", "data_vis.csv".)
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(

    children=[
        html.Section(
            style={
                'width': '100%',
                'height': '100%',
                'background-color': colors['background']
            },
            children=[
                # Left Side
                html.Div(
                    id='left_container',
                    children=[
                        html.H1(
                            children='CS405 - Visualization Project',
                            style={
                                'font-family': '-apple-system, BlinkMacSystemFont, sans-serif;',
                                'textAlign': 'center',
                                'color': colors['header'],
                                'margin': '30px'
                            }
                        ),
                        html.Div(
                            children='made by Yagiz Ismet Ugur',
                            style={
                                'font-family': '-apple-system, BlinkMacSystemFont, sans-serif;',
                                'textAlign': 'center',
                                'color': colors['text']
                            }),
                        html.H2("NY Taxi Trip", style={
                            'font-family': '-apple-system, BlinkMacSystemFont, sans-serif;',
                            'textAlign': 'center',
                            'color': colors['header'],
                            'margin': '30px'

                        }),

                        html.Div(
                            className="dropdown_date",
                            children=[
                                dcc.DatePickerSingle(
                                    id="datepicker",
                                    min_date_allowed=datetime.datetime(df['tpep_pickup_datetime'].min().year,
                                                                       df['tpep_pickup_datetime'].min().month,
                                                                       df['tpep_pickup_datetime'].min().day),
                                    max_date_allowed=datetime.datetime(df['tpep_pickup_datetime'].max().year,
                                                                       df['tpep_pickup_datetime'].max().month,
                                                                       df['tpep_pickup_datetime'].max().day),
                                    initial_visible_month=datetime.datetime(df['tpep_pickup_datetime'].min().year,
                                                                            df['tpep_pickup_datetime'].min().month,
                                                                            df['tpep_pickup_datetime'].min().day),
                                    date=datetime.datetime(df['tpep_pickup_datetime'].min().year,
                                                           df['tpep_pickup_datetime'].min().month,
                                                           df['tpep_pickup_datetime'].min().day).date(),
                                    display_format="MMMM D, YYYY",
                                    style={"border": "0px solid black", "margin": "200px", "align-content": "center",
                                           "width": "50%"},

                                )
                            ]
                        ),

                    ],
                    style={
                        'width': '40vh',
                        'height': '100vh',
                        'float': 'left',
                        'background-color': colors['background']
                    }),

                # Right Side
                html.Div(
                    id='right_container',
                    children=[
                        html.H2(
                            children='NYC Yellow Trip Data Table(2017)',
                            style={
                                'color': colors['header'],

                                'font-family': '-apple-system, BlinkMacSystemFont, sans-serif;',
                                'margin-left': '30px',
                                'margin-right': '30px',
                                'text-decoration': 'underline solid'
                            }
                        ),

                        # TODO: IDEAS --> Aylara gore total odeme dagilimlari
                        # generate_scatter_graph(df)
                        html.Div(
                            children=[
                                html.Div([html.H1("Scatter Graph")],
                                         style={"text-align": "center", "color": colors['header'],
                                                "backgorund-color": colors['background']}),
                                html.Div(dcc.Graph(id="myScatterGraph"),
                                         style={"background-color": colors['background']}),
                                # html.Div([dcc.RangeSlider(id="month-slider", min=1, max=df['tpep_pickup_datetime'].max().month, marks={
                                #    1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug',
                                #    9: 'Sep',
                                #    10: 'Oct', 11: 'Nov', 12: 'Dec'
                                # }, value=[1, 2])], style={"margin": "20", "padding": "20"})
                            ]),

                        html.Div(
                            children=[
                                dcc.Graph(id="map-graph", figure=fig),
                                # dcc.Graph(id="histogram"),
                                # dcc.Graph(id="doughnut-chart")
                            ]

                        )

                        # TODO: IDEAS --> Aylara gore tip dagilimlari

                        # TODO: IDEAS --> Aylara gore trip distancelar

                        # TODO: IDEAS -->

                        # TODO: Call Graph Function Here.

                        # generate_figure(df_1, len(df_1))
                    ],
                    style={
                        'background-color': '#444444',
                        # 'margin-left': '40vh',
                        'height': '100vh',
                        'width': 'auto',
                        # 'width': '70vh'
                        'overflow': 'scroll',
                    }),
            ]),

    ])


@app.callback(
    dash.dependencies.Output('myScatterGraph', 'figure'),
    [dash.dependencies.Input('datepicker', 'date')])
def update_figure(selected_date):
    selected_date = pd.to_datetime(selected_date, format="%Y-%m-%d")
    pd.options.mode.chained_assignment = None
    data = df
    date_range_output = data[
        (data['tpep_pickup_datetime'] >= selected_date) & (data['tpep_pickup_datetime'] <= selected_date)]

    figure1 = go.Scatter(
        y=date_range_output['total_amount'],
        x=date_range_output['tpep_pickup_datetime'],
        mode='markers',
        marker={"size": 6, "color": "#FF9800"
                },
        name="Total amount",

    ),

    return go.Figure(data=figure1)


if __name__ == '__main__':
    app.run_server(debug=True)
