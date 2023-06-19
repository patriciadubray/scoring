import pandas as pd
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import requests
import base64
import os
import re
import dash_table

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Lire les données à partir du fichier CSV
pred = pd.read_csv('/home/patriciadubray/mysite/df_pred_display.csv')
train = pd.read_csv('/home/patriciadubray/mysite/df_train.csv')

# Passer la première colonne en index
pred = pred.set_index('SK_ID_CURR')

# Créer les options pour le dropdown
options = [{'label': str(i), 'value': str(i)} for i in pred.index.unique()]

# URL de l'API
api_url = 'http://api-patriciadubray.pythonanywhere.com/predict'

# Fonction pour encoder les images
def encode_image(image_file):
    with open(image_file, 'rb') as f:
        encoded_image = base64.b64encode(f.read()).decode('ascii')
    return 'data:image/png;base64,{}'.format(encoded_image)

# fonction pour encoder l'image et l'utiliser dans le layout
logo_src = encode_image('/home/patriciadubray/mysite/logo.png')

# Layouts

# --- Home Layout ---
home_layout = html.Div(
    style={'backgroundColor': 'black', 'padding': '20px'},
    children=[
        dbc.Row(
            [
                dbc.Col(html.H1("Prêt à dépenser", style={'color': 'white', 'textAlign': 'left'}), width=8),
                dbc.Col(html.Img(src=logo_src, style={'width': '150px', 'height': 'auto', 'float': 'right'}), width=4),
            ],
            style={'marginBottom': '20px'}
        ),
        dbc.Row(
            dbc.Col(
                html.Div(
                    [
                        dcc.Link('Prédictions', href='/predictions', style={'marginRight': '10px'}),
                        dcc.Link('Comparaisons', href='/comparisons', style={'marginRight': '10px'}),
                        dcc.Link('Fichier Client', href='/client_file', style={'marginRight': '10px'}),
                    ],
                    className="nav"
                ),
                width=12
            ),
            style={'marginBottom': '20px'}
        ),
    ]
)

# --- Prédictions Layout ---
predictions_layout = html.Div(
    style={'backgroundColor': 'black', 'padding': '20px'},
    children=[
        dbc.Row(
            [
                dbc.Col(html.H1("Prédictions", style={'color': 'white', 'textAlign': 'left'}), width=8),
                dbc.Col(
                    html.Img(
                        id='logo',
                        src=logo_src,
                        style={'width': '150px', 'height': 'auto', 'float': 'right'}
                    ),
                    width=4
                ),
            ],
            style={'marginBottom': '20px'}
        ),
        dbc.Row(
            dbc.Col(
                html.Div(
                    [
                        dcc.Link('Retour à l\'accueil', href='/'),
                    ],
                    className="nav"
                ),
                width=12
            ),
            style={'marginBottom': '20px'}
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        style={'position': 'relative'},
                        children=[
                            dcc.Dropdown(
                                id='client-dropdown',
                                options=options,
                                value='',
                                placeholder='Sélectionnez un client',
                                style={'width': '100%'}
                            ),
                            html.P(
                                "Sélectionnez un client",
                                style={'position': 'absolute', 'top': '-20px', 'left': '5px', 'color': 'white',
                                       'fontSize': '12px'}
                            )
                        ]
                    ),
                    width=4
                ),
                dbc.Col(
                    html.Img(
                        id='alert-image',
                        src='',
                        style={'width': '150px', 'height': 'auto', 'float': 'left'}
                    ),
                    width=4
                ),
            ],
            style={'marginBottom': '20px'}
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.Div(id='output', style={'color': 'white', 'textAlign': 'center', 'marginTop': '20px'}),
                    width=4
                ),
                dbc.Col(
                    html.Div(
                        style={'display': 'none', 'marginTop': '20px'},
                        children=[
                            html.P("Ci-dessous un graphique pour comprendre l'impact positif (bleu) et négatif (rose) sur la probabilité :",
                                   style={'color': 'white'}),
                            html.Img(
                                id='summary-plot',
                                src='',
                                style={'width': '100%', 'height': 'auto'}
                            )
                        ],
                        id='summary-container'
                    ),
                    width=8
                ),
            ]
        ),
        html.Div(id='predictions', style={'color': 'white', 'textAlign': 'center'})
    ]
)

