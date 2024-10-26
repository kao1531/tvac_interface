# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.


from dash import Dash, dcc, html, Input, Output, ctx, callback, MATCH, State, ALL
# import plotly.express as px
import pandas as pd
from collections import deque
import random
import plotly.graph_objs as go
import json
import os
# import RPi.GPIO as GPIO
import time
from datetime import datetime
# from max31855.max31855 import MAX31855, MAX31855Error
import csv


app = Dash(__name__)

# create CSS file that will make it look better

# define some constants

# line graph colors
tc_colors = ['red', 'blue', 'green', 'yellow', 'purple', 'orange', 'pink', 'cyan', 'black', 'brown',
             'grey', 'lime', 'navy', 'maroon', 'silver', 'teal']

# maximum number of points to show at a time on the plot
MAX_LEN = 20

# number of thermocouples
NUM_TC = 16

# H1 temp threshold
H1_TEMP = 23

# RPi setup
# mux selects
A3 = 17
A2 = 16
A1 = 27
A0 = 26
# D = pin 3 of TC reader

# TC reader
CS = 24
SO = 22
SCK = 23

# Heater control
H1 = 12
H2 = 13
LN2 = 18

# thermocouple = MAX31855(CS, SCK, SO)

# GPIO.setmode(GPIO.BOARD)
# GPIO.setup(A3, GPIO.OUT)
# GPIO.setup(A2, GPIO.OUT)
# GPIO.setup(A1, GPIO.OUT)
# GPIO.setup(A0, GPIO.OUT)

# GPIO.setup(H1, GPIO.OUT)
# GPIO.setup(H2, GPIO.OUT)
# GPIO.setup(LN2, GPIO.OUT)
# GPIO.setup(CS, GPIO.OUT)
# GPIO.setup(SO, GPIO.OUT)
# GPIO.setup(SCK, GPIO.OUT)


