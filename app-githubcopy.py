import dash_html_components as html
import dash_core_components as dcc
import dash
from flask import send_file
import plotly.graph_objs as go
import pyodbc

import plotly
import dash_table as dte
from dash.dependencies import Input, Output, State


import pandas as pd
import numpy as np

import json
import datetime
import operator
import os
import sqlite3

import base64
import io
import time 
import re
import pickle
from itertools import chain
from modelcleaning1 import modelcleaning1
from modeleligibility1 import *

from NEWSpro import *

import warnings



warnings.simplefilter(action='ignore', category=FutureWarning)



# Set the global font family
FONT_FAMILY = 'Roboto-Medium'

# set the tab styles
tabs_styles = {
    'height': '40px',
    'fontSize': '18px',
    'fontWeight': 'bold'

}
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontSize': '18px',
    'font_family': FONT_FAMILY,
    'fontWeight': 'bold'
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#124469',
    #'backgroundColor': '#F4F4F8',
    'opacity': '0.8',
    'font_size': '18px',
    'font_family': FONT_FAMILY,
    'color': 'white',
    'padding': '6px'
}


# initialise the DASH app
app = dash.Dash(__name__)


# import logos

# change location to assets folder location

image_filename = r'C:\Users\Amber\Anaconda3\envs\Pro\assets\b.jpg' 
image_filename1 = r'C:\Users\Amber\Anaconda3\envs\Pro\assets\hf.jpg' 




encoded_image = base64.b64encode(open(image_filename, 'rb').read())
encoded_image1 = base64.b64encode(open(image_filename1, 'rb').read())



# run locally

app.scripts.config.serve_locally = True

app.config['suppress_callback_exceptions'] = True

# app layout

app.layout = html.Div([


    html.Div([   
        
    html.Div(
    className="app-header",
    children = [
        
    html.Div([
    html.Img(src='data:image/jpg;base64,{}'.format(encoded_image.decode()),style={'width': '135%', 'display': 'inline-block'})], className= "three columns",style={'margin-right': '200px'}),
        

     
    html.Div([
    html.Div([html.P("Enter attendance ID")] , style= {'margin-top': '10px', 'font-size': '16px'}, className= "two columns"),
        
    html.Div(dcc.Input(id='input-att_id', value='', inputmode= 'str', placeholder= 'enter ID', 
             style = {'height': '30px', 'font-size': '14px', 'width': '100px', 'text-align': 'center', 'border': '3px solid #f2f2f2'}),className= "two columns", style={'margin-left': '-2px', 'margin-top': '10px'}),
    
    html.Div([html.Button(id='propagate-button', n_clicks=0, children='Calculate scores')],className= "two columns", style={'margin-top': '10px', 'margin-left': '-10px', 'margin-right': '50px'}),
        
        
        html.Div([html.Button(id='propagate-button1', n_clicks=0, children='Reset')],className= "two columns", style={'margin-top': '10px', 'margin-left': '30px'})
        
    ]),
        
        
    
    ]
    
    ),
        
    ]),
    
        

    
    html.Br(),
    
       
    
    
    
    html.Div([
    
    html.Div([  # content div
            html.Div(id='tes')]  ,style= {'margin-top': '2px', 'font-size': '24px'}),

                    ],),
    
    html.Div(id='wholepage', children=[
    
    dcc.Tabs(id="tabs", children=[
        
    dcc.Tab(label='Summary',style=tab_style, selected_style=tab_selected_style, 
    children=[
        
    html.Div([

    html.Div([
    html.Br(),
    html.H6("NEWS 2"),
    
    html.Div([
    html.Div([html.H1(id="news_text")],id='news',    
                                    style={'textAlign': 'center', 'width': '200px', 'height': '70px', 'border-top': '4px solid #31B89C'},
                                    className="mini_container",
            )], 
        className= 'three columns')], 
        className="three columns"),
        
        
    html.Div([
    html.Br(),
    html.H6("Admissions (last 28 days)"),
    
    html.Div([
    html.Div([html.H1(id="prev_text")], id='prev',    
                                    style={'textAlign': 'center', 'width': '200px', 'height': '70px', 'border-top': '4px solid #31B89C'},
                                    className="mini_container",
                        )], className= 'three columns')], className="three columns"),
    
    html.Div([
    html.Br(),
    html.H6("Attendances (last 28 days)"),
    
    html.Div([
    html.Div([html.H1(id="att_text")],  id='attend',   
                                    style={'textAlign': 'center', 'width': '200px', 'height': '70px', 'border-top': '4px solid #31B89C'},
                                    className="mini_container",
                        )], className= 'three columns')], className="three columns"),
        
        
    html.Div([
    html.Br(),
    html.H6("Admission probability"),
    
    html.Div([
    html.Div([html.H1(id="admit_text")], id='admit',
             
                                   style={'textAlign': 'center', 'width': '200px', 'height': '70px', 'border-top': '4px solid #31B89C'},
                                    className="mini_container",
)], className= 'three columns')],className="three columns")]
        
        
      , className="row"),
    
    html.Div([
        
        
    html.Div([
        



    html.Br(),
    html.Div(
        id="graph-container1", 
        children = [
            dcc.Graph(
                    id='example-graph-1', config={'staticPlot': True},
                )] # graph1, children
                    
                 )], className="six columns"),


    
    html.Div([
    html.Div(id="graph-container2",
              children = [
      dcc.Graph(
                id='example-graph-2', config={'staticPlot': True},), ]
            )], className="six columns", style ={'margin-top': '-450px', 'margin-left': '600px'})
    
    ], className="row"),
        
    html.Div(
    children = [ html.Div([
    html.Img(src='data:image/jpg;base64,{}'.format(encoded_image1.decode()),style={'opacity': 0.4, 'width': '100%', 'display': 'inline-block'})], className= "three columns",style={'margin-right': '200px', 'margin-top' : '100px'}),
      ]),
    
    html.Div([dcc.Markdown(id='output-container-button')], style ={'textAlign': 'left', 'fontFamily': FONT_FAMILY, 'backgroundColor': '#d5f5e3'}),
        html.Div([dcc.Markdown(id='output-container-button1')], style ={'textAlign': 'left', 'fontFamily': FONT_FAMILY, 'backgroundColor': '#d5f5e3'}),
        html.Div(id='test',style= {'display':'none'})
        

        ]),
        

        
    ], style=tabs_styles) # dcc.Tabs
    
    ], style = {'display': 'block'}),
], className="page") # app.layout