# --- Comparisons Layout ---
comparisons_layout = html.Div(
    style={'backgroundColor': 'black', 'padding': '20px'},
    children=[
        dbc.Row(
            [
                dbc.Col(html.H1("Comparaisons", style={'color': 'white', 'textAlign': 'left'}), width=8),
                dbc.Col(html.Img(src=logo_src, style={'width': '150px', 'height': 'auto', 'float': 'right'}), width=4),
            ],
            style={'marginBottom': '20px'}
        ),
        dbc.Row(
            dbc.Col(
                html.Div(
                    [
                        dcc.Link('Retour à l\'accueil', href='/'),
                    ],
                    className="nav"
                ),
                width=12
            ),
            style={'marginBottom': '20px'}
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        style={'position': 'relative'},
                        children=[
                            dcc.Dropdown(
                                id='client-dropdown-comparisons',
                                options=options,
                                value='',
                                placeholder='Sélectionnez un client',
                                style={'width': '100%'}
                            ),
                            html.P(
                                "Sélectionnez un client",
                                style={'position': 'absolute', 'top': '-20px', 'left': '5px', 'color': 'white',
                                       'fontSize': '12px'}
                            )
                        ]
                    ),
                    width=4
                ),
            ],
            style={'marginBottom': '20px'}
        ),
        # Graphiques
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id='graph-days-birth'), width=6),
                dbc.Col(dcc.Graph(id='graph-days-employed'), width=6),
            ],
            style={'marginBottom': '20px'}
        ),
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id='graph-ext-source-2'), width=6),
                dbc.Col(dcc.Graph(id='graph-ext-source-3'), width=6),
            ],
            style={'marginBottom': '20px'}
        ),
    ]
)

# --- Client File Layout ---
client_file_layout = html.Div(
    style={'backgroundColor': 'black', 'padding': '20px'},
    children=[
        dbc.Row(
            [
                dbc.Col(html.H1("Fichier Client", style={'color': 'white', 'textAlign': 'left'}), width=8),
                dbc.Col(html.Img(src=logo_src, style={'width': '150px', 'height': 'auto', 'float': 'right'}), width=4),
            ],
            style={'marginBottom': '20px'}
        ),
        dbc.Row(
            dbc.Col(
                html.Div(
                    [
                        dcc.Link('Retour à l\'accueil', href='/'),
                    ],
                    className="nav"
                ),
                width=12
            ),
            style={'marginBottom': '20px'}
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        style={'position': 'relative'},
                        children=[
                            dcc.Dropdown(
                                id='client-dropdown-file',
                                options=options,
                                value='',
                                placeholder='Sélectionnez un client',
                                style={'width': '100%'}
                            ),
                            html.P(
                                "Sélectionnez un client",
                                style={'position': 'absolute', 'top': '-20px', 'left': '5px', 'color': 'white',
                                       'fontSize': '12px'}
                            )
                        ]
                    ),
                    width=4
                ),
            ],
            style={'marginBottom': '20px'}
        ),
        dbc.Row(
            dbc.Col(
                dash_table.DataTable(
                    id='table',
                    filter_action="native",  # activer le filtrage
                    style_data={
                        'backgroundColor': 'white',  # Fond blanc pour toutes les lignes
                        'color': 'black'  # Texte noir pour toutes les lignes
                    },
                    style_cell={
                        'textAlign': 'left'  # Alignement du texte à gauche dans les cellules
                    }
                ),
                width=12
            ),
        )
    ]
)


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/predictions':
         return predictions_layout
    elif pathname == '/comparisons':
         return comparisons_layout
    elif pathname == '/client_file':
         return client_file_layout
    else:
        return home_layout

