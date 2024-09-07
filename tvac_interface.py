# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.


from dash import Dash, dcc, html, Input, Output, ctx, callback, MATCH, State
import plotly.express as px
import pandas as pd


app = Dash(__name__)

df = pd.read_csv('https://gist.githubusercontent.com/chriddyp/5d1ea79569ed194d432e56108a04d188/raw/a9f9e8076b837d541398e999dcbac2b2826a81f8/gdp-life-exp-2007.csv')

fig = px.scatter(df, x="gdp per capita", y="life expectancy",
                 size="population", color="continent", hover_name="country",
                 log_x=True, size_max=60)

df = px.data.iris()  # iris is a pandas DataFrame
fig = px.scatter(df, x="sepal_width", y="sepal_length")

# create CSS file that will make it look better

app.layout = html.Div([
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
                        style={'height': "7vh", # TODO: make dynamic sizes
                            'background-color': "red",
                            'color': "white",
                            'font-size': "3vh",
                            'padding:': "1vh 1vh",
                            'margin-left': "15vw"}
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
                        dcc.Input(id="shroud-temp-in", type="number", debounce=True, placeholder="Shroud Temp"),
                        style={'margin': "3vh auto", 'padding': "1vh"})
                ], style={'text-align': "center"}),
                html.Tr([
                    html.Td(
                        html.H4("TVAC Representation"),
                        style={'margin': "2vh auto", 'padding': "1vh", 'text-align': "center", 'color': "white"})
                ]),
                html.Tr([
                    html.Td(
                        dcc.Input(id="obj-temp-in", type="number", debounce=True, placeholder="Object Temp"),
                        style={'margin': "5vh auto", 'padding': "1vh", 'text-align': "center"})
                ]),
                html.Tr([
                    html.Td(
                        dcc.Input(id="heater-temp-in", type="number", debounce=True, placeholder="Heater Temp"),
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
                dcc.Graph(figure=fig, style={'border': "2px solid black", 'width': '37vw', 'margin-right': "1vw"}, 
                          config={'displayModeBar': False}),
                dcc.Checklist(
                    id="tc-select-panel",
                    options=[
                        {
                            "label": [html.Span(f"TC{i+1}", style={"font-size": "2.3vh", "padding-left": '0.5vw', 'width': "3.2vw"}),
                                    html.Div('', style={'height': "2vh", 'width': "2vw", 'background-color': color}),
                                    html.Div(f"{i+1}.00", style={"font-size": "2vh", "padding": '0px 1vw', 'background-color': "rgb(180,180,180)",
                                                                 "border": '2px solid black', "margin-left": '2vw', "width": "2vw",
                                                                 "margin-top": '0.5vh', "margin-right": '3vw'})],
                            "value": f"{i+1}"
                        } for i, color in enumerate(
                                ['red', 'blue', 'green', 'yellow', 'purple', 'orange', 'pink', 'cyan', 'black', 'brown',
                                'grey', 'lime', 'navy', 'maroon', 'silver', 'teal', 'olive', 'aqua', 'fuchsia', 'gray'])
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
                            ]) for i in range(20)
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
                        html.Td(html.Button('', id='btn-h1-override-on-off',
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
                    html.Td(html.Button('', id='btn-heater-override-on-off',
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
                    html.Td(html.Button('', id='btn-ln2-override-on-off',
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
                        html.Div("Pass Through"),
                        dcc.Input(id="temp-pass-through-max-in", type="number", debounce=True, placeholder="Max", style={'margin': "1vh 1vw"}),
                        dcc.Input(id="temp-pass-through-min-in", type="number", debounce=True, placeholder="Min", style={'margin': "1vh 1vw"}),
                        html.Div("Temp", id='temp-temp-out', style={'margin-bottom': "1vh", 'border': "2px solid black", 'padding': "0px 1vw"})
                    ], style={'display': "flex", 'align-items': 'center','flex-direction': "column", 'border': "2px solid black", 
                              'margin-bottom': "2vh"}),

                    html.Div([
                        html.Div("LN2"),
                        dcc.Input(id="temp-ln2-object-target-in", type="text", debounce=True, placeholder="Object Target", style={'margin': "1vh 1vw"}),
                        dcc.Input(id="temp-ln2-ln2-on-time-in", type="number", debounce=True, placeholder="LN2 On Time", style={'margin': "1vh 1vw"}),
                        dcc.Input(id="temp-ln2-shroud-min-in", type="number", debounce=True, placeholder="Shroud Min", style={'margin': "1vh 1vw"}),
                        html.Div("Shroud Temp", id='temp-shroud-temp-out', style={'margin-bottom': "1vh", 'border': "2px solid black", 'padding': "0px 1vw"})
                    ], style={'display': "flex", 'align-items': 'center','flex-direction': "column", 'border': "2px solid black",
                              'margin-bottom': "1vh"}),
                ], style={'margin-left': "1vw", 'margin-top': "1vh"}),

                html.Div([
                    html.Div([
                        html.Div("Heater"),
                        dcc.Input(id="temp-heater-object-target-in", type="text", debounce=True, placeholder="Object Target", style={'margin': "1vh 1vw"}),
                        dcc.Input(id="temp-heater-over-temp-in", type="number", debounce=True, placeholder="Over Temp", style={'margin': "1vh 1vw"}),
                        dcc.Input(id="temp-heater-heater-max-in", type="number", debounce=True, placeholder="Heater Max", style={'margin': "1vh 1vw"}),
                        html.Div("Heater Temp", id='temp-heater-temp-out', style={'margin-bottom': "1vh", 'border': "2px solid black", 'padding': "0px 1vw"})
                    ], style={'display': "flex", 'align-items': 'center','flex-direction': "column", 'border': "2px solid black", 
                              'margin-bottom': "2vh"}),

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
                            style={'display': 'flex', 'align-items': 'center', 'margin': '0px'}) for i in range(20)
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
                            style={'display': 'flex', 'align-items': 'center', 'margin': '0px'}) for i in range(20)
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
                            style={'display': 'flex', 'align-items': 'center', 'margin': '0px'}) for i in range(20)
                        ]) 
                    ], style={'padding': '0px 1vw', 'border': "2px solid black", 'background-color': "rgb(39,68,90)"}),

                    html.Div([
                        html.Div("LN2 TCs", style={'color': "white", "font-size": "2.5vh", 'margin-left': "1vw"}),  
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
                            style={'display': 'flex', 'align-items': 'center', 'margin': '0px'}) for i in range(20)
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
    # Output(component_id='my-output', component_property='children'),
    Input(component_id='btn-estop', component_property='n_clicks'),
    prevent_initial_call=True
)
def update_estop(n_clicks):
    if "btn-estop" == ctx.triggered_id:
        # TODO: add functionality for E-Stop
        print("The E-Stop button has been pressed")
        return


