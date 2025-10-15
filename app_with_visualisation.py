from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output
import pandas as pd
from matplotlib import pyplot as plt
import webbrowser
from waitress import serve
import base64
import io
import matplotlib
from math_functions import remainder_method, dHont_rull, division_method
matplotlib.use('agg')

num_of_places_in = -1
parties_votes_in = pd.DataFrame()

quotas = [
        {"label": "Квота Хара (QH)", "value": "QH"},
        {"label": "Квота Друпа (QD)", "value": "QD"},
        {"label": "Нормальная имперская квота (QNI)", "value": "QNI"},
        {"label": "Усиленная имперская квота (QRI)", "value": "QRI"},
        ]
quotas_dict = pd.DataFrame(quotas).set_index('value').label.to_dict()

other_methods = [
        {"label": "Метод д'Онта (dHont)", "value": "dHont"},
        ]
        
divisor_methods = [
        {"label": "Метод наименьшего делителя, Метод Адамса (SD)", "value": "SD"},
        {"label": "Метод наибольшего делителя, метод Джефферсона (LD)", "value": "LD"},
        {"label": "Среднее арифметическое, Система Сент-Лаге, метод Уэбстера (AM)", "value": "AM"},
        {"label": "Среднее геометрическое, метод Хилла (GM)", "value": "GM"},
        {"label": "Среднее гармоническое, метод Дина (HM)", "value": "HM"},
        {"label": "Дитская ситема (D)", "value": "D"},
        {"label": "Модифицированная система Сент-Лаге (MSL)", "value": "MSL"},
        ]

other_methods_dict = pd.DataFrame(other_methods).set_index('value').label.to_dict()
divisor_methods_dict = pd.DataFrame(divisor_methods).set_index('value').label.to_dict()

"""
external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
        "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]
app = Dash(
    __name__,
    external_stylesheets=external_stylesheets,
)
app.title = "charts drawing"
"""
app = Dash(prevent_initial_callbacks=True)
app.title = "Методы пропорционального представительства"
app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.H1(children="Процедура пропорционального представительства", className="header-title"),
            ],
            className="header",
        ),
        dcc.Upload(
            id='load-data',
            children=html.Div([
                html.A('Load data')
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            multiple=False,
        ),
        html.Div(
            children=[
                html.Div(
                    id="num-of-places-div",
                    style={'display': 'block'},
                    children=[
                        'Введите количество мест в парламенте: ',
                        dcc.Input(
                        id="num-of-places-input",
                        type="text",
                        placeholder="",
                        pattern=r'[0-9]*',  # только цифры
                        debounce=True
                        )
                    ],
                ),
                html.Div(children=[
                        html.Div(children=[
                            "Методы наибольшего остатка",
                            dcc.Checklist(
                                id="reminder_methods",
                                options=quotas,
                                className="checklist",
                                inputStyle={"margin-right": "5px", "margin-left": "10px"},
                                labelStyle={'display': 'block'},
                            )
                            ],
                        ),
                        html.Div(children=[
                            "Метод наибольшего среднего",
                            dcc.Checklist(
                                id="other_methods",
                                options=other_methods,
                                className="checklist",
                                inputStyle={"margin-right": "5px", "margin-left": "10px"},
                                labelStyle={'display': 'block'},
                            )
                            ],
                        ),
                        html.Div(children=[
                            "Методы делителей",
                            dcc.Checklist(
                                id="divisor_methods",
                                options=divisor_methods,
                                className="checklist",
                                inputStyle={"margin-right": "5px", "margin-left": "10px"},
                                labelStyle={'display': 'block'},
                            )
                            ],
                        ),
                    ],
                    id="methods",
                    style={'display': 'none'},
                ),

                html.Div(
                    children = [
                        "Выберите хотя бы один метод пропорционального представителства.",
                    ],
                    id='res',
                ),
            ],
            id="data-processing",
            style={'display': 'none'},
        )
    ]
)

@app.callback(
    Output("data-processing", 'style'),
    Output("reminder_methods", 'value'),
    Output("other_methods", 'value'),
    Output("num-of-places-input", 'value'),
    [
        Input("load-data", 'contents'),
    ],
)
def load_func(load_data):
    global parties_votes_in#, parties_places_table
    #print('I am in load_func')
    content_type, content_string = load_data.split(',')
    decoded = base64.b64decode(content_string)
    parties_votes_in = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
    #print(parties_votes_in)
    parties_votes_in.Votes = parties_votes_in.Votes.astype(float)
    #parties_places_table  = parties_votes_in.copy()
    #print(parties_votes_in)
    return {'display': 'block'}, list(), list(), str()

@app.callback(
    Output("methods", 'style'),
    [
        Input("num-of-places-input", 'value'),
    ],
)
def num_of_places_input_func(num_of_places_input):
    global num_of_places_in
    if num_of_places_input:
        num_of_places_in = int(num_of_places_input)
        style={'display': 'block'}
    else:
        style={'display': 'none'}
    return style

@app.callback(
    Output("res", 'children'),
    [
        Input("reminder_methods", 'value'),
        Input("other_methods", 'value'),
        Input("divisor_methods", 'value'),
    ],
)
def choose_reminder_method(reminder_methods, other_methods, divisor_methods):
    global parties_votes_in, num_of_places_in#, parties_places_table

    if (not reminder_methods) and (not other_methods) and (not divisor_methods):
        return "Выберите хотя бы один метод пропорционального представителства."
    
    parties_places_table  = parties_votes_in.copy()

    for method in reminder_methods:
        parties_places_table[quotas_dict[method]] = remainder_method(parties_votes_in, method, num_of_places_in)
    
    #print(parties_places_table)
    if 'dHont' in other_methods:
        parties_places_table[other_methods_dict['dHont']] = dHont_rull(parties_votes_in, num_of_places_in)
        
    for method in divisor_methods:
        parties_places_table[divisor_methods_dict[method]] = division_method(parties_votes_in, method, num_of_places_in)

    return dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in parties_places_table.columns],
        data=parties_places_table.to_dict('records')
    )
    
    #dHont_rull(parties_votes_in, num_of_places_in)




if __name__ == "__main__":
    webbrowser.open("http://localhost:8050")
    serve(app.server, host="0.0.0.0", port=8050)
