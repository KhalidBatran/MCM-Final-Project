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

CONTENT_STYLE_COLLAPSED = {
    "margin-left": "2rem",
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
                dbc.NavLink("Daily Medals Statistics", href="/fig4", active="exact"),  # New link for fig4
            ],
            vertical=True,
            pills=True,
        ),
    ],
    id="sidebar",
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
            html.Br(),
            html.H2("Olympics Bar Chart"),
            html.P("This visualization allows you to explore the total count of Olympic medals won by different countries, "
                   "broken down by medal type (Gold, Silver, Bronze). You can filter the data by country and sport."),
            html.Br(),
            html.H2("Olympics Line Progression"),
            html.P("This chart shows how athletes' medal counts progress over the dates of the competition. You can filter the data "
                   "by country and specific dates."),
            html.Br(),
            html.H2("Olympics Gender Comparison"),
            html.P("This bar chart compares the medals won by athletes of different genders, broken down by medal type. "
                   "You can filter the data by country."),
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
        return fig4_layout()  # New layout function for fig4
    return html.Div(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ],
        className="p-3 bg-light rounded-3",
    )

# Figure 4 layout and callback
def fig4_layout():
    return html.Div([
        html.H1("Daily Olympic Medals and Country Statistics", style={'textAlign': 'center'}),
        dcc.Graph(id='medals-daily-animation'),
        html.P("Drag the slider to change the date and observe the changes in Olympic medals data."),
    ])

@app.callback(
    Output('medals-daily-animation', 'figure'),
    Input('url', "pathname")
)
def update_fig4(pathname):
    if pathname == "/fig4":
        dff = df.copy()
        fig = px.scatter(dff, x="gdpPercap", y="lifeExp", animation_frame="Day Month", animation_group="Athlete Name",
                         size="pop", color="continent", hover_name="Country Code",
                         log_x=True, size_max=55, range_x=[100, 100000], range_y=[25, 90])
        fig["layout"].pop("updatemenus")  # Remove the play button and other animation controls
        return fig
    else:
        return {}

if __name__ == "__main__":
    app.run_server(debug=True)