# callback function for when shroud temp is changed
@callback(
    Input(component_id="shroud-temp-in", component_property='value')
)
def update_shroud_temp(temp):
    # TODO: add functionality for shroud temp change
    print("Shroud temp changed to ", temp)
    return


# callback function for when obj temp is changed
@callback(
    Input(component_id="obj-temp-in", component_property='value')
)
def update_obj_temp(temp):
    # TODO: add functionality for obj temp change
    print("Obj temp changed to ", temp)
    return


# callback function for when heater temp is changed
@callback(
    Input(component_id="heater-temp-in", component_property='value')
)
def update_heater_temp(temp):
    # TODO: add functionality for heater temp change
    print("Heater temp changed to ", temp)
    return


# Callback to capture the selected checklist options
@callback(
    Input('tc-select-panel', 'value')
)
def update_tc_select(selected_values):
    print(f"Selected: {', '.join(selected_values)}")
    return 


# callback function for when H1 override toggle button is pressed
@callback(
    Output(component_id='btn-h1-override-toggle', component_property='style'),
    Input(component_id='btn-h1-override-toggle', component_property='n_clicks'),
    prevent_initial_call=True
)
def update_h1_override_toggle_btn(n_clicks):
    if "btn-h1-override-toggle" == ctx.triggered_id:
        # TODO: add functionality for h1 override toggle button
        print("The H1 override toggle button has been clicked")
        
        if n_clicks % 2 == 1:
            # button is on
            return {'background-color': "green",
                    'height': "10vh",
                    'width': "10vh",
                    'border-radius': "100%",
                    'border': '2px solid black',
                    'background-color': 'rgb(55,140,77)',
                    'box-shadow': '0px 0px 3px 3px rgb(62,200,87)'}
        else:
            return {'background-color': "grey",
                    'height': "10vh",
                    'width': "10vh",
                    'border-radius': "100%",
                    'border': '2px solid black'}


