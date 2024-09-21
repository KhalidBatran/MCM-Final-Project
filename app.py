import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html
import pandas as pd
import plotly.express as px

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])
server = app.server

df = pd.read_csv("https://raw.githubusercontent.com/KhalidBatran/MCM-Final-Project/main/assets/Olympics%202024.csv")
df['Medal Date'] = pd.to_datetime(df['Medal Date'], errors='coerce', format='%d-%b')
df = df.dropna(subset=['Medal Date'])
df['Day Month'] = df['Medal Date'].dt.strftime('%d %b')

# Sidebar layout
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
    "transition": "0.3s"
}

CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
    "transition": "0.3s",
}

# Collapsible Sidebar
sidebar = html.Div(
    [
        html.H2("Menu", className="display-4"),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/", active="exact"),
                dbc.NavLink("Olympics Bar Chart", href="/fig1", active="exact"),
                dbc.NavLink("Olympics Line Progression", href="/fig2", active="exact"),
                dbc.NavLink("Olympics Gender Comparison", href="/fig3", active="exact"),
                dbc.NavLink("Daily Medals Statistics", href="/fig4", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

# Button to toggle the sidebar
sidebar_toggle_button = dbc.Button("Toggle Sidebar", id="toggle-button", n_clicks=0, style={"margin": "10px"})

# Content layout
content = html.Div(id="page-content", style=CONTENT_STYLE)

# App layout
app.layout = html.Div([
    dcc.Location(id="url"),
    sidebar_toggle_button,
    sidebar,
    content
])

# Home Page Layout
def home_layout():
    return html.Div(
        style={"textAlign": "center"},
        children=[
            html.H1("The Olympic Medals Visualization", style={'font-weight': 'bold', 'margin-bottom': '20px'}),
            html.P("Welcome to the Olympic Medals Dashboard! Here, you can explore data from the Olympic Games for this year. "
                   "This dashboard provides insights into Olympic athletes and their achievements."),
        ]
    )

# Callback to render the appropriate page content based on the URL
@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def render_page_content(pathname):
    if pathname == "/":
        return home_layout()
    elif pathname == "/fig1":
        return fig1_layout()
    elif pathname == "/fig2":
        return fig2_layout()
    elif pathname == "/fig3":
        return fig3_layout()
    elif pathname == "/fig4":
        return fig4_layout()
    else:
        return html.Div([
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ])

# Define layouts and callbacks for fig1, fig2, fig3, fig4 as needed.
# Placeholder function definitions for fig1, fig2, fig3
def fig1_layout():
    return html.Div([html.H1("Figure 1 Title")])
def fig2_layout():
    return html.Div([html.H1("Figure 2 Title")])
def fig3_layout():
    return html.Div([html.H1("Figure 3 Title")])

def fig4_layout():
    return html.Div([
        html.H1("Daily Olympic Medals and Country Statistics", style={'textAlign': 'center'}),
        dcc.Graph(id='medals-daily-animation'),
    ])

@app.callback(
    Output('medals-daily-animation', 'figure'),
    Input('url', "pathname")
)
def update_fig4(pathname):
    if pathname == "/fig4":
        dff = df.copy()
        fig = px.scatter(dff, x="Country Code", y="Medal Type", animation_frame="Day Month", animation_group="Athlete Name",
                         size="Medal Type", color="Gender", hover_name="Athlete Name",
                         size_max=55)
        fig["layout"].pop("updatemenus")  # Remove the play button and other animation controls
        return fig
    else:
        return {}

if __name__ == "__main__":
    app.run_server(debug=True)
