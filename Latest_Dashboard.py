import dash
from dash import Dash, html, dcc, Input, Output
import pandas as pd
import plotly.express as px

# Load your data
cleaned_covid_data1 = pd.read_csv(r"Downloads\cleaned_covid_data1.csv")
worldometer_data1 = pd.read_csv(r"Downloads\worldometer_data1.csv")
covid_19_clean_complete1 = pd.read_csv(r"Downloads\covid_19_clean_complete1.csv")

covid_19_clean_complete1['Date'] = pd.to_datetime(covid_19_clean_complete1['Date'])
data_grouped = covid_19_clean_complete1.groupby(['Date', 'Country', 'Lat', 'Long', 'WHO Region'], as_index=False).sum()

# Scatter Geo Plot (Map)
map_figure = px.scatter_geo(
    data_grouped,
    lat="Lat",
    lon="Long",
    size="Confirmed",
    color="WHO Region",
    hover_name="Country",
    animation_frame=data_grouped['Date'].dt.strftime('%Y-%m-%d'),
    title="COVID-19 Spread Over Time",
    template="plotly",
    projection="natural earth",
    size_max=50
)

# Pie Chart
pie_chart = px.pie(
    worldometer_data1,
    names='Continent',
    values='TotalCases',
    title="COVID-19 Cases % by Continent"
)

sunburst_chart = px.sunburst(
    worldometer_data1,
    path=["Continent", "Country"],
    values="TotalCases",
    color="TotalCases",
    title="COVID-19 Cases Distribution by Continent and Country",
    color_continuous_scale="Reds"
)


# Dash App
app = Dash()

# Layout
app.layout = html.Div(
    children=[
        # Header Section
        html.Div(
            children=[
                html.H1(
                    "Covid-19 Dashboard",
                    style={"textAlign": "center", "fontWeight": "bold", "padding": "20px"}
                ),
                html.H2(
                    "COVID-19 Spread Time-Series Map",
                    style={"textAlign": "center", "color": "#555"}
                ),
                html.P(
                    "An animated visualization of COVID-19 cases spreading over time.",
                    style={"textAlign": "center", "color": "#777"}
                ),
            ],
            style={"backgroundColor": "#f8f9fa", "padding": "20px", "borderRadius": "8px", "marginBottom": "20px"}
        ),

        # Map Section
        html.Div(
            children=[
                dcc.Graph(figure=map_figure)
            ],
            style={
                "backgroundColor": "#fff",
                "padding": "20px",
                "borderRadius": "8px",
                "boxShadow": "0 4px 6px rgba(0, 0, 0, 0.1)",
                "marginBottom": "20px"
            }
        ),

        # Main Content Section (Pie Chart and Bar Chart Side by Side)
        html.Div(
            children=[
                # Left Column (Pie Chart)
                html.Div(
                    children=[
                        dcc.Graph(figure=pie_chart),
                        dcc.Graph(figure=sunburst_chart),
                    ],
                    style={
                        "flex": "1",
                        "backgroundColor": "#fff",
                        "padding": "20px",
                        "borderRadius": "8px",
                        "boxShadow": "0 4px 6px rgba(0, 0, 0, 0.1)",
                        "margin": "10px"
                    }
                ),
               
                # Right Column (Bar Chart with Dropdown)
                html.Div(
                    children=[
                        html.Div(
                            children=[
                                html.Label(
                                    "Choose a Country to view its data",
                                    style={"fontWeight": "bold", "marginBottom": "10px"}
                                ),
                                dcc.Dropdown(
                                    id="country-dropdown",
                                    options=[
                                        {"label": country, "value": country}
                                        for country in sorted(worldometer_data1["Country"].unique())
                                    ],
                                    value="Egypt",
                                    placeholder="Select a Country",
                                    style={"width": "100%", "marginBottom": "20px"}
                                )
                            ],
                            style={"paddingBottom": "10px"}
                        ),
                        dcc.Graph(id="country-graph"),
                        dcc.Graph(id="country-line-graph"),
                    ],
                    style={
                        "flex": "1",
                        "backgroundColor": "#fff",
                        "padding": "20px",
                        "borderRadius": "8px",
                        "boxShadow": "0 4px 6px rgba(0, 0, 0, 0.1)",
                        "margin": "10px"
                    }
                ),
            ],
            style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-between"}
        ),
       
    
    ]
    
)

# Callback
@app.callback(
    [Output("country-graph", "figure"),  
     Output("country-line-graph", "figure")],
    [Input("country-dropdown", "value")]
)
def update_graph(selected_country):
    # Bar Chart
    filtered_data = worldometer_data1[worldometer_data1["Country"] == selected_country]
    metrics = {
        "Total Cases": filtered_data["TotalCases"].values[0] if not filtered_data.empty else 0,
        "Total Deaths": filtered_data["TotalDeaths"].values[0] if not filtered_data.empty else 0,
        "Total Recovered": filtered_data["TotalRecovered"].values[0] if not filtered_data.empty else 0,
        "Active Cases": filtered_data["ActiveCases"].values[0] if not filtered_data.empty else 0,
    }
    bar_fig = px.bar(
        x=list(metrics.keys()),
        y=list(metrics.values()),
        labels={"x": "Metrics", "y": "Count"},
        title=f"COVID-19 Data in {selected_country}"
    )

    # Line Chart
    line_fig = px.line(
        covid_19_clean_complete1[covid_19_clean_complete1["Country"] == selected_country],
        x="Date",
        y=["Confirmed", "Deaths", "Recovered"],
        labels={"value": "Count", "variable": "Metric"},
        title=f"COVID-19 Trends in {selected_country}"
    )
    
    return bar_fig, line_fig

if __name__ == "__main__":
    app.run(debug=True) 