# functions
    
@app.callback(
    [Output(component_id='news_text', component_property='children'),
     Output(component_id='prev_text', component_property='children'),
     Output(component_id='att_text', component_property='children'),
     Output(component_id='admit_text', component_property='children'),
     Output(component_id='test', component_property='children'),
     Output(component_id='tes', component_property='children'),

     Output('example-graph-1', 'figure'),
     Output('example-graph-2', 'figure')],
    [Input(component_id='propagate-button', component_property='n_clicks')],
    [State(component_id='input-att_id', component_property='value')])


def update_output_div(n_clicks,att_id):
    if n_clicks >=1:
        
    # Connect to database using either pyodbc for a SQL Server, or sqlite3 for local db
    # pyodbc for external
    
        '''conn_global = pyodbc.connect()

        query = ""
        df = pd.read_sql_query(query, conn_global)'''

        
        # local test db
        conn_global = sqlite3.connect("C:\\Users\\Amber\\desktop\\Update News\\NEWStest.db")


        
        df = pd.read_sql_query("SELECT pas_id, arrival_mode, referral_source, age, gcs, respiratory_rate, heart_rate, saturation_o2, attendance_365d, attendance_28d, attendance_7d, admittance_7d, admittance_28d, admittance_365d, temperature, gender, blood_pressure_systolic, blood_pressure_diastolic, pain_score,recorded_outcome, complaint, arrival_dttm, triage_notes  FROM NEWStest WHERE pas_id = '{}'".format(att_id), conn_global)

# close database
        conn_global.close()
    
    