app.layout = html.Div([
    # time interval
    dcc.Interval(id='int-comp', interval=1000, n_intervals=0),

    # TC data store
    dcc.Store(id='tc-data-store', data={'time': [], 
                                        'ln2-object-target': [],
                                        'h2-object-target': [],
                                        'ln2-temp': [],
                                        'h2-temp': [],
                                        'h2-max': [],
                                        'over-temp': [],
                                        'shroud-min': [],
                                        'h1-temp': [],
                                        'obj-tc-btns': ["off"] * 16,
                                        'h2-tc-btns': ["off"] * 16,
                                        'ln2-tc-btns': ["off"] * 16,
                                        'over-temp-tc-btns': ["off"] * 16,
                                        'pass-through-min': [],
                                        'pass-through-max': [],
                                        **{f'{i+1}': [0] for i in range(NUM_TC)}}),

    # top half
    html.Div([html.Table(
                [html.Caption("Heater Control State"),
                
                # Body
                html.Tr([
                    html.Td(html.Button('', id='heater-override-out', disabled=True, title='Override',
                                        style={'background-color': "grey",
                                            'height': "6.5vh",
                                            'width': "6.5vh",
                                            'border-radius': "100%"})),
                    html.Td([html.H4("Override")],
                            style={'margin': "2vh",
                                'padding': "1vh"}),

                    html.Td(html.Button('', id='heater-max-out', disabled=True, title='Max',
                                        style={'background-color': "grey",
                                            'height': "6.5vh",
                                            'width': "6.5vh",
                                            'border-radius': "100%"})),
                    html.Td([html.H4("Max")],
                            style={'margin': "2vh",
                                'padding': "1vh"})]),

                html.Tr([
                    html.Td(html.Button('', id='heater-over-temp-out', disabled=True, title='Over Temp',
                                        style={'background-color': "grey",
                                            'height': "6.5vh",
                                            'width': "6.5vh",
                                            'border-radius': "100%"})),
                    html.Td([html.H4("Over Temp")],
                            style={'margin': "2vh",
                                'padding': "1vh"}),
                                
                    html.Td(html.Button('', id='heater-@-target-out', disabled=True, title='@ Target',
                                        style={'background-color': "grey",
                                            'height': "6.5vh",
                                            'width': "6.5vh",
                                            'border-radius': "100%"})),
                    html.Td([html.H4("@ Target")],
                            style={'margin': "2vh",
                                'padding': "1vh"})])],
                                
                style={'border': "2px solid black",
                       'margin-left': "30vw",
                       'padding' : "1vh"}
            ),

            html.Table(
                [html.Caption("LN2 Control State"),
                
                # Body
                html.Tr([
                    html.Td(html.Button('', id='ln2-override-out', disabled=True, title='Override',
                                        style={'background-color': "grey",
                                            'height': "6.5vh",
                                            'width': "6.5vh",
                                            'border-radius': "100%"})),
                    html.Td([html.H4("Override")],
                            style={'margin': "2vh",
                                'padding': "1vh"}),

                    html.Td(html.Button('', id='ln2-shroud-lim-out', disabled=True, title='Shroud Lim',
                                        style={'background-color': "grey",
                                            'height': "6.5vh",
                                            'width': "6.5vh",
                                            'border-radius': "100%"})),
                    html.Td([html.H4("Shroud Lim")],
                            style={'margin': "2vh",
                                'padding': "1vh"})]),

                html.Tr([
                    html.Td(html.Button('', id='ln2-@-target-out', disabled=True, title='@ Target',
                                        style={'background-color': "grey",
                                            'height': "6.5vh",
                                            'width': "6.5vh",
                                            'border-radius': "100%"})),
                    html.Td([html.H4("@ Target")],
                            style={'margin': "2vh",
                                'padding': "1vh"})])],

                style={'border': "2px solid black",
                       'padding' : "1vh"}
            ),

            html.Button('E-Stop', id='btn-estop', n_clicks=0,
                        style={'height': "9vh", 
                            'background-color': "rgb(140,20,11)",
                            'color': "white",
                            'font-size': "3vh",
                            'padding:': "1vh 1vh",
                            'margin-left': "15vw",
                            'clip-path': 'polygon(30% 0%, 70% 0%, 100% 30%, 100% 70%, 70% 100%, 30% 100%, 0% 70%, 0% 30%)',}
            ),

        ], 
        style={'display': "flex",
                'flex-direction': "row",
                'justify-content': "flex-start",
                'align-items': "center"}),

    # add some space in between top and bottom
    html.Div(style={'height': "5vh"}),

    # bottom half
    html.Div([ 
        # left panel
        html.Div([
            html.Button('LN2 Status', id='btn-ln2-status', disabled=True,
                        style={
                            'height': "7vh", 
                            'width': "7vw",
                            'background-color': "rgb(20,82,29)",
                            'color': "white",
                            'font-size': "2vh",
                            'margin': "1vh 1vh"
                        }),
            html.Button('H1 Status', id='btn-h1-status', disabled=True,
                        style={
                            'height': "4vh",  
                            'width': "10vw",
                            'background-color': "rgb(140,20,11)",
                            'color': "white",
                            'font-size': "2vh",
                            'margin': "0.5vh 1vh"
                        }),
            html.Table([
                html.Tr([
                    html.Td(
                        html.Div(id="shroud-temp-out", style={'margin-bottom': "1vh", 'border': "2px solid black", 'padding': "0px 1vw", 'margin-bottom': '0.5vh'}),
                        style={'margin': "3vh auto", 'padding': "1vh"})
                ], style={'text-align': "center"}),
                html.Tr([
                    html.Td(
                        html.H4("TVAC Representation"),
                        style={'margin': "2vh auto", 'padding': "1vh", 'text-align': "center", 'color': "white"})
                ]),
                html.Tr([
                    html.Td(
                        html.Div(id="obj-temp-out", style={'margin-bottom': "1vh", 'border': "2px solid black", 'padding': "0px 1vw", 'margin-bottom': '0.5vh'}),
                        style={'margin': "5vh auto", 'padding': "1vh", 'text-align': "center"})
                ]),
                html.Tr([
                    html.Td(
                        html.Div(id="heater-temp-out", style={'margin-bottom': "1vh", 'border': "2px solid black", 'padding': "0px 1vw", 'margin-bottom': '0.5vh'}),
                        style={'margin': "0vh auto", 'padding': "1vh", 'text-align': "center"})
                ]),
                html.Tr(
                    html.Td(
                        html.Button('Heater Status', id='btn-heater-status', disabled=True,
                        style={
                            'height': "3vh", 
                            'width': "10vw",
                            'background-color': "rgb(140,20,11)",
                            'color': "white",
                            'font-size': "2vh",
                            'margin': "0vh auto"
                        }), style={'text-align': 'center', 'width': '100%'}
                    )
                ),
            ], style={'margin': '0 auto', 'border': "4px solid rgb(207, 207, 207)", 'background-color': "grey", 'width': "16vw"}),   
        ],
        style={
            'display': "flex",
            'flex-direction': "column",
            'justify-content': "center",
            'align-items': "center",  # Center elements horizontally
            'width': "20vw",
            'padding': "3vh 3vw",
            #'border': "2px solid green"
        }),

        # tabs panel
        html.Div([
            dcc.Tabs(id="tabs", value='status-tab', children=[
                dcc.Tab(label='Status', value='status-tab'),
                dcc.Tab(label='Override', value='override-tab'),
                dcc.Tab(label='Temp', value='temp-tab'),
                dcc.Tab(label='Logging', value='logging-tab'),
            ], colors={
                "border": "white",
                "primary": "gold",
                "background": "cornsilk"
            }, style={'width': "69vw"}),

            # status tab
            html.Div([
                dcc.Graph(id='status-plot', style={'border': "2px solid black", 'width': '37vw', 'margin-right': "1vw", 'height': "55vh"}, 
                          config={'displayModeBar': False}),
                dcc.Checklist(
                    id="tc-select-panel",
                    options=[
                        {
                            "label": [html.Span(f"TC{i+1}", style={"font-size": "2.3vh", "padding-left": '0.5vw', 'width': "3.2vw"}),
                                    html.Div('', style={'height': "2vh", 'width': "2vw", 'background-color': color}),
                                    html.Div(id=f'tc{i+1}-out', style={"font-size": "2vh", "padding": '0px 1vw', 'background-color': "rgb(180,180,180)",
                                                                 "border": '2px solid black', "margin-left": '2vw', "width": "2vw",
                                                                 "margin-top": '0.5vh', "margin-right": '3vw'})],
                            "value": f"{i+1}"
                        } for i, color in enumerate(tc_colors)
                    ],
                    labelStyle={"display": "flex", "align-items": "center"}
                ),
                    
                html.Div([
                    html.Table([
                        html.Tr([html.Th("TC"), html.Th("Location")]),
                        html.Tbody([
                            html.Tr([
                                html.Td(f"{i+1}", style={'width': '2vw'}),  
                                html.Td(dcc.Input(id=f'location-{i+1}-in', type='text', placeholder=f'Location {i+1}', style={'width': '11vw'}))  
                            ]) for i in range(NUM_TC)
                        ])  
                    ], style={'border': '1px solid black', 'table-layout': 'fixed'})  
                ]),
            ], id='status-content', style={'display': "none"}),

            # override tab
            html.Div([
                html.Table([
                    html.Tr([
                        html.Td(html.H4("H1 Override"),
                                style={
                                    'text-align': 'center',  # Center the content inside the cell
                                    'display': 'flex',
                                    'justify-content': 'center',
                                    'align-items': 'center'
                                })
                    ]),

                    html.Tr([
                        html.Td(html.Button('', id='btn-h1-override-toggle',
                            style={
                                'height': "10vh", 
                                'width': "10vh",
                                'background-color': "grey",
                                'border-radius': "100%",
                                'border': '2px solid black',
                            }),
                            style={
                                'text-align': 'center',  # Center the button inside the cell
                                'display': 'flex',
                                'justify-content': 'center',
                                'align-items': 'center'
                            }
                        )
                    ]),

                    html.Tr([
                        html.Td(html.H4("Override toggle"),
                                style={
                                    'text-align': 'center',
                                    'margin': "1vh",
                                    'display': 'flex',
                                    'justify-content': 'center',
                                    'align-items': 'center'
                                })
                    ]),

                    html.Tr([
                        html.Td(html.Button('', id='btn-h1-override-on-off', disabled=True,
                            style={
                                'height': "10vh", 
                                'width': "10vh",
                                'background-color': "grey",
                                'border-radius': "100%",
                            }),
                            style={
                                'text-align': 'center',
                                'display': 'flex',
                                'justify-content': 'center',
                                'align-items': 'center'
                            }
                        )
                    ]),

                    html.Tr([
                        html.Td(html.H4("On/Off"),
                                style={
                                    'text-align': 'center',
                                    'display': 'flex',
                                    'justify-content': 'center',
                                    'align-items': 'center'
                                })
                    ]),
                ], style={
                    'border': "2px solid black",
                    'width': '100%',
                    'margin': '0 auto'
                }),

            html.Table([
                html.Tr([
                    html.Td(html.H4("Heater Override"),
                            style={
                                'text-align': 'center',
                                'display': 'flex',
                                'justify-content': 'center',
                                'align-items': 'center'
                            })
                ]),

                html.Tr([
                    html.Td(html.Button('', id='btn-heater-override-toggle',
                        style={
                            'height': "10vh",
                            'width': "10vh",
                            'background-color': "grey",
                            'border-radius': "100%",
                        }),
                        style={
                            'text-align': 'center',
                            'display': 'flex',
                            'justify-content': 'center',
                            'align-items': 'center'
                        }
                    )
                ]),

                html.Tr([
                    html.Td(html.H4("Override toggle"),
                            style={
                                'text-align': 'center',
                                'margin': "1vh",
                                'display': 'flex',
                                'justify-content': 'center',
                                'align-items': 'center'
                            })
                ]),

                html.Tr([
                    html.Td(html.Button('', id='btn-heater-override-on-off', disabled=True,
                        style={
                            'height': "10vh",
                            'width': "10vh",
                            'background-color': "grey",
                            'border-radius': "100%",
                        }),
                        style={
                            'text-align': 'center',
                            'display': 'flex',
                            'justify-content': 'center',
                            'align-items': 'center'
                        }
                    )
                ]),

                html.Tr([
                    html.Td(html.H4("On/Off"),
                            style={
                                'text-align': 'center',
                                'display': 'flex',
                                'justify-content': 'center',
                                'align-items': 'center'
                            })
                ]),
            ], style={
                'border': "2px solid black",
                'width': '100%',
                'margin': '0 auto'
            }),
                    
            html.Table([
                html.Tr([
                    html.Td(html.H4("LN2 Override"),
                            style={
                                'text-align': 'center',
                                'display': 'flex',
                                'justify-content': 'center',
                                'align-items': 'center'
                            })
                ]),

                html.Tr([
                    html.Td(html.Button('', id='btn-ln2-override-toggle',
                        style={
                            'height': "10vh",  
                            'width': "10vh",
                            'background-color': "grey",
                            'border-radius': "100%",
                        }),
                        style={
                            'text-align': 'center',
                            'display': 'flex',
                            'justify-content': 'center',
                            'align-items': 'center'
                        }
                    )
                ]),

                html.Tr([
                    html.Td(html.H4("Override toggle"),
                            style={
                                'text-align': 'center',
                                'margin': "1vh",
                                'display': 'flex',
                                'justify-content': 'center',
                                'align-items': 'center'
                            })
                ]),

                html.Tr([
                    html.Td(html.Button('', id='btn-ln2-override-on-off', disabled=True,
                        style={
                            'height': "10vh", 
                            'width': "10vh",
                            'background-color': "grey",
                            'border-radius': "100%",
                        }),
                        style={
                            'text-align': 'center',
                            'display': 'flex',
                            'justify-content': 'center',
                            'align-items': 'center'
                        }
                    )
                ]),

                html.Tr([
                    html.Td(html.H4("On/Off"),
                            style={
                                'text-align': 'center',
                                'display': 'flex',
                                'justify-content': 'center',
                                'align-items': 'center'
                            })
                ]),
            ], style={
                'border': "2px solid black",
                'width': '100%',
                'margin': '0 auto',
                'justify-content': "center",
                'align-items': "center"
            }),
            ],
            id='override-content', style={'display': "none"}),

            # temp tab
            html.Div([
                html.Div([
                   html.Div([
                        html.Div("Pass Through", style={'font-weight': 'bold', 'margin-bottom': '1vh'}),
                        
                        # Label and Input for Max
                        html.Div([
                            html.Label("Max", style={'margin': '0px 0.5vw'}),
                            dcc.Input(id="temp-pass-through-max-in", type="number", debounce=True, placeholder="Max",
                                    style={'margin': "0.5vh 0.5vw", 'width': '6vw'})
                        ], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '0.5vh'}),

                        # Label and Input for Min
                        html.Div([
                            html.Label("Min", style={'margin': '0px 0.5vw'}),
                            dcc.Input(id="temp-pass-through-min-in", type="number", debounce=True, placeholder="Min",
                                    style={'margin': "0.5vh 0.5vw", 'width': '6vw'})
                        ], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '0.5vh'}),
                        
                        # Output div for Temp
                        html.Div("Temp", id='temp-temp-out', style={'margin-bottom': "1vh", 'border': "2px solid black", 'padding': "0px 1vw", 'margin-bottom': '0.5vh'})
                    ], style={'display': "flex", 'align-items': 'center', 'flex-direction': "column", 'border': "2px solid black", 'margin-bottom': "2vh"}),

                    html.Div([
                        html.Div("LN2", style={'font-weight': 'bold', 'margin-bottom': '1vh'}),  # Main section label
                        
                        html.Div([
                            html.Label("Object Target", style={'margin': '0px 0.5vw'}),
                            dcc.Input(id="temp-ln2-object-target-in", type="text", debounce=True, placeholder="Object Target",
                                    style={'margin': "0.5vh", 'width': '6vw'}),
                        ], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '0.5vh'}),
                        
                        html.Div([
                            html.Label("LN2 On Time", style={'margin': '0px 0.5vw'}),
                            dcc.Input(id="temp-ln2-ln2-on-time-in", type="number", debounce=True, placeholder="On Time",
                                    style={'margin': "0.5vh", 'width': '6vw'}),
                        ], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '0.5vh'}),
                        
                        html.Div([
                            html.Label("Shroud Min", style={'margin': '0px 0.5vw'}),
                            dcc.Input(id="temp-ln2-shroud-min-in", type="number", debounce=True, placeholder="Shroud Min",
                                    style={'margin': "0.5vh", 'width': '6vw'}),
                        ], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '0.5vh'}),

                        html.Div(id='temp-shroud-temp-out', style={'border': "2px solid black", 'padding': "0px 1vw", 'width': '10vw', 'margin-bottom': '0.5vh'}),
                    ], style={'display': "flex", 'align-items': 'center','flex-direction': "column", 'border': "2px solid black", 'margin-bottom': "1vh"})
                ], style={'margin-left': "1vw", 'margin-top': "1vh"}),

                html.Div([
                    html.Div([
                        html.Div("Heater", style={'font-weight': 'bold', 'margin-bottom': '1vh'}),  # Main section label
                        
                        html.Div([
                            html.Label("Object Target", style={'margin': '0px 0.5vw'}),
                            dcc.Input(id="temp-heater-object-target-in", type="text", debounce=True, placeholder="Object Target",
                                    style={'margin': "0.5vh", 'width': '6vw'}),
                        ], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '0.5vh'}),
                        
                        html.Div([
                            html.Label("Over Temp", style={'margin': '0px 0.5vw'}),
                            dcc.Input(id="temp-heater-over-temp-in", type="number", debounce=True, placeholder="Over Temp",
                                    style={'margin': "0.5vh", 'width': '6vw'}),
                        ], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '0.5vh'}),
                        
                        html.Div([
                            html.Label("Heater Max", style={'margin': '0px 0.5vw'}),
                            dcc.Input(id="temp-heater-heater-max-in", type="number", debounce=True, placeholder="Heater Max",
                                    style={'margin': "0.5vh", 'width': '6vw'}),
                        ], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '0.5vh'}),

                        html.Div(id='temp-heater-temp-out', style={'border': "2px solid black", 'padding': "0px 1vw", 'width': '10vw', 'margin-bottom': "1vh"}),
                    
                    ], style={'display': "flex", 'align-items': 'center','flex-direction': "column", 'border': "2px solid black", 'margin-bottom': "2vh"}),

                    html.Div([
                        html.Div("Object Temp", id="temp-object-temp-out", style={'margin': "1vh 1vw", 'border': "2px solid black", 'padding': "0px 1vw"}),
                        html.Div("Delta to Hot", id='temp-del-hot-out', style={'margin-bottom': "1vh", 'border': "2px solid black", 'padding': "0px 1vw"}),
                        html.Div("Delta to Cold", id='temp-del-cold-out', style={'margin-bottom': "1vh", 'border': "2px solid black", 'padding': "0px 1vw"}),
                    ], style={'display': "flex", 'align-items': 'center','flex-direction': "column", 'border': "2px solid black",
                              'margin-bottom': "1vh"}),
                ], style={'margin': "1vh 0px", 'margin-left': "1vw"}),

                html.Div([
                    html.Div([
                        html.Div("Object TCs", style={'color': "white", "font-size": "2.5vh", 'margin-left': "1vw"}),  
                        html.Div([
                            html.Div([
                                html.Div(f"TC{i + 1}", style={'width': '4vw', 'text-align': 'center', 'margin-right': '0.5vw', 'color': "white"}),
                                html.Button("", id={'type': 'temp-obj-tc-button', 'index': i}, n_clicks=0,
                                            style={'height': "3vh",
                                                'width': "3vw",
                                                'background-color': "grey",
                                                'border-radius': "30%",
                                                'margin': "1px"})
                            ],
                            style={'display': 'flex', 'align-items': 'center', 'margin': '0px'}) for i in range(NUM_TC)
                        ]) 
                    ], style={'padding': '0px 1vw', 'margin-left': "1vw", 'border': "2px solid black", 'background-color': "rgb(39,68,90)"}),

                    html.Div([
                        html.Div("Heater TCs", style={'color': "white", "font-size": "2.5vh", 'margin-left': "1vw"}),  
                        html.Div([
                            html.Div([
                                html.Div(f"TC{i + 1}", style={'width': '4vw', 'text-align': 'center', 'margin-right': '0.5vw', 'color': "white"}),
                                html.Button("", id={'type': 'temp-heater-tc-button', 'index': i}, n_clicks=0,
                                            style={'height': "3vh",
                                                'width': "3vw",
                                                'background-color': "grey",
                                                'border-radius': "30%",
                                                'margin': "1px"})
                            ],
                            style={'display': 'flex', 'align-items': 'center', 'margin': '0px'}) for i in range(NUM_TC)
                        ]) 
                    ], style={'padding': '0px 1vw', 'border': "2px solid black", 'background-color': "rgb(39,68,90)"}),

                    html.Div([
                        html.Div("Over TCs", style={'color': "white", "font-size": "2.5vh", 'margin-left': "1vw"}),  
                        html.Div([
                            html.Div([
                                html.Div(f"TC{i + 1}", style={'width': '4vw', 'text-align': 'center', 'margin-right': '0.5vw', 'color': "white"}),
                                html.Button("", id={'type': 'temp-over-temp-tc-button', 'index': i}, n_clicks=0,
                                            style={'height': "3vh",
                                                'width': "3vw",
                                                'background-color': "grey",
                                                'border-radius': "30%",
                                                'margin': "1px"})
                            ],
                            style={'display': 'flex', 'align-items': 'center', 'margin': '0px'}) for i in range(NUM_TC)
                        ]) 
                    ], style={'padding': '0px 1vw', 'border': "2px solid black", 'background-color': "rgb(39,68,90)"}),

                    html.Div([
                        html.Div("Shroud TCs", style={'color': "white", "font-size": "2.5vh", 'margin-left': "1vw"}),  
                        html.Div([
                            html.Div([
                                html.Div(f"TC{i + 1}", style={'width': '4vw', 'text-align': 'center', 'margin-right': '0.5vw', 'color': "white"}),
                                html.Button("", id={'type': 'temp-ln2-tc-button', 'index': i}, n_clicks=0,
                                            style={'height': "3vh",
                                                'width': "3vw",
                                                'background-color': "grey",
                                                'border-radius': "30%",
                                                'margin': "1px"})
                            ],
                            style={'display': 'flex', 'align-items': 'center', 'margin': '0px'}) for i in range(NUM_TC)
                        ]) 
                    ], style={'padding': '0px 1vw', 'margin-right': "1vw", 'border': "2px solid black", 'background-color': "rgb(39,68,90)"}),

                ], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '1vh'}),
            ],
            id='temp-content', style={'display': "none"}),
            
            # logging tab
            html.Div([dcc.Input(id="file-path-in", type="text", debounce=True, placeholder="File Path", style={'margin': "1vh auto"}),
            dcc.Input(id="file-name-in", type="text", debounce=True, placeholder="File Name", style={'margin': "1vh auto"}),
            dcc.Input(id="log-freq-in", type="number", debounce=True, placeholder="Logging Frequency", style={'margin': "1vh auto"}),
            html.Table(
                html.Tr([
                    html.Td(html.Button('', id='log-tcs-btn', title='TCs', n_clicks=0,
                                        style={'background-color': "grey",
                                            'height': "6vh",
                                            'width': "6vh",
                                            'border-radius': "100%"})),
                    html.Td([html.H4("TCs", style={'margin-right': "3vw"})],
                            style={'margin': "0px 2vh",
                                'padding': "1vh"}),

                    html.Td(html.Button('', id='log-heater-status-btn', title='Heater Status',
                                        style={'background-color': "grey",
                                            'height': "6vh",
                                            'width': "6vh",
                                            'border-radius': "100%"})),
                    html.Td([html.H4("Heater Status", style={'margin-right': "2vw"})],
                            style={'margin': "2vh",
                                'padding': "1vh"}),

                    html.Td(html.Button('', id='log-ln2-status-btn', title='LN2 Status',
                                        style={'background-color': "grey",
                                            'height': "6vh",
                                            'width': "6vh",
                                            'border-radius': "100%"})),
                    html.Td([html.H4("LN2 Status")],
                            style={'margin': "2vh",
                                'padding': "1vh"})]), style={'margin': "1vh auto"})
                ], id='logging-content', style={'display': "none", 'width': "58vw"})])
    ], 
    style={'display': "flex",'flex-direction': "row",'align-items': "flex-start"})
])