# Callback function for when H1 override on/off button is pressed
@callback(
    Output(component_id='btn-h1-override-on-off', component_property='style'),
    Input(component_id='btn-h1-override-on-off', component_property='n_clicks'),
    prevent_initial_call=True
)
def update_h1_override_on_off_btn(n_clicks):
    if "btn-h1-override-on-off" == ctx.triggered_id:
        # TODO: add functionality for H1 override on/off button
        print("The H1 override on/off button has been clicked")
        
        if n_clicks % 2 == 1:
            # button is on
            return {'background-color': "green",
                    'height': "10vh",
                    'width': "10vh",
                    'border-radius': "100%",
                    'border': '2px solid black',
                    'background-color': 'rgb(55,140,77)',
                    'box-shadow': '0px 0px 3px 3px rgb(62,200,87)'}
        else:
            return {'background-color': "grey",
                    'height': "10vh",
                    'width': "10vh",
                    'border-radius': "100%",
                    'border': '2px solid black'}
        

# Callback function for when Heater override toggle button is pressed
@callback(
    Output(component_id='btn-heater-override-toggle', component_property='style'),
    Input(component_id='btn-heater-override-toggle', component_property='n_clicks'),
    prevent_initial_call=True
)
def update_heater_override_toggle_btn(n_clicks):
    if "btn-heater-override-toggle" == ctx.triggered_id:
        # TODO: add functionality for Heater override toggle button
        print("The Heater override toggle button has been clicked")
        
        if n_clicks % 2 == 1:
            # button is on
            return {'background-color': "green",
                    'height': "10vh",
                    'width': "10vh",
                    'border-radius': "100%",
                    'border': '2px solid black',
                    'background-color': 'rgb(55,140,77)',
                    'box-shadow': '0px 0px 3px 3px rgb(62,200,87)'}
        else:
            return {'background-color': "grey",
                    'height': "10vh",
                    'width': "10vh",
                    'border-radius': "100%",
                    'border': '2px solid black'}
        

# Callback function for when Heater override on/off button is pressed
@callback(
    Output(component_id='btn-heater-override-on-off', component_property='style'),
    Input(component_id='btn-heater-override-on-off', component_property='n_clicks'),
    prevent_initial_call=True
)
def update_heater_override_on_off_btn(n_clicks):
    if "btn-heater-override-on-off" == ctx.triggered_id:
        # TODO: add functionality for Heater override on/off button
        print("The Heater override on/off button has been clicked")
        
        if n_clicks % 2 == 1:
            # button is on
            return {'background-color': "green",
                    'height': "10vh",
                    'width': "10vh",
                    'border-radius': "100%",
                    'border': '2px solid black',
                    'background-color': 'rgb(55,140,77)',
                    'box-shadow': '0px 0px 3px 3px rgb(62,200,87)'}
        else:
            return {'background-color': "grey",
                    'height': "10vh",
                    'width': "10vh",
                    'border-radius': "100%",
                    'border': '2px solid black'}


# Callback function for when LN2 override toggle button is pressed
@callback(
    Output(component_id='btn-ln2-override-toggle', component_property='style'),
    Input(component_id='btn-ln2-override-toggle', component_property='n_clicks'),
    prevent_initial_call=True
)
def update_ln2_override_toggle_btn(n_clicks):
    if "btn-ln2-override-toggle" == ctx.triggered_id:
        # TODO: add functionality for LN2 override toggle button
        print("The LN2 override toggle button has been clicked")
        
        if n_clicks % 2 == 1:
            # button is on
            return {'background-color': "green",
                    'height': "10vh",
                    'width': "10vh",
                    'border-radius': "100%",
                    'border': '2px solid black',
                    'background-color': 'rgb(55,140,77)',
                    'box-shadow': '0px 0px 3px 3px rgb(62,200,87)'}
        else:
            return {'background-color': "grey",
                    'height': "10vh",
                    'width': "10vh",
                    'border-radius': "100%",
                    'border': '2px solid black'}
        

