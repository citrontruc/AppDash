from colorsys import hls_to_rgb
import pandas as pd
from plotly.colors import n_colors
import plotly.graph_objects as go
import seaborn as sns

def filter_data(pandas_df, column_filter, value_keep):
    """
    Filters a dataframe depending on a column on which to apply a filter and the values to keep
    
    Input:
        pandas_df (pandas dataframe): a dataframe to filter \n
        column_filter (dict): The name of the column to apply a filter on \n
        value_keep (str): A list of values to keep \n
    
    Output:
        (pandas dataframe) : A filtered dataframe \n
    """
    if value_keep == []:
        return pandas_df
    return pandas_df.loc[pandas_df[column_filter].isin(value_keep)]

def generate_colourmap(pandas_df, interest_column):
    """
    Generates a colourmap with an unique colour for each of the values in the column interest_column

    Input:
        Pandas_df (pandas dataframe): the dataframe with the values
        interest_column (str): column on which to filter
    
    Output:
        (dict)
    """
    interest_list = pandas_df[interest_column].unique()
    colourscale_hls = sns.color_palette("husl", len(interest_list))
    colourscale = []
    for element in colourscale_hls:
        colourscale.append(tuple([value * 255 for value in hls_to_rgb(*element)]))
    colourmap = {col_val : colour for col_val, colour in zip(interest_list, colourscale)}
    return colourmap

def generate_all_plot(pandas_band_df, pandas_song_df):
    """
    Method to generate all our figures. Your dataset needs to contain the following columns

    Input:
        pandas_band_df (pandas dataframe)
        pandas_song_df (pandas dataframe)
    Output:
        (plotly graph_object)
        (plotly graph_object)
        (list of plotly graph_objects)
    """
    # Sort values to keeo only the biggest ones
    song_count = pandas_band_df.sort_values("song_title", ascending=False).head(10)[["band_name", "song_title", "colour"]]
    most_popular_song = pandas_song_df.sort_values("lyrics_view", ascending=False).head(10)[["song_title", "lyrics_view", "band_name", "colour"]]
    song_count_df = pandas_song_df.groupby(["band_name", "year", "colour"])["song_title"].count().reset_index()
    
    # We generate our bar plots
    song_count_bar = go.Bar(x=song_count["band_name"], y=song_count["song_title"], marker={"color" : song_count["colour"]}, showlegend=False, text=song_count["song_title"],
                            hovertemplate='<b>Band</b>: %{customdata[0]}<br>' +
                                      '<b>Number of songs written</b>: %{customdata[1]}<br>',
                                      customdata=[(song_count[["band_name"]].iloc[i], song_count[["song_title"]].iloc[i]) for i in range(len(song_count))])
    most_popular_song_bar = go.Bar(x=most_popular_song["song_title"], y=most_popular_song["lyrics_view"], marker={"color" : most_popular_song["colour"]}, showlegend=False, text="",
                                   hovertemplate='<b>Band</b>: %{customdata[0]}<br>' +
                                      '<b>Song title</b>: %{customdata[1]}<br>' +
                                      '<b>Number of views</b>: %{customdata[2]}<br>',
                                      customdata=[(most_popular_song[["band_name"]].iloc[i], most_popular_song[["song_title"]].iloc[i], most_popular_song[["lyrics_view"]].iloc[i]) for i in range(len(most_popular_song))])

    # We need to generate a list of scatter plots which will then be added to our subplot
    list_scatter_plot = []
    for unique_band in song_count_df["band_name"].unique():
        one_band_df = song_count_df.loc[song_count_df["band_name"] == unique_band]
        year_list = one_band_df["year"].to_list()
        year_list = [int(element) for element in year_list]
        num_song_list = one_band_df["song_title"].to_list()
        year_to_include = [i for i in range(min(year_list), max(year_list)+1)]
        num_song_per_year_list = []
        for unique_year in year_to_include:
            if unique_year in year_list:
                num_song_per_year_list.append(num_song_list[year_list.index(unique_year)])
            else:
                num_song_per_year_list.append(0)
        list_scatter_plot.append(go.Scatter(x=year_to_include, y=num_song_per_year_list, mode="lines", marker={"color" : one_band_df["colour"].iloc[0]}, showlegend=False))
    return song_count_bar, most_popular_song_bar, list_scatter_plot