# callback function to control tabs
@callback(
        [Output(component_id='status-content', component_property='style'),
         Output(component_id='override-content', component_property='style'),
         Output(component_id='temp-content', component_property='style'),
         Output(component_id='logging-content', component_property='style')],
        Input(component_id='tabs', component_property='value'))
def render_content(tab):
    if tab == 'status-tab':
        return {'display': "flex",
                'flex-direction': "row",
                'align-items': "flex-start",
                #'border': "2px solid black",
                'width': "70vw"}, {'display': "none"}, {'display': "none"}, {'display': "none"}
    elif tab == 'override-tab':
        return {'display': "none"}, {'display': "flex",
                                    'flex-direction': "row",
                                    'align-items': "flex-start",
                                    #'border': "2px solid black",
                                    'width': "60vw"}, {'display': "none"}, {'display': "none"}
    elif tab == 'temp-tab':
        return {'display': "none"}, {'display': "none"}, {'display': "flex",
                                                            'flex-direction': "row",
                                                            'align-items': "flex-start"}, {'display': "none"}
    elif tab == 'logging-tab':
        return {'display': "none"}, {'display': "none"}, {'display': "none"}, {'display': "flex",
                                                                                'flex-direction': "column",
                                                                                'align-items': "flex-start",
                                                                                #'border': "2px solid black",
                                                                                'width': "60vw"}


