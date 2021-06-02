# See PyCharm help at https://www.jetbrains.com/help/pycharm/
import json

import dash
import dash_core_components as dcc
import dash_html_components as html
import flat_table
import pandas as pd
import plotly.graph_objects as go
from dash.dependencies import Output, Input
from plotly.subplots import make_subplots

bs_theme = 'https://codepen.io/chriddyp/pen/bWLwgP.css'
external_stylesheets = [bs_theme]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


def import_data():
    with open('snapshots.json') as data:
        read_content = json.load(data)
        df = pd.json_normalize(read_content)

    new_df = flat_table.normalize(df)
    return new_df


df = import_data()

"""some variables"""
df['date'] = pd.to_datetime(df['date'])
df['date'] = df['date'] + pd.offsets.DateOffset(years=7)
df['year'] = df.date.dt.year
df['s2f_ratio'] = round((df['coins.priceUSD'] / 0.18) ** (1 / 3.36), 1).astype(int)

app.layout = html.Div([
    dcc.Graph(id='graph_with_slider', style={'height': 644}),

    html.H3('Stock to flow slider'),
    html.Br(),

    html.Div(id='sliders', children=[
        dcc.Slider(
            id='s2f_ratio_slider',
            step=1,
            marks={str(i): str(i) for i in df['s2f_ratio'].sort_values().unique()},

        ),
        html.Div(id='slider_output'),
        html.H2('Coin Name'),
        dcc.Dropdown(id='coin_name',
                     options=[{'label': i, 'value': i} for i in df['coins.name'].unique()],
                     value='Bitcoin')])
])


@app.callback([Output('s2f_ratio_slider', 'min'),
               Output('s2f_ratio_slider', 'max'),
               Output('s2f_ratio_slider', 'marks'),
               Output('s2f_ratio_slider', 'value')
               ],
              Input('coin_name', 'value'))
def populate_pressure_slider(coin):
    min_v = round(int(df['s2f_ratio'][df['coins.name'] == coin].min()))
    max_v = round(int(df['s2f_ratio'][df['coins.name'] == coin].max()))
    marks_v = {str(i): str(i) for i in df['s2f_ratio'][df['coins.name'] == coin].sort_values().unique()}
    value = round(int(df['s2f_ratio'][df['coins.name'] == coin].min()))
    return min_v, max_v, marks_v, value


@app.callback(
    Output("graph_with_slider", "figure"),
    [Input("s2f_ratio_slider", "value"),
     Input('coin_name', 'value')])
def update_graph_with_s2f(s2f, coin):
    coin_df = df[df['coins.name'] == coin]
    s2f_df = coin_df[(coin_df['s2f_ratio'] == s2f)]

    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(
            x=s2f_df['date'],
            y=s2f_df['coins.availableSuppy'],
            name="Circulating",
            mode='lines',
            line=dict(shape="spline", smoothing=1.3, width=3, color='green'),
            # marker=dict(size=10, symbol='circle', color='white',
            #             line=dict(color='orange', width=2)
            #             ),
        ), secondary_y=False
    )

    fig.add_trace(
        go.Scatter(
            x=s2f_df['date'],
            y=s2f_df['coins.priceUSD'],
            name="Price (USD)",
            mode='lines',
            line=dict(shape="spline", smoothing=1.3, width=3, color='#FF00FF'),
            # marker=dict(size=10, symbol='circle', color='white',
            #             line=dict(color='#FF00FF', width=2)
            #             ),
        ), secondary_y=True
    )

    # Add figure title
    fig.update_layout(
        title_text="Stock to flow UI Example"
    )

    # Set x-axis title
    fig.update_xaxes(title_text="<b>Date</b>")

    # Set y-axes titles
    fig.update_yaxes(
        title_text="<b>Circulating</b>",
        secondary_y=False)
    fig.update_yaxes(
        title_text="<b>Price in USD</b>",
        secondary_y=True)

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)

