from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

# App Initialization
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
server = app.server

# Data Loading and Preparation
df = pd.read_csv("https://raw.githubusercontent.com/KhalidBatran/MCM-Final-Project/refs/heads/main/assets/Olympics%202024.csv")

# Print column names to see what's available
print("Available columns:", df.columns)

# Use 'Sport Discipline' instead of 'Sport'
df['Sport Discipline'] = df['Sport Discipline'].fillna('Unknown')

# Prepare the data for the figures
medal_counts = df.pivot_table(index='Country Code', columns='Medal Type', values='Athlete Name', 
                              aggfunc='count', fill_value=0).reset_index()
medal_counts.columns = ['Country Code', 'Bronze Medal', 'Gold Medal', 'Silver Medal']

medal_summary = df.groupby(['Country Code', 'Medal Date'])['Medal Type'].count().reset_index(name='Total Medals')

athlete_medals = df.groupby(['Gender', 'Athlete Name', 'Medal Type']).size().reset_index(name='Count')

# Layout and Callbacks for each Figure

# Figure 1: Olympic Medals Distribution (Bar Chart)
@app.callback(
    Output('fig1-container', 'children'),
    [Input('fig1-country-dropdown', 'value'),
     Input('fig1-sport-dropdown', 'value')]
)
def update_fig1(selected_countries, selected_sport):
    filtered_df = df
    if selected_countries and 'All' not in selected_countries:
        filtered_df = filtered_df[filtered_df['Country Code'].isin(selected_countries)]
    if selected_sport != 'All':
        filtered_df = filtered_df[filtered_df['Sport Discipline'] == selected_sport]
    
    medal_counts = filtered_df.pivot_table(index='Country Code', columns='Medal Type', values='Athlete Name', 
                                           aggfunc='count', fill_value=0).reset_index()
    
    # Ensure all medal types are present
    for medal_type in ['Bronze Medal', 'Silver Medal', 'Gold Medal']:
        if medal_type not in medal_counts.columns:
            medal_counts[medal_type] = 0
    
    medal_counts = medal_counts[['Country Code', 'Bronze Medal', 'Silver Medal', 'Gold Medal']]
    
    fig = px.bar(
        medal_counts, 
        x='Country Code', 
        y=['Gold Medal', 'Silver Medal', 'Bronze Medal'],
        title="Medals Distribution Across Different Countries in Olympics 2024",
        labels={"value": "Number of Medals", "variable": "Medal Type"},
        color_discrete_map={
            'Gold Medal': 'gold',
            'Silver Medal': 'silver',
            'Bronze Medal': '#cd7f32'
        },
        barmode='group'
    )
    return dcc.Graph(figure=fig)

# Figure 2: Medal Distribution by Country Over Time (Scatter Plot)
def get_fig2():
    fig = px.scatter(
        medal_summary,
        x='Country Code',
        y='Total Medals',
        size='Total Medals',
        animation_frame='Medal Date',
        title='Medal Distribution by Country Over Time',
        labels={'Total Medals': 'Number of Medals'},
        size_max=60
    )
    return fig

# Figure 3: Medal Distribution by Gender and Athletes (Treemap)
@app.callback(
    Output('fig3-container', 'children'),
    [Input('fig3-country-dropdown', 'value'),
     Input('fig3-sport-dropdown', 'value')]
)
def update_fig3(selected_countries, selected_sport):
    filtered_df = df
    if 'All' not in selected_countries and selected_countries:
        filtered_df = filtered_df[filtered_df['Country Code'].isin(selected_countries)]
    if selected_sport != 'All':
        filtered_df = filtered_df[filtered_df['Sport Discipline'] == selected_sport]
    
    athlete_medals = filtered_df.groupby(['Gender', 'Athlete Name', 'Medal Type']).size().reset_index(name='Count')
    
    fig = px.treemap(
        athlete_medals,
        path=['Gender', 'Medal Type', 'Athlete Name'],
        values='Count',
        color='Medal Type',
        color_discrete_map={"Gold Medal": "gold", "Silver Medal": "silver", "Bronze Medal": "#cd7f32"},
        title="Medal Distribution Among Athletes Categorized by Gender"
    )
    return dcc.Graph(figure=fig)