# callback function for when E-Stop button is pressed
@callback(
    Output(component_id='btn-estop', component_property='style'),
    Input(component_id='btn-estop', component_property='n_clicks'),
    prevent_initial_call=True
)
def update_estop(n_clicks):
    if n_clicks % 2 == 0:
        return {'height': "9vh", 'background-color': "rgb(140,20,11)", 'color': "white", 'font-size': "3vh", 'padding:': "1vh 1vh", 'margin-left': "15vw",
                    'clip-path': 'polygon(30% 0%, 70% 0%, 100% 30%, 100% 70%, 70% 100%, 30% 100%, 0% 70%, 0% 30%)'}
    else:
        return {'height': "9vh", 'background-color': "red", 'color': "white", 'font-size': "3vh", 'padding:': "1vh 1vh", 'margin-left': "15vw",
                    'clip-path': 'polygon(30% 0%, 70% 0%, 100% 30%, 100% 70%, 70% 100%, 30% 100%, 0% 70%, 0% 30%)'}

# callback function to update deltas
@callback(
    [Output(component_id='temp-del-hot-out', component_property='children'),
     Output(component_id='temp-del-cold-out', component_property='children')],
     [Input(component_id='int-comp', component_property='n_intervals'),
     Input(component_id='temp-heater-temp-out', component_property='children'),
     Input(component_id='temp-shroud-temp-out', component_property='children'),
     Input(component_id='temp-object-temp-out', component_property='children')]
)
def update_delta_temps(n_intervals, heater_temp, shroud_temp, object_temp):
    if type(heater_temp) != type(None) and type(shroud_temp) != type(None) and type(object_temp) != type(None):
        heater_temp_value = float(heater_temp.split("Heater Temp: ")[1].split("°C")[0])
        shroud_temp_value = float(shroud_temp.split("Shroud Temp: ")[1].split("°C")[0])
        object_temp_value = float(object_temp.split("Object Temp: ")[1].split("°C")[0])

        delta_hot = heater_temp_value - object_temp_value
        delta_cold = object_temp_value - shroud_temp_value

        return f"Delta to Hot: {delta_hot:.2f}°C", f"Delta to Cold: {delta_cold:.2f}°C"
    else:
        return "", ""


# callback function to output @ target for heater
@callback(
    [Output(component_id='heater-@-target-out', component_property='style'),
     Output(component_id='temp-object-temp-out', component_property='children'),
     Output(component_id='obj-temp-out', component_property='children')],
    [Input(component_id='int-comp', component_property='n_intervals'),
     Input({'type': 'temp-obj-tc-button', 'index': ALL}, 'n_clicks'),
     Input(component_id='temp-heater-object-target-in', component_property='value'),],
    State(component_id='tc-data-store', component_property='data')
)
def update_heater_at_target(n_intervals, buttons_n_clicks, object_target, store_data):
    selected_tc_values = [
        store_data[f'{i+1}'][-1]  # Get the latest value of each selected TC
        for i in range(NUM_TC)
        if buttons_n_clicks[i] % 2 == 1
    ]
    
    if selected_tc_values:
        average_value = sum(selected_tc_values) / len(selected_tc_values)
    else:
        average_value = 0

    if type(object_target) != type(None) and average_value >= float(object_target):
        return {'background-color': "green", 'height': "6.5vh", 'width': "6.5vh", 'border-radius': "100%", 'border': '2px solid black', 
                'background-color': 'rgb(55,140,77)', 'box-shadow': '0px 0px 3px 3px rgb(62,200,87)'}, f"Object Temp: {average_value:.2f}°C", f"Object Temp: {average_value:.2f}°C"
    else:
        return {'background-color': "grey", 'height': "6.5vh", 'width': "6.5vh", 'border-radius': "100%", 'border': '2px solid black'}, f"Object Temp: {average_value:.2f}°C", f"Object Temp: {average_value:.2f}°C"


# callback function to output @ target for ln2
@callback(
    Output(component_id='ln2-@-target-out', component_property='style'),
    [Input(component_id='int-comp', component_property='n_intervals'),
     Input({'type': 'temp-ln2-tc-button', 'index': ALL}, 'n_clicks'),
     Input(component_id='temp-ln2-object-target-in', component_property='value'),],
    State(component_id='tc-data-store', component_property='data')
)
def update_ln2_at_target(n_intervals, buttons_n_clicks, object_target, store_data):
    selected_tc_values = [
        store_data[f'{i+1}'][-1]  # Get the latest value of each selected TC
        for i in range(NUM_TC)
        if buttons_n_clicks[i] % 2 == 1
    ]
    
    if selected_tc_values:
        average_value = sum(selected_tc_values) / len(selected_tc_values)
    else:
        average_value = 0

    if type(object_target) != type(None) and average_value >= float(object_target):
        return {'background-color': "green", 'height': "6.5vh", 'width': "6.5vh", 'border-radius': "100%", 'border': '2px solid black', 
                'background-color': 'rgb(55,140,77)', 'box-shadow': '0px 0px 3px 3px rgb(62,200,87)'}
    else:
        return {'background-color': "grey", 'height': "6.5vh", 'width': "6.5vh", 'border-radius': "100%", 'border': '2px solid black'}


# callback to save TC locations to file
@callback(
    [Input(f'location-{i+1}-in', 'value') for i in range(NUM_TC)], 
    prevent_initial_call=True
)
def save_tc_location(*values):
    # Create a dictionary with the TC number and corresponding location
    data = {'TC': [i+1 for i in range(NUM_TC)], 'Location': values}
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Define the file path for the CSV
    file_path = 'thermocouples_locations.csv'
    
    # Write the DataFrame to a CSV file
    df.to_csv(file_path, index=False)

    return

# <---------------------------------------------------------------------------------------
# callback function to save store to file
@callback(
    [Input(component_id='int-comp', component_property='n_intervals')],
    [State(component_id='tc-data-store', component_property='data'),
     State(component_id="file-path-in", component_property='value'),
     State(component_id="file-name-in", component_property='value'),
     State(component_id="log-freq-in", component_property='value'),
     State(component_id='log-tcs-btn', component_property='n_clicks'),
     State(component_id='log-heater-status-btn', component_property='n_clicks'),
     State(component_id='log-ln2-status-btn', component_property='n_clicks')]
)
def save_store_data(n_intervals, store_data, file_path, file_name, freq, log_tcs_n_clicks, log_heater_n_clicks, log_ln2_n_clicks):
    if type(freq) != type(None) and n_intervals % int(freq) == 0:
    # Save the store data to a JSON file every 5 seconds for now
        # file_path = 'thermocouple_data.json' # need to update to file path/location in log tab
        keys = []
        if (type(log_tcs_n_clicks) != type(None)) and log_tcs_n_clicks % 2 == 1:
            keys.append("obj-tc-btns")
            keys.append("h2-tc-btns")
            keys.append("ln2-tc-btns")
            keys.append("over-temp-tc-btns")
        if (type(log_heater_n_clicks) != type(None)) and log_heater_n_clicks % 2 == 1:
            keys.append("h2-temp")
        if (type(log_ln2_n_clicks) != type(None)) and log_ln2_n_clicks % 2 == 1:
            keys.append("ln2-temp")

        # need to get all the selected TCs and save the corresponding values
        # or does it mean to just save the average temp
        filtered_data = {key:store_data[key] for key in keys if key in store_data}

        if file_path and file_name:
            save_file = file_path + '/' + file_name
            with open(save_file, 'w') as file:
                # check what data should be stored
                json.dump(filtered_data, file, indent=4)
    return
# ---------------------------------------------------------------------------------------->

# callback function to update TC data displayed
@callback(
    [Output(f'tc{i+1}-out', 'children') for i in range(NUM_TC)],
    Input(component_id="int-comp", component_property='n_intervals'), 
    State('tc-data-store', 'data') 
)
def update_tc_data_out(n_intervals, store_data):
    return [
        f"{store_data[f'{i+1}'][-1]:.2f}" if store_data[f'{i+1}'] else "" 
        for i in range(NUM_TC)
    ]
    

