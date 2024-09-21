Perfect:

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html
import pandas as pd
import plotly.express as px

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])
server = app.server

# Load the cleaned dataset
df = pd.read_csv("https://raw.githubusercontent.com/KhalidBatran/MCM-Exercise-3/main/assets/Olympics%202024.csv")

# Ensure 'Medal Date' is parsed correctly, handling the specific format
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
    return html.Div(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ],
        className="p-3 bg-light rounded-3",
    )

# Callback for the sidebar toggle button
@app.callback(
    [Output("sidebar", "style"), Output("page-content", "style")],
    Input("toggle-button", "n_clicks")
)
def toggle_sidebar(n_clicks):
    if n_clicks % 2 == 1:
        return {"display": "none"}, CONTENT_STYLE_COLLAPSED
    return SIDEBAR_STYLE, CONTENT_STYLE

# Figure 1 layout and callback
def fig1_layout():
    return html.Div([
        html.H1('Olympic Medals Count by Country', style={'textAlign': 'center'}),
        dcc.Dropdown(
            id='dropdown-country',
            options=[{'label': 'All', 'value': 'All'}] + [{'label': i, 'value': i} for i in df['Country Code'].unique()],
            value='All',
            multi=True,
            clearable=False,
            placeholder="Choose a Country"
        ),
        dcc.Dropdown(
            id='dropdown-sport',
            options=[{'label': 'All', 'value': 'All'}] + [{'label': s, 'value': s} for s in df['Sport Discipline'].dropna().unique()],
            value='All',
            multi=False,
            clearable=False,
            placeholder="Choose a Sport"
        ),
        dcc.Graph(id="medals-count")
    ])

@app.callback(
    Output('medals-count', 'figure'),
    [Input('dropdown-country', 'value'), Input('dropdown-sport', 'value')]
)
def update_fig1(selected_countries, selected_sport):
    filtered_df = df if 'All' in selected_countries or not selected_countries else df[df['Country Code'].isin(selected_countries)]
    if selected_sport != 'All':
        filtered_df = filtered_df[filtered_df['Sport Discipline'] == selected_sport]
    medal_counts = filtered_df.groupby(['Country Code', 'Medal Type']).size().reset_index(name='Count')
    # Color mapping for Gold, Silver, and Bronze
    fig = px.bar(medal_counts, x='Country Code', y='Count', color='Medal Type', barmode='group',
                 color_discrete_map={'Gold Medal': '#FFD700', 'Silver Medal': '#C0C0C0', 'Bronze Medal': '#CD7F32'})
    # Remove "medal type" from hover information
    fig.update_traces(hovertemplate='<b>Country Code:</b> %{x}<br><b>Count:</b> %{y}<extra></extra>')
    return fig

# Figure 2 layout and callback
def fig2_layout():
    slider_marks = {i: {'label': date.strftime('%b %d')} for i, date in enumerate(sorted(df['Medal Date'].dt.date.unique()))}
    slider_marks[-1] = {'label': 'All'}
    return html.Div([
        html.H1("Olympic Athletes' Medal Progression by Date", style={'textAlign': 'center'}),
        dcc.Dropdown(
            id='country-dropdown-fig2',
            options=[{'label': 'All', 'value': 'All'}] + [{'label': country, 'value': country} for country in df['Country Code'].unique()],
            value='All',
            clearable=False,
            style={'width': '50%', 'margin': '10px auto'},
            placeholder="Choose a country"
        ),
        dcc.Graph(id='medals-line-chart'),
        dcc.Slider(
            id='date-slider',
            min=-1,
            max=len(df['Medal Date'].dt.date.unique()) - 1,
            value=-1,
            marks=slider_marks,
            step=None
        )
    ])

@app.callback(
    Output('medals-line-chart', 'figure'),
    [Input('date-slider', 'value'), Input('country-dropdown-fig2', 'value')]
)
def update_fig2(slider_value, selected_country):
    filtered_df = df if slider_value == -1 else df[df['Medal Date'].dt.date == df['Medal Date'].dt.date.unique()[slider_value]]
    if selected_country != 'All':
        filtered_df = filtered_df[filtered_df['Country Code'] == selected_country]
    
    # Add medal type, country code, gender, and sport discipline to hover information, but remove date and index
    fig = px.line(
        filtered_df,
        x='Day Month',  # Day and month will remain as the x-axis but not in hover data
        y=filtered_df.index,  # The y-axis is based on the index, but index will not be included in hover data
        color='Athlete Name',
        markers=True,
        hover_data={
            'Medal Type': True, 
            'Country Code': True, 
            'Gender': True, 
            'Sport Discipline': True,
            'Day Month': False,  # Removing 'Day Month' from hover
            filtered_df.index.name: False  # Removing index from hover
        }
    )
    return fig

# Figure 3 layout and callback
def fig3_layout():
    return html.Div([
        html.H1("Total Medals by Gender", style={'textAlign': 'center'}),
        dcc.Dropdown(
            id='country-dropdown-fig3',
            options=[{'label': i, 'value': i} for i in df['Country Code'].unique()],
            value=['All'],  # Default to 'All' if it makes sense, or adjust as needed
            multi=True,
            style={'width': '50%', 'margin': '10px auto'},
            placeholder="Select countries"
        ),
        dcc.Graph(id='gender-medal-facet-bar-chart')
    ])

@app.callback(
    Output('gender-medal-facet-bar-chart', 'figure'),
    [Input('country-dropdown-fig3', 'value')]
)
def update_fig3(selected_countries):
    # Filter the dataframe based on selected countries
    if 'All' in selected_countries or not selected_countries:
        filtered_df = df
    else:
        filtered_df = df[df['Country Code'].isin(selected_countries)]
    
    # Aggregate data by gender and medal type
    medal_counts = filtered_df.groupby(['Gender', 'Medal Type']).size().reset_index(name='Count')
    
    # Create the bar chart faceted by gender
    fig = px.bar(
        medal_counts,
        x='Medal Type',
        y='Count',
        color='Gender',
        barmode='group',
        facet_col='Gender',
        category_orders={
            "Medal Type": ["Bronze Medal", "Silver Medal", "Gold Medal"], 
            "Gender": ["M", "F"]
        },
        color_discrete_map={"M": "blue", "F": "pink"}
    )
    return fig
    
# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