# Callback function for when LN2 override on/off button is pressed
@callback(
    Output(component_id='btn-ln2-override-on-off', component_property='style'),
    Input(component_id='btn-ln2-override-on-off', component_property='n_clicks'),
    prevent_initial_call=True
)
def update_ln2_override_on_off_btn(n_clicks):
    if "btn-ln2-override-on-off" == ctx.triggered_id:
        # TODO: add functionality for LN2 override on/off button
        print("The LN2 override on/off button has been clicked")
        
        if n_clicks % 2 == 1:
            # button is on
            return {'background-color': "green",
                    'height': "10vh",
                    'width': "10vh",
                    'border-radius': "100%",
                    'border': '2px solid black',
                    'background-color': 'rgb(55,140,77)',
                    'box-shadow': '0px 0px 3px 3px rgb(62,200,87)'}
        else:
            return {'background-color': "grey",
                    'height': "10vh",
                    'width': "10vh",
                    'border-radius': "100%",
                    'border': '2px solid black'}
        

# callback function for when pass through max is changed
@callback(
    Input(component_id="temp-pass-through-max-in", component_property='value')
)
def update_pass_through_max(max):
    # TODO: add functionality for pass through max change
    print("Pass Through Max changed to ", max)
    return

# Callback function for when pass-through min is changed
@callback(
    Input(component_id="temp-pass-through-min-in", component_property='value')
)
def update_pass_through_min(min_value):
    # Functionality for pass-through min change
    print("Pass Through Min changed to", min_value)
    return

# Callback function for when LN2 object target is changed
@callback(
    Input(component_id="temp-ln2-object-target-in", component_property='value')
)
def update_ln2_object_target(target_value):
    # Functionality for LN2 object target change
    print("LN2 Object Target changed to", target_value)
    return

# Callback for LN2 On Time Input
@callback(
    Input(component_id="temp-ln2-ln2-on-time-in", component_property='value')
)
def update_ln2_on_time(ln2_on_time):
    print("LN2 On Time changed to", ln2_on_time)
    return

# Callback for LN2 Shroud Min Input
@callback(
    Input(component_id="temp-ln2-shroud-min-in", component_property='value')
)
def update_ln2_shroud_min(shroud_min):
    print("LN2 Shroud Min changed to", shroud_min)
    return

# Callback for Heater Object Target Input
@callback(
    Input(component_id="temp-heater-object-target-in", component_property='value')
)
def update_heater_object_target(heater_target):
    print("Heater Object Target changed to", heater_target)
    return

# Callback for Heater Over Temp Input
@callback(
    Input(component_id="temp-heater-over-temp-in", component_property='value')
)
def update_heater_over_temp(over_temp):
    print("Heater Over Temp changed to", over_temp)
    return

# Callback for Heater Max Input
@callback(
    Input(component_id="temp-heater-heater-max-in", component_property='value')
)
def update_heater_max(heater_max):
    print("Heater Max changed to", heater_max)
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


# callback function for when file path is changed
@callback(
    Input(component_id="file-path-in", component_property='value')
)
def update_file_path(path):
    # TODO: add functionality for file path change
    print("File path changed to ", path)
    return


# callback function for when file name is changed
@callback(
    Input(component_id="file-name-in", component_property='value')
)
def update_file_name(name):
    # TODO: add functionality for file name change
    print("File name changed to ", name)
    return


# callback function for when logging freq is changed
@callback(
    Input(component_id="log-freq-in", component_property='value')
)
def update_log_freq(freq):
    # TODO: add functionality for logging freq change
    print("Logging frequency changed to ", freq)
    return


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


if __name__ == '__main__':
    app.run(debug=True)