# callback function to update store with new TC data
@callback(
    [Output(component_id='tc-data-store', component_property='data'),
     Output(component_id='heater-over-temp-out', component_property='style'),
     Output(component_id='temp-shroud-temp-out', component_property='children'),
     Output(component_id='shroud-temp-out', component_property='children'),
     Output(component_id='temp-heater-temp-out', component_property='children'),
     Output(component_id='heater-temp-out', component_property='children'),
     Output(component_id='heater-max-out', component_property='style'),
     Output(component_id='ln2-shroud-lim-out', component_property='style'),
     Output(component_id='temp-temp-out', component_property='children'),],
    Input(component_id="int-comp", component_property='n_intervals'),
    [State(component_id='tc-data-store', component_property='data'),
     State(component_id="temp-ln2-object-target-in", component_property='value'),
     State(component_id="temp-heater-object-target-in", component_property='value'),
     State(component_id="temp-ln2-shroud-min-in", component_property='value'),
     State(component_id="temp-heater-over-temp-in", component_property='value'),
     State(component_id="temp-heater-heater-max-in", component_property='value'),
     State({'type': 'temp-over-temp-tc-button', 'index': ALL}, 'n_clicks'),
     State({'type': 'temp-ln2-tc-button', 'index': ALL}, 'n_clicks'),
     State({'type': 'temp-heater-tc-button', 'index': ALL}, 'n_clicks'),
     State({'type': 'temp-obj-tc-button', 'index': ALL}, 'n_clicks'),
     State(component_id="temp-pass-through-max-in", component_property='value'),
     State(component_id="temp-pass-through-min-in", component_property='value')]
)
def update_data_store(n_intervals, data, ln2_obj_target, h2_obj_target, shroud_min, over_temp, heater_max, 
                      over_temp_buttons_n_clicks, ln2_buttons_n_clicks, h2_buttons_n_clicks, object_buttons_n_clicks,
                      pass_through_max, pass_through_min):
    # Update time values
    new_time = (data['time'][-1] + 1) if data['time'] else 0

    # Update the store with the new time value
    data['time'].append(new_time)

    # move all average calculations and stuff in here to have data store be updated in one place
    data['ln2-object-target'].append(ln2_obj_target)
    data['h2-object-target'].append(h2_obj_target)

    data["pass-through-min"].append(pass_through_min)
    data["pass-through-max"].append(pass_through_max)
    
    #
    # read from csv
    temp_file = []
    with open('temp.csv', mode = 'r') as myfile:
        reader = csv.reader(myfile)
        for row in reader:
            temp_file = list(map(float,row))
        
    for i in range(len(temp_file)):
        data[f'{i+1}'].append(temp_file[i])


    # add which tc buttons are clicked
    for i in range(NUM_TC):
        if object_buttons_n_clicks[i] % 2 == 1:
            data["obj-tc-btns"][i] = "on"
        else:
            data["obj-tc-btns"][i] = "off"
        if h2_buttons_n_clicks[i] % 2 == 1:
            data["h2-tc-btns"][i] = "on"
        else:
            data["h2-tc-btns"][i] = "off"
        if ln2_buttons_n_clicks[i] % 2 == 1:
            data["ln2-tc-btns"][i] = "on"
        else:
            data["ln2-tc-btns"][i] = "off"
        if over_temp_buttons_n_clicks[i] % 2 == 1:
            data["over-temp-tc-btns"][i] = "on"
        else:
            data["over-temp-tc-btns"][i] = "off"
    
    # over temp calculations
    selected_tc_values = [
        data[f'{i+1}'][-1]  # Get the latest value of each selected TC
        for i in range(NUM_TC)
        if over_temp_buttons_n_clicks[i] % 2 == 1
    ]
    
    if selected_tc_values:
        max_value = max(selected_tc_values)
    else:
        max_value = -1

    if (type(over_temp) != type(None) and max_value >= float(over_temp)):
        heater_over_temp = {'background-color': "green", 'height': "6.5vh", 'width': "6.5vh", 'border-radius': "100%", 'border': '2px solid black', 'background-color': 'rgb(55,140,77)', 'box-shadow': '0px 0px 3px 3px rgb(62,200,87)'}
        data['over-temp'].append(1)
    else:
        heater_over_temp = {'background-color': "grey", 'height': "6.5vh", 'width': "6.5vh", 'border-radius': "100%", 'border': '2px solid black'}
        data['over-temp'].append(0)


    # shroud temp calculations
    selected_tc_values = [
        data[f'{i+1}'][-1]  # Get the latest value of each selected TC
        for i in range(NUM_TC)
        if ln2_buttons_n_clicks[i] % 2 == 1
    ]
    
    if selected_tc_values:
        average_value = sum(selected_tc_values) / len(selected_tc_values)
    else:
        average_value = 0

    data['ln2-temp'].append(average_value)
    
    shroud_temp_out = f"Shroud Temp: {average_value:.2f}°C"


    # heater temp calculations
    selected_tc_values = [
        data[f'{i+1}'][-1]  # Get the latest value of each selected TC
        for i in range(NUM_TC)
        if h2_buttons_n_clicks[i] % 2 == 1
    ]
    
    if selected_tc_values:
        average_value = sum(selected_tc_values) / len(selected_tc_values)
    else:
        average_value = 0

    data['h2-temp'].append(average_value)
    
    heater_temp_out = f"Heater Temp: {average_value:.2f}°C"

    
    # heater max calculations
    selected_tc_values = [
        data[f'{i+1}'][-1]  # Get the latest value of each selected TC
        for i in range(NUM_TC)
        if h2_buttons_n_clicks[i] % 2 == 1
    ]
    
    if selected_tc_values:
        max_value = max(selected_tc_values)
    else:
        max_value = -1

    if (type(heater_max) != type(None) and max_value >= float(heater_max)):
        heater_max_out = {'background-color': "green", 'height': "6.5vh", 'width': "6.5vh", 'border-radius': "100%", 'border': '2px solid black', 'background-color': 'rgb(55,140,77)', 'box-shadow': '0px 0px 3px 3px rgb(62,200,87)'}
        data['h2-max'].append(1)
    else:
        heater_max_out = {'background-color': "grey", 'height': "6.5vh", 'width': "6.5vh", 'border-radius': "100%", 'border': '2px solid black'}
        data['h2-max'].append(0)

    
    # shroud min calculations
    selected_tc_values = [
        data[f'{i+1}'][-1]  # Get the latest value of each selected TC
        for i in range(NUM_TC)
        if ln2_buttons_n_clicks[i] % 2 == 1
    ]
    
    if selected_tc_values:
        min_value = min(selected_tc_values)
    else:
        min_value = 20000

    if (type(shroud_min) != type(None) and min_value <= float(shroud_min)):
        shroud_min_out = {'background-color': "green", 'height': "6.5vh", 'width': "6.5vh", 'border-radius': "100%", 'border': '2px solid black', 'background-color': 'rgb(55,140,77)', 'box-shadow': '0px 0px 3px 3px rgb(62,200,87)'}
        data['shroud-min'].append(1)
    else:
        shroud_min_out = {'background-color': "grey", 'height': "6.5vh", 'width': "6.5vh", 'border-radius': "100%", 'border': '2px solid black'}
        data['shroud-min'].append(0)


    # H1 temp calculations
    h1_average = (data['15'][-1] + data['16'][-1]) / 2
    data['h1-temp'].append(h1_average)
    pass_through_temp_out = f'Temp: {h1_average:.2f} °C'
    

    return data, heater_over_temp, shroud_temp_out, shroud_temp_out, heater_temp_out, heater_temp_out, heater_max_out, shroud_min_out, pass_through_temp_out


# callback function to update graph every second
@callback(
        Output(component_id='status-plot', component_property='figure'),
        [Input(component_id='tc-select-panel', component_property='value'),
         Input(component_id="int-comp", component_property='n_intervals')],
        State(component_id='tc-data-store', component_property='data')
)
def update_graph(selected_tcs, n_intervals, store_data):
    # Ensure selected_tcs is not None; if None, assign an empty list
    if selected_tcs is None:
        selected_tcs = []
       
    # Create traces for only the selected TCs
    traces = []
    for tc in selected_tcs:
        color = tc_colors[int(tc)-1]
        last_values = list(store_data[tc][-MAX_LEN:])
        last_time = list(store_data['time'])[-MAX_LEN:]
        traces.append(go.Scatter(
            x=last_time,  # Use the time axis for all
            y=last_values,
            mode='lines+markers',
            name=tc,
            line=dict(color=color),
        ))
    
    # Create the figure for the graph
    fig = go.Figure(
        data=traces,
        layout=go.Layout(
            xaxis=dict(title="Time (s)"),
            yaxis=dict(title="Temperature (°C)"),
            margin=dict(l=40, r=40, t=40, b=40)
        )
    )
    return fig


# Callback to capture the selected checklist options
@callback(
    Input('tc-select-panel', 'value')
)
def update_tc_select(selected_values):
    print(f"Selected: {', '.join(selected_values)}")
    return 