# Conserver la fonction de rappel pour la page Prédictions
@app.callback(
    [Output('output', 'children'),
     Output('predictions', 'children'),
     Output('summary-container', 'style'),
     Output('summary-plot', 'src'),
     Output('logo', 'src'),
     Output('alert-image', 'src')],
    [Input('client-dropdown', 'value')]
)
def update_output_and_predictions(selected_client):
    if selected_client:
        client_data = pred.loc[int(selected_client)].copy()

        response = requests.post(api_url, json=client_data.to_dict())

        try:
            result = response.json()
            class_0 = result['class_0']
            class_1 = result['class_1']
            summary_plot_path = result['summary_plot_path']

            directory = '/home/patriciadubray/mysite'

            alert_image_path = os.path.join(directory, 'attention.png') if float(re.findall("\d+\.\d+", class_0)[0]) < 50 else os.path.join(directory, 'check.png')
            encoded_alert_image = base64.b64encode(open(alert_image_path, 'rb').read()).decode('ascii')
            alert_image_src = 'data:image/png;base64,{}'.format(encoded_alert_image)

            summary_plot_path = os.path.join(directory, summary_plot_path)
            encoded_image = base64.b64encode(open(summary_plot_path, 'rb').read()).decode('ascii')
            image_src = 'data:image/png;base64,{}'.format(encoded_image)

            logo_path = os.path.join(directory, 'logo.png')
            encoded_logo = base64.b64encode(open(logo_path, 'rb').read()).decode('ascii')
            logo_src = 'data:image/png;base64,{}'.format(encoded_logo)

            output = html.Div([
                html.H3("Probabilités pour le client sélectionné :", style={'textAlign': 'center'}),
                html.P(class_0),
                html.P(class_1),
            ])

            predictions = ''

            return output, predictions, {'display': 'block'}, image_src, logo_src, alert_image_src
        except ValueError:
            error_message = html.Div("Erreur lors de la récupération des prédictions")
            return error_message, error_message, {'display': 'none'}, '', '', ''
    else:
        #no_client_message = html.Div("", style={'textAlign': 'center'})
        directory = '/home/patriciadubray/mysite'
        logo_path = os.path.join(directory, 'logo.png')
        encoded_logo = base64.b64encode(open(logo_path, 'rb').read()).decode('ascii')
        logo_src = 'data:image/png;base64,{}'.format(encoded_logo)
        return '', {'display': 'none'}, '', logo_src, ''

# Ajouter une nouvelle fonction de rappel pour mettre à jour les graphiques en fonction du client sélectionné
@app.callback(
    [Output('graph-days-birth', 'figure'),
     Output('graph-days-employed', 'figure'),
     Output('graph-ext-source-2', 'figure'),
     Output('graph-ext-source-3', 'figure')],
    [Input('client-dropdown-comparisons', 'value')]
)
def update_graphs(selected_client):
    if selected_client:
        client_data = pred.loc[int(selected_client)].copy()

        fig1 = px.histogram(train, x=(-train['DAYS_BIRTH']/365), color='TARGET', nbins=100, histnorm='percent',
                            color_discrete_sequence=['lightpink', 'lightblue'])
        fig1.update_layout(xaxis_title='AGE')
        fig1.add_vline(x=-client_data['DAYS_BIRTH']/365, line_width=3, line_dash="dash", line_color="red")

        fig2 = px.histogram(train, x=train['AMT_ANNUITY'], color='TARGET', nbins=100, histnorm='percent',
                            color_discrete_sequence=['lightblue', 'lightpink'])
        fig2.update_layout(xaxis_title='AMT_ANNUITY')
        fig2.add_vline(x=client_data['AMT_ANNUITY'], line_width=3, line_dash="dash", line_color="red")

        fig3 = px.histogram(train, x='EXT_SOURCE_2', color='TARGET', nbins=100, histnorm='percent',
                            color_discrete_sequence=['lightpink', 'lightblue'])
        fig3.add_vline(x=client_data['EXT_SOURCE_2'], line_width=3, line_dash="dash", line_color="red")

        fig4 = px.histogram(train, x='EXT_SOURCE_3', color='TARGET', nbins=100, histnorm='percent',
                            color_discrete_sequence=['lightpink', 'lightblue'])
        fig4.add_vline(x=client_data['EXT_SOURCE_3'], line_width=3, line_dash="dash", line_color="red")

        return fig1, fig2, fig3, fig4

    else:
        return {}, {}, {}, {}

@app.callback(
    [Output('table', 'data'),
     Output('table', 'columns')],
    [Input('client-dropdown-file', 'value')]
)
def update_table(selected_client):
    if selected_client:
        client_data = pred.loc[int(selected_client)].copy().reset_index()
        client_data.columns = ['Variable', 'Valeur']

        data = client_data.to_dict('records')
        columns = [{"name": i, "id": i} for i in client_data.columns]

        return data, columns
    else:
        return [], []

if __name__ == '__main__':
    app.run_server(debug=True)