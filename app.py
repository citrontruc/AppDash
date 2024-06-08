from dash import Dash, html, dcc, ctx, Patch
import dash_bootstrap_components as dbc # Library to add some style to our application.
from dash_bootstrap_templates import load_figure_template
from dash.dependencies import Input, Output
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

from helper.helper import filter_data, generate_colourmap, generate_all_plot

load_figure_template(["minty", "minty_dark"])

# Load the data we are going to use for our analysis
all_songs_df = pd.read_csv("data/all_songs_df.csv", sep=";")
band_df = pd.read_csv("data/group_df.csv", sep=";")
band_df["smallest_date"] = pd.to_datetime(band_df["smallest_date"], dayfirst=True).dt.date
band_df["biggest_date"] = pd.to_datetime(band_df["biggest_date"], dayfirst=True).dt.date
all_songs_df["release_date"] = pd.to_datetime(all_songs_df["release_date"]).dt.date
all_songs_df = all_songs_df.drop_duplicates(subset=["song_title", "band_name"], keep=False)
all_songs_df["year"] =  pd.to_datetime(all_songs_df["release_date"]).dt.year

colourmap = generate_colourmap(band_df, "band_name")
band_df["colour"] = band_df["band_name"].map(colourmap).apply(lambda x : '#%02x%02x%02x' % (int(x[0]), int(x[1]), int(x[2])))
all_songs_df["colour"] = all_songs_df["band_name"].map(colourmap).apply(lambda x : '#%02x%02x%02x' % (int(x[0]), int(x[1]), int(x[2])))

# Define styles we would like to use in order to get a clean app
# Trying you own style is not recommended (use dash.bootstrap_components instead) but is possible.
desc_style = {
    'background': '#FFFFFF',
    'text': '#5473FF'
}

# We define the variables we would like to study. 
list_subplot_titles = ["Number of songs per band", "Number of songs written per year", "Songs with max views"]
fig = make_subplots(rows=2, cols=3, specs=[[{}, {"rowspan" : 2, "colspan" : 2, "type" : "treemap"},  None], [{}, None, None]], subplot_titles = list_subplot_titles)
color_mode_switch =  html.Span(
    [
        dbc.Label(className="fa fa-moon", html_for="color-mode-switch"),
        dbc.Switch( id="color-mode-switch", value=False, className="d-inline-block ms-1", persistence=True),
        dbc.Label(className="fa fa-sun", html_for="color-mode-switch"),
    ]
)

# We define our app layout.
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME])
app.layout = html.Div([
    html.H1("Analysis of the views of song lyrics according to Genius Website", ),
    html.H3(children = 'Band Selection', style={'backgroundColor': desc_style['background'], 'color': desc_style['text']}),
    dcc.Dropdown(id="band-selection", options=band_df["band_name"].unique(), value=["Architects", "STARSET", "Poets of the Fall", "CHVRCHES"], clearable=True, multi=True, placeholder="Select bands (by default, no bands are selected)"),
    color_mode_switch,    
    html.Table([html.Tr([html.Th('Smallest Date |'), html.Th('Biggest Date')]),
                html.Tr([html.Td(id='value-1'),html.Td(id='value-2')])]),
    html.Div(id='filter-display', style={'backgroundColor': desc_style['background'], 'color': desc_style['text'], 'textAlign': 'left'}),
    dcc.Graph(id='graph', figure=fig)],
    style={"textAlign" : "center",'margin': '50px'}
)

# We will make our figures dynamic thanks to callback (clicking the figure applies a filter on the graph)
@app.callback(
    [Output('graph', 'figure'),
    Output('band-selection', 'value'),
    Output('value-1', 'children'),
    Output('value-2', 'children')],
    [Input('graph', 'clickData'),
     Input('band-selection', 'value'),
     Input("color-mode-switch", "value")],
)
def update_graph(clickData, band_name, switch_on):
    template = pio.templates["minty"] if switch_on else pio.templates["minty_dark"]
    patched_figure = Patch()
    patched_figure["layout"]["template"] = template
    # We update our dataframe to get the filters we want.
    # With clickdata, we could recover information from the user clicks
    if ctx.triggered_id == "graph":
        if clickData["points"][0]["curveNumber"] == 0:
            band_name = [clickData["points"][0]["x"]]
        print(clickData)
    filtered_band_df = filter_data(band_df, "band_name", band_name)
    filtered_song_df = filter_data(all_songs_df, "band_name", band_name)

    # Recover value for label at the top
    value1 = filtered_band_df["smallest_date"].min()
    value2 = filtered_band_df["biggest_date"].max()
    #existing_children = [html.P(f"Filters: {' | '.join(band_name)}")]

    # Create our figures
    fig_updated = make_subplots(rows=2, cols=3, specs=[[{}, {"rowspan" : 2, "colspan" : 2},  None], [{}, None, None]], subplot_titles = list_subplot_titles)
    fig1, fig2, fig3 = generate_all_plot(filtered_band_df, filtered_song_df)
    fig_updated.add_trace(fig1, row=1, col=1)
    fig_updated.add_trace(fig2, row=2, col=1)
    for scatter_plots in fig3:
        fig_updated.add_trace(scatter_plots, row=1, col=2)
    fig_updated.update_layout(height=1000, legend_title_text = "Band Names", legend_x=1, legend_y=1, template=template)
    return fig_updated, band_name, value1, value2

if __name__ == '__main__':
    app.run(debug=True)