# callback function for H1 override buttons
@callback(
        [Output(component_id='btn-h1-override-on-off', component_property='disabled'),
         Output(component_id='btn-h1-override-on-off', component_property='style'),
         Output(component_id='btn-h1-override-toggle', component_property='style'),
         Output(component_id='btn-h1-override-toggle', component_property='disabled'),
         Output(component_id='btn-h1-override-on-off', component_property='n_clicks')],
        [Input(component_id='btn-h1-override-toggle', component_property='n_clicks'),
         Input(component_id='btn-h1-override-on-off', component_property='n_clicks'),
         Input(component_id='btn-estop', component_property='n_clicks')],
        [State(component_id='btn-h1-override-on-off', component_property='disabled')]
)
def h1_override_control(toggle_n_clicks, on_off_n_clicks, estop_n_clicks, disabled):
    if estop_n_clicks % 2 == 1:
        return False, {'background-color': "grey", 'height': "10vh", 'width': "10vh", 'border-radius': "100%", 'border': '2px solid black'}, {'background-color': "green", 'height': "10vh", 'width': "10vh", 'border-radius': "100%",
                                'border': '2px solid black', 'background-color': 'rgb(55,140,77)', 'box-shadow': '0px 0px 3px 3px rgb(62,200,87)'}, True, on_off_n_clicks
    elif (type(toggle_n_clicks) != type(None)) and (toggle_n_clicks % 2 == 1):
        if disabled:
            return False, {'background-color': "grey", 'height': "10vh", 'width': "10vh", 'border-radius': "100%", 'border': '2px solid black'}, {'background-color': "green", 'height': "10vh", 'width': "10vh", 'border-radius': "100%",
                                'border': '2px solid black', 'background-color': 'rgb(55,140,77)', 'box-shadow': '0px 0px 3px 3px rgb(62,200,87)'}, False, on_off_n_clicks
        else:
            if on_off_n_clicks % 2 == 1:
                return False, {'background-color': "green", 'height': "10vh", 'width': "10vh", 'border-radius': "100%",
                                'border': '2px solid black', 'background-color': 'rgb(55,140,77)', 'box-shadow': '0px 0px 3px 3px rgb(62,200,87)'}, {'background-color': "green", 'height': "10vh", 'width': "10vh", 'border-radius': "100%",
                                                                                                                                                    'border': '2px solid black', 'background-color': 'rgb(55,140,77)', 'box-shadow': '0px 0px 3px 3px rgb(62,200,87)'}, False, on_off_n_clicks
            else:
                return False, {'background-color': "grey", 'height': "10vh", 'width': "10vh", 'border-radius': "100%", 'border': '2px solid black'}, {'background-color': "green", 'height': "10vh", 'width': "10vh", 'border-radius': "100%",
                                                                                                                                                        'border': '2px solid black', 'background-color': 'rgb(55,140,77)', 'box-shadow': '0px 0px 3px 3px rgb(62,200,87)'}, False, on_off_n_clicks
    else:
        if (type(on_off_n_clicks) != type(None)) and (on_off_n_clicks % 2 == 1):
            return True, {'background-color': "grey", 'height': "10vh", 'width': "10vh", 'border-radius': "100%", 'border': '2px solid black'}, {'background-color': "grey", 'height': "10vh", 'width': "10vh", 'border-radius': "100%", 'border': '2px solid black'}, False, on_off_n_clicks-1
        else:
            return True, {'background-color': "grey", 'height': "10vh", 'width': "10vh", 'border-radius': "100%", 'border': '2px solid black'}, {'background-color': "grey", 'height': "10vh", 'width': "10vh", 'border-radius': "100%", 'border': '2px solid black'}, False, on_off_n_clicks

        
# callback function for heater override buttons
@callback(
        [Output(component_id='btn-heater-override-on-off', component_property='disabled'),
         Output(component_id='btn-heater-override-on-off', component_property='style'),
         Output(component_id='btn-heater-override-toggle', component_property='style'),
         Output(component_id='btn-heater-override-toggle', component_property='disabled'),
         Output(component_id='btn-heater-override-on-off', component_property='n_clicks'),
         Output(component_id='heater-override-out', component_property='style')],
        [Input(component_id='btn-heater-override-toggle', component_property='n_clicks'),
         Input(component_id='btn-heater-override-on-off', component_property='n_clicks'),
         Input(component_id='btn-estop', component_property='n_clicks')],
        [State(component_id='btn-heater-override-on-off', component_property='disabled')]
)
def heater_override_control(toggle_n_clicks, on_off_n_clicks, estop_n_clicks, disabled):
    if estop_n_clicks % 2 == 1:
        return False, {'background-color': "grey", 'height': "10vh", 'width': "10vh", 'border-radius': "100%", 'border': '2px solid black'}, {'background-color': "green", 'height': "10vh", 'width': "10vh", 'border-radius': "100%",
                                'border': '2px solid black', 'background-color': 'rgb(55,140,77)', 'box-shadow': '0px 0px 3px 3px rgb(62,200,87)'}, True, on_off_n_clicks, {'background-color': "grey", 'height': "6.5vh", 'width': "6.5vh", 'border-radius': "100%", 'border': '2px solid black'}
    elif (type(toggle_n_clicks) != type(None)) and toggle_n_clicks % 2 == 1:
        if disabled:
            return False, {'background-color': "grey", 'height': "10vh", 'width': "10vh", 'border-radius': "100%", 'border': '2px solid black'}, {'background-color': "green", 'height': "10vh", 'width': "10vh", 'border-radius': "100%",
                                'border': '2px solid black', 'background-color': 'rgb(55,140,77)', 'box-shadow': '0px 0px 3px 3px rgb(62,200,87)'}, False, on_off_n_clicks, {'background-color': "grey", 'height': "6.5vh", 'width': "6.5vh", 'border-radius': "100%", 'border': '2px solid black'}
        else:
            if on_off_n_clicks % 2 == 1:
                return False, {'background-color': "green", 'height': "10vh", 'width': "10vh", 'border-radius': "100%",
                                'border': '2px solid black', 'background-color': 'rgb(55,140,77)', 'box-shadow': '0px 0px 3px 3px rgb(62,200,87)'}, {'background-color': "green", 'height': "10vh", 'width': "10vh", 'border-radius': "100%",
                                                                                                                                                    'border': '2px solid black', 'background-color': 'rgb(55,140,77)', 'box-shadow': '0px 0px 3px 3px rgb(62,200,87)'}, False, on_off_n_clicks, {'background-color': "green", 'height': "6.5vh", 'width': "6.5vh", 'border-radius': "100%",
                                                                                                                                                                                                                                                                                        'border': '2px solid black', 'background-color': 'rgb(55,140,77)', 'box-shadow': '0px 0px 3px 3px rgb(62,200,87)'}
            else:
                return False, {'background-color': "grey", 'height': "10vh", 'width': "10vh", 'border-radius': "100%", 'border': '2px solid black'}, {'background-color': "green", 'height': "10vh", 'width': "10vh", 'border-radius': "100%",
                                                                                                                                                        'border': '2px solid black', 'background-color': 'rgb(55,140,77)', 'box-shadow': '0px 0px 3px 3px rgb(62,200,87)'}, False, on_off_n_clicks, {'background-color': "grey", 'height': "6.5vh", 'width': "6.5vh", 'border-radius': "100%", 'border': '2px solid black'}
    else:
        if (type(on_off_n_clicks) != type(None)) and on_off_n_clicks % 2 == 1:
            return True, {'background-color': "grey", 'height': "10vh", 'width': "10vh", 'border-radius': "100%", 'border': '2px solid black'}, {'background-color': "grey", 'height': "10vh", 'width': "10vh", 'border-radius': "100%", 'border': '2px solid black'}, False, on_off_n_clicks-1, {'background-color': "grey", 'height': "6.5vh", 'width': "6.5vh", 'border-radius': "100%", 'border': '2px solid black'}
        else:
            return True, {'background-color': "grey", 'height': "10vh", 'width': "10vh", 'border-radius': "100%", 'border': '2px solid black'}, {'background-color': "grey", 'height': "10vh", 'width': "10vh", 'border-radius': "100%", 'border': '2px solid black'}, False, on_off_n_clicks, {'background-color': "grey", 'height': "6.5vh", 'width': "6.5vh", 'border-radius': "100%", 'border': '2px solid black'}