# Navbar and Layout
def create_figure_layout(figure_id, dropdown_id_prefix):
    return html.Div([
        dbc.Row([
            dbc.Col(dcc.Dropdown(
                id=f'{dropdown_id_prefix}-country-dropdown',
                options=[{'label': 'All', 'value': 'All'}] + [{'label': i, 'value': i} for i in sorted(df['Country Code'].unique())],
                multi=True,
                placeholder="Select Countries",
                value=['All']
            ), width=6, className="filter-dropdown"),
            dbc.Col(dcc.Dropdown(
                id=f'{dropdown_id_prefix}-sport-dropdown',
                options=[{'label': 'All', 'value': 'All'}] + [{'label': i, 'value': i} for i in sorted(df['Sport Discipline'].unique())],
                multi=False,
                placeholder="Select Sport",
                value='All'
            ), width=6, className="filter-dropdown"),
        ], className="filter-row"),
        html.Div(id=figure_id, className="figure-container")
    ])

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dbc.Navbar(
        dbc.Container(
            [
                html.A(html.Img(src="assets/MMU_Logo.png", height="25px"), href="/home", className="navbar-brand"),
                dbc.Nav(
                    [
                        dbc.NavItem(dbc.NavLink("Home", href="/home", className="nav-link", id="nav-home")),
                        dbc.NavItem(dbc.NavLink("Olympics Medal Distribution", href="/fig1", className="nav-link", id="nav-fig1")),
                        dbc.NavItem(dbc.NavLink("Country Medal Trends", href="/fig2", className="nav-link", id="nav-fig2")),
                        dbc.NavItem(dbc.NavLink("Athlete Performance", href="/fig3", className="nav-link", id="nav-fig3")),
                    ],
                    className="ms-auto",  # Right alignment
                    navbar=True
                ),
            ],
            fluid=True,
        ),
        color="light",
        dark=False,
        className="mb-5"
    ),
    html.Div(id='page-content', className='container-fluid mt-4')  # Central content
])

# Callback to Highlight Active Navbar Link
@app.callback(
    [Output('nav-home', 'className'),
     Output('nav-fig1', 'className'),
     Output('nav-fig2', 'className'),
     Output('nav-fig3', 'className')],
    [Input('url', 'pathname')]
)
def update_nav_active(pathname):
    base_class = 'nav-link'
    active_class = 'nav-link active'
    links = [base_class] * 4  # Default all links to not active
    if pathname == '/home':
        links[0] = active_class
    elif pathname == '/fig1':
        links[1] = active_class
    elif pathname == '/fig2':
        links[2] = active_class
    elif pathname == '/fig3':
        links[3] = active_class
    return links

# Page Content Rendering Callback
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def render_page_content(pathname):
    if pathname == "/home":
        return html.Div([
            html.H1("Welcome to the Olympics 2024 Dashboard"),
            html.P("This dashboard gives a detailed look at the 2024 Olympic Games, showing how medals were won across different countries, sports, and athletes. The data includes information about each athlete, the country they represented, their gender, and the type of medal they won—Gold, Silver, or Bronze. You can explore which countries performed best, see how medal totals changed over time, and compare performances between male and female athletes. The dashboard helps you understand the overall results of the Olympics, highlighting not only the top countries but also the individual sports that contributed to their success. It’s a great way to explore the achievements of athletes and see how different nations competed in the 2024 Games."),
            dbc.Button("Let's Have A Look", color="primary", href="/fig1")
        ], className="home-content")
    elif pathname == "/fig1":
        return html.Div([
            dbc.Row([
                dbc.Col(dcc.Dropdown(
                    id='fig1-country-dropdown',
                    options=[{'label': 'All', 'value': 'All'}] + [{'label': i, 'value': i} for i in sorted(df['Country Code'].unique())],
                    multi=True,
                    placeholder="Select Countries",
                    value=['All']
                ), width=6),
                dbc.Col(dcc.Dropdown(
                    id='fig1-sport-dropdown',
                    options=[{'label': 'All', 'value': 'All'}] + [{'label': i, 'value': i} for i in sorted(df['Sport Discipline'].unique())],
                    multi=False,
                    placeholder="Select Sport",
                    value='All',
                    clearable=False  # Add this line
                ), width=6),
            ], className="mb-4"),
            html.Div(id='fig1-container', className='figure1')  # Add className here
        ])
    elif pathname == "/fig2":
        return html.Div([
            dcc.Graph(
                id='fig2-graph',
                figure=get_fig2(),
                style={'height': '100%', 'width': '100%'}
            )
        ], className='figure2')  # Make sure this line is present
    elif pathname == "/fig3":
        return html.Div([
            dbc.Row([
                dbc.Col(dcc.Dropdown(
                    id='fig3-country-dropdown',
                    options=[{'label': 'All', 'value': 'All'}] + [{'label': i, 'value': i} for i in sorted(df['Country Code'].unique())],
                    multi=True,
                    placeholder="Select Countries",
                    value=['All']
                ), width=6),
                dbc.Col(dcc.Dropdown(
                    id='fig3-sport-dropdown',
                    options=[{'label': 'All', 'value': 'All'}] + [{'label': i, 'value': i} for i in sorted(df['Sport Discipline'].unique())],
                    multi=False,
                    placeholder="Select Sport",
                    value='All',
                    clearable=False  # Add this line
                ), width=6),
            ], className="mb-4"),
            html.Div(id='fig3-container', className='figure3')  # Add className here
        ])
    else:
        return "404 Page Not Found"  # Handle undefined routes

# Run the App
if __name__ == "__main__":
    app.run_server(debug=True)