# if the dataframe is not empty, ie. if id exists, clean dataframe
        if df.empty:
        
            
            f = 'Attendance ID not found, please check and try again'
        
        if not df.empty:
            f = 0
            df = modelcleaning1(df)
            
            # results are tuple with admit prob, lime dataframe, admittance/attendance dataframe
            q = modeleligible1(df)
            
            if len(q) >1:
            
                # create colour field
                q[1]['colour'] = ((q[1]['Rank']>0)).astype('int')

                # create dictionary with 2 colours
                color_dict = {'0':'#31B89C', '1':'red'}
                colors = np.array([''] * 5, dtype = object)

                for i in np.unique(q[1]['colour']):

                    colors[np.where(q[1]['colour'] == i)] = color_dict[str(i)]
            else:
                
                pass

            # insert piece to add admissions necessary to other database here
            
            
            
                        
            # if we have at least one value in the tuple, it will be the admittance/attendance
            # y is the total admittances, w is the attendances, z is the admit prob
            
            if len(q) > 1:
                y = q[2]['admittance_28d']
                w = q[2]['attendance_28d']
                
             # q[0] is the admission probability
            
                z = np.round(q[0],2)
                
                if z[0] >= 0.44:
                    h = 'Likely'
                else:
                    h = 'unlikely'
                h = "{:.0%}".format(z[0])
                
                
             # do lime graph
                
                yrange2 = (-0.6,0.6)   
            
                figure2={
                   'data': [
                       {'y':q[1]['Feature'], 'x': q[1]['Rank'],
                            'orientation': 'h', 'type': 'bar', 'mode': 'markers+text', 'text': q[1]['Word'], 
                        'textfont':{'color': 'white'},
                         'textposition': 'auto', "marker" : {'size': 50,'color': colors, 'opacity': 0.8}},
                                                 
             #   'colorscale':[[0, '#31B89C'], [1, 'red']]}, 'opacity': 0.8},




                    ],            
                'layout': {
                    'title': 'Criteria admission probability based on',
                    'plot_bgcolor': '#f9f9f9',
                    'margin': {'l': 150, 'pad': 4},
                    'color': '#00a0db',
                    'xaxis':{'showline': 'False', 'showgrid': 'False', 'gridcolor': '#f9f9f9', 'range': yrange2, 'title': 'Contribution', 'tickvals':[-0.3, 0.5],'ticktext':['No admission', 'Admission']},

                    'yaxis':{'showline': 'False', 'showgrid': 'False', 'gridcolor': '#f9f9f9',  'autorange':'reversed',
                    'dtick': 0.2},
                    'paper_bgcolor': '#f9f9f9',
                    'font': {
                        'color': 'black'
                    },

                }
                            }
                
             
            # if we do not have all 3 variables, we just have attendance 
            # admit probability is n/a
            
            else:
                y = q['admittance_28d']
                w = q['attendance_28d']
                z = 'N/A*'
                h = 'N/A*'
                f = 0
                figure2 = {}
             
                
            
            news = df.copy()
            

                
            a = NEWS_DASH(news)
            
            
          
            yrange1 = (0,4)
            yrange2 = (0,6)
            
            
            if not a[2].empty:

                figure1={
                'data': [
                    {'x': a[2]['final'], 'y': a[2]['vals'],
                        'type': 'scatter', 'mode': 'markers+text', 'text': a[2]['vals2'],
                     'textposition': 'auto', 'marker': {'size': 70}, 'opacity': 0.8},


                ],            
            'layout': {
                'title': 'Abnormal NEWS 2 variables',
                'plot_bgcolor': '#f9f9f9',
                'color': '#00a0db',
                'xaxis':{'showline': 'False', 'showgrid': 'False', 'gridcolor': '#f9f9f9'},
                'yaxis':{'showline': 'False', 'showgrid': 'False', 'gridcolor': '#f9f9f9',
                'dtick': 1, 'title': 'NEWS', 'range': yrange1},
                'paper_bgcolor': '#f9f9f9',
                'font': {
                    'color': 'black'
                },

            }
                        }
                
                
                
            else:
                d = {'news': [2], 'vals': [1], 'vals2': [''], 'final': ['']}
                dfa = pd.DataFrame(data=d)
                
                figure1={
                'data': [
                    {'x': dfa['final'], 'y': dfa['vals'],
                        'type': 'scatter', 'mode': 'markers+text', 'text': dfa['vals2'],
                     'textposition': 'top', 'marker': {'color': '#f9f9f9', 'size': 70}, 'opacity': 1},


                ],            
            'layout': {
                'title': 'No abnormal NEWS 2 variables',
                'plot_bgcolor': '#f9f9f9',
                'color': '#f9f9f9',
                'xaxis':{'zeroline': 'False', 'showgrid': 'False', 'gridcolor': '#f9f9f9'},
                'yaxis':{'zeroline': 'False', 'showgrid': 'False', 'gridcolor': '#f9f9f9',
                'dtick': 1, 'range': yrange1},
                'paper_bgcolor': '#f9f9f9',
                'font': {
                    'color': 'black'
                },

            }
                        }
            
                
            if z == 'N/A*':
                figure2 = {
            'data': [
                {'x': a[3]['vals'], 'y': a[3]['Missing data'], 
                    'type': 'scatter', 'mode': 'markers+text', 'text': a[3]['Missing data'],
                 'textposition': 'right', 'textfont': {'color': 'black'}, 'marker': {'size': 50, 'color': ((a[3]['vals'] == 1)).astype('int'),
        'colorscale':[[0, '#f9f9f9'], [1, '#31B89C']]}, 'opacity': 0.9},


            ],   
         
       
        
        'layout': {
            'title': 'The following variables are missing',
            'plot_bgcolor': '#f9f9f9',
            'margin': {'l': 0, 'r': 0, 'b': 0, 't': 70},
            'color': '#00a0db',
            'xaxis':{'showline': 'False', 'showgrid': 'False', 'gridcolor': '#f9f9f9', 'range': yrange2},
            'yaxis':{'showline': 'False', 'showgrid': 'False', 'gridcolor': '#f9f9f9', 'autorange' : 'reversed'},
            'paper_bgcolor': '#f9f9f9',
            'font': {
                'color': 'black'
            },

        }
                    }
                
            if len(a[1]) == 7:
                figure1 = {}


                return 'N/A*', y, w, h, z[0], f,figure1, figure2
            
            else:
                return a[0], y, w, h, z[0],f, figure1, figure2



        else:
            return '','','','','',f,{},{}
        
        
    else:
        return '','','','','','Finding results...', {},{}

    