# callback function for LN2 override buttons
@callback(
        [Output(component_id='btn-ln2-override-on-off', component_property='disabled'),
         Output(component_id='btn-ln2-override-on-off', component_property='style'),
         Output(component_id='btn-ln2-override-toggle', component_property='style'),
         Output(component_id='btn-ln2-override-toggle', component_property='disabled'),
         Output(component_id='btn-ln2-override-on-off', component_property='n_clicks'),
         Output(component_id='ln2-override-out', component_property='style')],
        [Input(component_id='btn-ln2-override-toggle', component_property='n_clicks'),
         Input(component_id='btn-ln2-override-on-off', component_property='n_clicks'),
         Input(component_id='btn-estop', component_property='n_clicks')],
        [State(component_id='btn-ln2-override-on-off', component_property='disabled')]
)
def ln2_override_control(toggle_n_clicks, on_off_n_clicks, estop_n_clicks, disabled):
    if estop_n_clicks % 2 == 1:
        return False, {'background-color': "grey", 'height': "10vh", 'width': "10vh", 'border-radius': "100%", 'border': '2px solid black'}, {'background-color': "green", 'height': "10vh", 'width': "10vh", 'border-radius': "100%",
                                        'border': '2px solid black', 'background-color': 'rgb(55,140,77)', 'box-shadow': '0px 0px 3px 3px rgb(62,200,87)'}, True, on_off_n_clicks, {'background-color': "grey", 'height': "6.5vh", 'width': "6.5vh", 'border-radius': "100%", 'border': '2px solid black'}
    elif (type(toggle_n_clicks) != type(None)) and toggle_n_clicks % 2 == 1:
        if disabled:
            return False, {'background-color': "grey", 'height': "10vh", 'width': "10vh", 'border-radius': "100%", 'border': '2px solid black'}, {'background-color': "green", 'height': "10vh", 'width': "10vh", 'border-radius': "100%",
                                'border': '2px solid black', 'background-color': 'rgb(55,140,77)', 'box-shadow': '0px 0px 3px 3px rgb(62,200,87)'}, False, on_off_n_clicks, {'background-color': "grey", 'height': "6.5vh", 'width': "6.5vh", 'border-radius': "100%", 'border': '2px solid black'}
        else:
            if on_off_n_clicks % 2 == 1:
                return False, {'background-color': "green", 'height': "10vh", 'width': "10vh", 'border-radius': "100%",
                                'border': '2px solid black', 'background-color': 'rgb(55,140,77)', 'box-shadow': '0px 0px 3px 3px rgb(62,200,87)'}, {'background-color': "green", 'height': "10vh", 'width': "10vh", 'border-radius': "100%",
                                                                                                                                                    'border': '2px solid black', 'background-color': 'rgb(55,140,77)', 'box-shadow': '0px 0px 3px 3px rgb(62,200,87)'}, False, on_off_n_clicks, {'background-color': "green", 'height': "6.5vh", 'width': "6.5vh", 'border-radius': "100%",
                                                                                                                                                                                                                                                                                        'border': '2px solid black', 'background-color': 'rgb(55,140,77)', 'box-shadow': '0px 0px 3px 3px rgb(62,200,87)'}
            else:
                return False, {'background-color': "grey", 'height': "10vh", 'width': "10vh", 'border-radius': "100%", 'border': '2px solid black'}, {'background-color': "green", 'height': "10vh", 'width': "10vh", 'border-radius': "100%",
                                                                                                                                                        'border': '2px solid black', 'background-color': 'rgb(55,140,77)', 'box-shadow': '0px 0px 3px 3px rgb(62,200,87)'}, False, on_off_n_clicks, {'background-color': "grey", 'height': "6.5vh", 'width': "6.5vh", 'border-radius': "100%", 'border': '2px solid black'}
    else:
        if (type(on_off_n_clicks) != type(None)) and on_off_n_clicks % 2 == 1:
            return True, {'background-color': "grey", 'height': "10vh", 'width': "10vh", 'border-radius': "100%", 'border': '2px solid black'}, {'background-color': "grey", 'height': "10vh", 'width': "10vh", 'border-radius': "100%", 'border': '2px solid black'}, False, on_off_n_clicks-1, {'background-color': "grey", 'height': "6.5vh", 'width': "6.5vh", 'border-radius': "100%", 'border': '2px solid black'}
        else:
            return True, {'background-color': "grey", 'height': "10vh", 'width': "10vh", 'border-radius': "100%", 'border': '2px solid black'}, {'background-color': "grey", 'height': "10vh", 'width': "10vh", 'border-radius': "100%", 'border': '2px solid black'}, False, on_off_n_clicks, {'background-color': "grey", 'height': "6.5vh", 'width': "6.5vh", 'border-radius': "100%", 'border': '2px solid black'}

# Callback for LN2 On Time Input
@callback(
    Input(component_id="temp-ln2-ln2-on-time-in", component_property='value')
)
def update_ln2_on_time(ln2_on_time):
    print("LN2 On Time changed to", ln2_on_time)
    return


# Callback to handle temp object TC button clicks
@callback(
    Output({'type': 'temp-obj-tc-button', 'index': MATCH}, 'style'),
    Input({'type': 'temp-obj-tc-button', 'index': MATCH}, 'n_clicks'),
    State({'type': 'temp-obj-tc-button', 'index': MATCH}, 'id'),
    prevent_initial_call=True
)
def update_temp_object_tc_btn(n_clicks, id):
    # Debugging information to ensure the callback is triggered
    print(f"Button clicked: {id['index'] + 1}, n_clicks: {n_clicks}")

    # button off
    if n_clicks % 2 == 0:
        return {'height': "3vh",
                'width': "3vw",
                'background-color': "grey",
                'border-radius': "30%",
                'margin': "1px"}
    else:
        #TODO: add functionality
        return {'height': "3vh",
                'width': "3vw",
                'background-color': "green",
                'border-radius': "30%",
                'margin': "1px"}
    


# Callback to handle temp heater TC button clicks
@callback(
    Output({'type': 'temp-heater-tc-button', 'index': MATCH}, 'style'),
    Input({'type': 'temp-heater-tc-button', 'index': MATCH}, 'n_clicks'),
    State({'type': 'temp-heater-tc-button', 'index': MATCH}, 'id'),
    prevent_initial_call=True
)
def update_temp_heater_tc_btn(n_clicks, id):
    # Debugging information to ensure the callback is triggered
    print(f"Button clicked: {id['index'] + 1}, n_clicks: {n_clicks}")
    
    # button off
    if n_clicks % 2 == 0:
        return {'height': "3vh",
                'width': "3vw",
                'background-color': "grey",
                'border-radius': "30%",
                'margin': "1px"}
    else:
        #TODO: add functionality
        return {'height': "3vh",
                'width': "3vw",
                'background-color': "green",
                'border-radius': "30%",
                'margin': "1px"}
    

# Callback to handle temp over temp TC button clicks
@callback(
    Output({'type': 'temp-over-temp-tc-button', 'index': MATCH}, 'style'),
    Input({'type': 'temp-over-temp-tc-button', 'index': MATCH}, 'n_clicks'),
    State({'type': 'temp-over-temp-tc-button', 'index': MATCH}, 'id'),
    prevent_initial_call=True
)
def update_temp_over_temp_tc_btn(n_clicks, id):
    # Debugging information to ensure the callback is triggered
    print(f"Button clicked: {id['index'] + 1}, n_clicks: {n_clicks}")
    
    # button off
    if n_clicks % 2 == 0:
        return {'height': "3vh",
                'width': "3vw",
                'background-color': "grey",
                'border-radius': "30%",
                'margin': "1px"}
    else:
        #TODO: add functionality
        return {'height': "3vh",
                'width': "3vw",
                'background-color': "green",
                'border-radius': "30%",
                'margin': "1px"}
    

# Callback to handle temp LN2 TC button clicks
@callback(
    Output({'type': 'temp-ln2-tc-button', 'index': MATCH}, 'style'),
    Input({'type': 'temp-ln2-tc-button', 'index': MATCH}, 'n_clicks'),
    State({'type': 'temp-ln2-tc-button', 'index': MATCH}, 'id'),
    prevent_initial_call=True
)
def update_temp_ln2_tc_btn(n_clicks, id):
    # Debugging information to ensure the callback is triggered
    print(f"Button clicked: {id['index'] + 1}, n_clicks: {n_clicks}")
    
    # button off
    if n_clicks % 2 == 0:
        return {'height': "3vh",
                'width': "3vw",
                'background-color': "grey",
                'border-radius': "30%",
                'margin': "1px"}
    else:
        #TODO: add functionality
        return {'height': "3vh",
                'width': "3vw",
                'background-color': "green",
                'border-radius': "30%",
                'margin': "1px"}


# callback function for when logging TCs button is pressed
@callback(
    Output(component_id='log-tcs-btn', component_property='style'),
    Input(component_id='log-tcs-btn', component_property='n_clicks'),
    prevent_initial_call=True
)
def update_log_tcs_btn(n_clicks):
    if "log-tcs-btn" == ctx.triggered_id:
        # TODO: add functionality for log TCs button
        print("The log TCs button has been clicked")
        
        if n_clicks % 2 == 1:
            # button is on
            return {'background-color': "green",
                    'height': "6vh",
                    'width': "6vh",
                    'border-radius': "100%",
                    'border': '2px solid black',
                    'background-color': 'rgb(55,140,77)',
                    'box-shadow': '0px 0px 3px 3px rgb(62,200,87)'}
        else:
            return {'background-color': "grey",
                    'height': "6vh",
                    'width': "6vh",
                    'border-radius': "100%",
                    'border': '2px solid black'}
    

# callback function for when logging heater status button is pressed
@callback(
    Output(component_id='log-heater-status-btn', component_property='style'),
    Input(component_id='log-heater-status-btn', component_property='n_clicks'),
    prevent_initial_call=True
)
def update_log_heater_status_btn(n_clicks):
    if "log-heater-status-btn" == ctx.triggered_id:
        # TODO: add functionality for log heater status button
        print("The log heater status button has been clicked")
        
        if n_clicks % 2 == 1:
            # button is on
            return {'background-color': "green",
                    'height': "6vh",
                    'width': "6vh",
                    'border-radius': "100%",
                    'border': '2px solid black',
                    'background-color': 'rgb(55,140,77)',
                    'box-shadow': '0px 0px 3px 3px rgb(62,200,87)'}
        else:
            return {'background-color': "grey",
                    'height': "6vh",
                    'width': "6vh",
                    'border-radius': "100%",
                    'border': '2px solid black'}
    

