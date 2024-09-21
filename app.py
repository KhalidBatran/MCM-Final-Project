import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html
import pandas as pd
import plotly.express as px

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])
server = app.server

# Assuming your DataFrame is ready to use
df = pd.read_csv("https://raw.githubusercontent.com/KhalidBatran/MCM-Final-Project/main/assets/Olympics%202024.csv")
df['Medal Date'] = pd.to_datetime(df['Medal Date'], format='%d-%b')
df['Day Month'] = df['Medal Date'].dt.strftime('%d %b')

# Sidebar layout
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa"
}

CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem"
}

sidebar = html.Div(
    [
        html.H2("Menu", className="display-4"),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/", active="exact"),
                dbc.NavLink("Olympic Medals Progression", href="/fig2", active="exact"),
                dbc.NavLink("Animated Medals Statistics", href="/fig4", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

sidebar_toggle_button = dbc.Button("Toggle Sidebar", id="toggle-button", n_clicks=0, style={"margin": "10px"})

content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([
    dcc.Location(id="url"),
    sidebar_toggle_button,
    sidebar,
    content
])

# Callback for rendering pages
@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def render_page_content(pathname):
    if pathname == "/":
        return html.Div([html.H1("Home")])
    elif pathname == "/fig2":
        return fig2_layout()
    elif pathname == "/fig4":
        return fig4_layout()
    else:
        return html.Div([html.H1("404: Not found"), html.P("The pathname was not recognised...")])

# Figure 2 layout with new slider
def fig2_layout():
    return html.Div([
        html.H1("Olympic Medals Progression by Date", style={'textAlign': 'center'}),
        dcc.Graph(id='medals-line-chart'),
        dcc.RangeSlider(
            id='date-range-slider',
            min=0,
            max=len(df['Day Month'].unique()) - 1,
            value=[0, len(df['Day Month'].unique()) - 1],
            marks={i: {'label': date} for i, date in enumerate(df['Day Month'].unique())},
            step=None
        )
    ])

@app.callback(
    Output('medals-line-chart', 'figure'),
    Input('date-range-slider', 'value')
)
def update_fig2(date_range):
    filtered_df = df[(df['Day Month'] >= df['Day Month'].unique()[date_range[0]]) & 
                     (df['Day Month'] <= df['Day Month'].unique()[date_range[1]])]
    fig = px.line(filtered_df, x='Day Month', y='Athlete Name', title='Medals Over Time')
    return fig

# Figure 4 layout
def fig4_layout():
    dff = px.data.gapminder()  # Example data
    fig = px.scatter(dff, x="gdpPercap", y="lifeExp", animation_frame="year", animation_group="country",
                     size="pop", color="continent", hover_name="country",
                     log_x=True, size_max=55, range_x=[100, 100000], range_y=[25, 90])
    fig["layout"].pop("updatemenus")
    return dcc.Graph(figure=fig)

if __name__ == "__main__":
    app.run_server(debug=True)