# ccallback to show or hide graphs
@app.callback([Output('graph-container1', 'style'),
              Output('graph-container2', 'style')],
                [Input('propagate-button', 'n_clicks'),
                Input('admit_text', 'children')])

def hide_graph(n_clicks, vals):
    if n_clicks >=1:
        return [{'display':'block'}, {'display':'block'}]

    else:
        return [{'display':'none'}, {'display':'none'}]




# callback to format cards with colour
@app.callback(Output('admit_text', 'style'),
                [Input('propagate-button', 'n_clicks'),
                Input('test', 'children')])

def colours(n_clicks, test):
    if n_clicks>=1:
        if test is not None:
            if type(test) is float:
                if test >= 0.44:
                    return {'color':'red', 'opacity': 0.8}
                return {'color':'black'}
    pass

# callback to hide page when id not found
@app.callback([Output('tes', 'style'),
              Output('wholepage', 'style')],
                [Input('propagate-button', 'n_clicks'),
                Input('tes', 'children')])

def no_id(n_clicks,tes):
    if n_clicks>=1:
        
        if tes is None or tes ==0:
            return [{'display': 'none'}, {'display': 'block'}]
        
      #   if tes != 0 and tes is not None:
       #     return  [{'display': 'block', 'textAlign': 'center', 'margin-bottom': '10px'}, {'display': 'none'}]
        
        else:
            
      #  if tes is None:
            return [{'display': 'block', 'textAlign': 'center', 'margin-bottom': '10px'}, {'display': 'none'}]
          #  return [{'display': 'none'}, {'display': 'block'}]
        
    else:
        return [{'display': 'none'}, {'display': 'block'}]


# clear results       
@app.callback([Output('propagate-button','n_clicks'),
              Output('input-att_id', 'value')],
              [Input('propagate-button1','n_clicks')],
              [State(component_id='propagate-button', component_property='n_clicks')])
def update(reset, button):
    if reset >=1:
        return 0, ''
    
    elif button ==0 & reset ==0:
        return 0, ''
    else:
        return 1, ''





app.css.append_css({"external_url": "static/stylepro.css"})

app.css.append_css({"external_url": "static/undopro.css"})

app.css.append_css({"external_url": "static/headerpro.css"})


if __name__ == '__main__':
    app.run_server(debug=True)