# callback function for when logging LN2 status button is pressed
@callback(
    Output(component_id='log-ln2-status-btn', component_property='style'),
    Input(component_id='log-ln2-status-btn', component_property='n_clicks'),
    prevent_initial_call=True
)
def update_log_ln2_status_btn(n_clicks):
    if "log-ln2-status-btn" == ctx.triggered_id:
        # TODO: add functionality for log LN2 status button
        print("The log LN2 status button has been clicked")
        
        if n_clicks % 2 == 1:
            # button is on
            return {'background-color': "green",
                    'height': "6vh",
                    'width': "6vh",
                    'border-radius': "100%",
                    'border': '2px solid black',
                    'background-color': 'rgb(55,140,77)',
                    'box-shadow': '0px 0px 3px 3px rgb(62,200,87)'}
        else:
            return {'background-color': "grey",
                    'height': "6vh",
                    'width': "6vh",
                    'border-radius': "100%",
                    'border': '2px solid black'}


# control loop function
@callback(
    [Output(component_id="btn-ln2-status", component_property="style"),
     Output(component_id="btn-heater-status", component_property="style"),
     Output(component_id="btn-h1-status", component_property="style")],
    Input(component_id="int-comp", component_property="n_intervals"),
    [State(component_id='tc-data-store', component_property='data'),
    State(component_id='btn-h1-override-on-off', component_property='style'),
    State(component_id='btn-heater-override-on-off', component_property='style'),
    State(component_id='btn-ln2-override-on-off', component_property='style')]

)
def control_loop(n_intervals, data, h1_override_style, h2_override_style, ln2_override_style):
    # heater_status = {}
    # ln2_status = {}
    # h1_status = {}
    json_data = {
        "H1": 0,
        "H2": 0,
        "LN2": 0
    }

    # H2
    if h2_override_style['background-color'] == 'rgb(55,140,77)':
        # GPIO.output(H1, GPIO.HIGH)
        json_data["H2"] = 1
        heater_status = {
                            'height': "3vh", 'width': "10vw", 'background-color': "rgb(230, 14, 7)",  'color': "white",
                            'font-size': "2vh", 'margin': "0vh auto", 'border-radius': '10px',  # Rounded corners to enhance the glow effect
                            'box-shadow': '0 0 10px rgba(255, 0, 0, 0.7), 0 0 20px rgba(255, 0, 0, 0.5), 0 0 30px rgba(255, 0, 0, 0.3)',  # Glow effect
                            'border': '2px solid rgba(255, 0, 0, 0.8)'  # Slightly glowing border
                        }
    else:
        if data['h2-object-target'] and type(data['h2-object-target'][-1]) != type(None) and float(data['h2-object-target'][-1]) > data['h2-temp'][-1]:
            # heater on
            print("heater on")
            json_data["H2"] = 1
            # GPIO.output(H2, GPIO.HIGH)
            heater_status = {
                                'height': "3vh", 'width': "10vw", 'background-color': "rgb(230, 14, 7)",  'color': "white",
                                'font-size': "2vh", 'margin': "0vh auto", 'border-radius': '10px',  # Rounded corners to enhance the glow effect
                                'box-shadow': '0 0 10px rgba(255, 0, 0, 0.7), 0 0 20px rgba(255, 0, 0, 0.5), 0 0 30px rgba(255, 0, 0, 0.3)',  # Glow effect
                                'border': '2px solid rgba(255, 0, 0, 0.8)'  # Slightly glowing border
                            }
        else:
            # GPIO.output(H2, GPIO.LOW)
            heater_status = {
                                'height': "3vh", 'width': "10vw", 'background-color': "rgb(140,20,11)", 'color': "white",
                                'font-size': "2vh", 'margin': "0vh auto"
                            }
        
        if data['h2-max'] and data['h2-max'][-1]:
            print('heater_max')
            # GPIO.output(H2, GPIO.LOW)
            heater_status = {
                                'height': "3vh", 'width': "10vw", 'background-color': "rgb(140,20,11)", 'color': "white",
                                'font-size': "2vh", 'margin': "0vh auto"
                            }
        if data['over-temp'] and data['over-temp'][-1]: 
            print('over_temp')
            # GPIO.output(H2, GPIO.LOW)
            heater_status = {
                                'height': "3vh", 'width': "10vw", 'background-color': "rgb(140,20,11)", 'color': "white",
                                'font-size': "2vh", 'margin': "0vh auto"
                            }
        
    # LN2
    if ln2_override_style['background-color'] == 'rgb(55,140,77)':
        # GPIO.output(LN2, GPIO.HIGH)
        json_data["LN2"] = 1
        ln2_status = {
                        'height': "7vh", 'width': "7vw", 'background-color': "rgb(56, 217, 7)", 'color': "white",
                        'font-size': "2vh", 'margin': "1vh 1vh", 'border-radius': '10px',  # Rounded corners to enhance the glow effect
                        'box-shadow': '0 0 15px rgba(0, 255, 0, 0.7), 0 0 30px rgba(0, 255, 0, 0.5), 0 0 45px rgba(0, 255, 0, 0.3)',  # Glowing green effect
                        'border': '2px solid rgba(0, 255, 0, 0.8)'  # Slightly glowing green border
                    }
    else:
        if (data['ln2-object-target']) and (data['ln2-temp']) and (type(data['ln2-object-target'][-1]) != type(None)) and (float(data['ln2-object-target'][-1]) < data['ln2-temp'][-1]):
            print('ln2 on')
            # GPIO.output(LN2, GPIO.HIGH)
            json_data["LN2"] = 1
            ln2_status = {
                            'height': "7vh", 'width': "7vw", 'background-color': "rgb(56, 217, 7)", 'color': "white",
                            'font-size': "2vh", 'margin': "1vh 1vh", 'border-radius': '10px',  # Rounded corners to enhance the glow effect
                            'box-shadow': '0 0 15px rgba(0, 255, 0, 0.7), 0 0 30px rgba(0, 255, 0, 0.5), 0 0 45px rgba(0, 255, 0, 0.3)',  # Glowing green effect
                            'border': '2px solid rgba(0, 255, 0, 0.8)'  # Slightly glowing green border
                        }
        else:
            # GPIO.output(LN2, GPIO.LOW)
            ln2_status = {
                            'height': "7vh", 'width': "7vw", 'background-color': "rgb(20,82,29)", 'color': "white",
                            'font-size': "2vh", 'margin': "1vh 1vh"
                        }
            
        if data['shroud-min'] and data['shroud-min'][-1]:
            # GPIO.output(LN2, GPIO.LOW)
            ln2_status = {
                            'height': "7vh", 'width': "7vw", 'background-color': "rgb(20,82,29)", 'color': "white",
                            'font-size': "2vh", 'margin': "1vh 1vh"
                        }

    # H1
    if h1_override_style['background-color'] == 'rgb(55,140,77)':
        # GPIO.output(H1, GPIO.HIGH)
        json_data["H1"] = 1
        h1_status = {
                        'height': "4vh", 'width': "10vw", 'background-color': "rgb(230, 14, 7)", 'color': "white",
                        'font-size': "2vh", 'margin': "0.5vh 1vh", 'border-radius': '10px',  # Rounded corners for a smooth glow effect
                        'box-shadow': '0 0 15px rgba(255, 0, 0, 0.7), 0 0 30px rgba(255, 0, 0, 0.5), 0 0 45px rgba(255, 0, 0, 0.3)',  # Glowing red effect
                        'border': '2px solid rgba(255, 0, 0, 0.8)'  # Slightly glowing red border
                    }
    else:
        if (type(data['pass-through-min'][-1]) == type(None) or type(data['pass-through-max'][-1]) == type(None)) or (data['h1-temp'] and data['h1-temp'][-1] > data['pass-through-min'][-1] and data['h1-temp'][-1] < data['pass-through-max'][-1]): # TODO: change to depend on pass through min/max
            # GPIO.output(H1, GPIO.LOW)
            h1_status = {
                            'height': "4vh", 'width': "10vw", 'background-color': "rgb(140,20,11)", 'color': "white",
                            'font-size': "2vh", 'margin': "0.5vh 1vh"
                        }
        else:
            json_data["H1"] = 1
            # GPIO.output(H1, GPIO.HIGH)
            h1_status = {
                            'height': "4vh", 'width': "10vw", 'background-color': "rgb(230, 14, 7)", 'color': "white",
                            'font-size': "2vh", 'margin': "0.5vh 1vh", 'border-radius': '10px',  # Rounded corners for a smooth glow effect
                            'box-shadow': '0 0 15px rgba(255, 0, 0, 0.7), 0 0 30px rgba(255, 0, 0, 0.5), 0 0 45px rgba(255, 0, 0, 0.3)',  # Glowing red effect
                            'border': '2px solid rgba(255, 0, 0, 0.8)'  # Slightly glowing red border
                        }

    with open('heater_control.json', 'w') as file:
        json.dump(data, file, indent=4)

    return ln2_status, heater_status, h1_status



if __name__ == '__main__':
    app.run(debug=True)
