import pandas as pd
import numpy as np
import plotly.graph_objects as go
from dash import Dash, dcc, html, callback, Output, Input
import common

# Import necessary dataframes
concerts, works = common.setup()
uniq_composers = works["composer"].unique()

# Group works by their year
works_by_year = works.groupby(works.date.dt.year)
start_year = 1842 # start date of animation, first date of concerts
end_year = 2025

# Function to update comp_freq with data from specific year_range
def update_freq(composer, composer_trends, composer_freq, curr_year):
    if composer in composer_trends:
        years, freqs = composer_trends[composer]
        # first entry in trend
        if len(years) == 0:
            years.append(curr_year - 1)
            freqs.append(0)
            years.append(curr_year)
            freqs.append(1)
        # already added this year
        elif years[-1] == curr_year:
            freqs[-1] += 1
        # add this year for the first time
        else:
            years.append(curr_year)
            freqs.append(freqs[-1] + 1)

    if composer in composer_freq:
        composer_freq[composer] += 1

# Return animation figure based off of tuning parameter
# year_range = adjust specificity of animation using period of frames
# top_N = number of top composers to display on graph
def create_animation_fig(year_range = 5, top_N = 10):
    fig_dict = {"data": [], "layout": {}, "frames": []}
    fig_dict["data"] = [go.Scatter(x=[], y=[], mode="lines", name="placeholder") for i in range(top_N)]

    # Fill in layout
    num_frames = (end_year - start_year) // year_range
    years = np.append(np.arange(start_year, end_year, step=year_range), end_year)
    fig_dict["layout"]["xaxis"] = {"range": [start_year, end_year], "title": "Year", "tickvals": years}
    fig_dict["layout"]["yaxis"] = {"range": [0, 5500], "title": "Popularity (Times Programmed)"}
    # Set up play/pause buttons
    fig_dict["layout"]["updatemenus"]= [
        {
            "buttons": [
                {
                    "args": [None, {"frame": {"duration": 500, "redraw": False},
                                    "fromcurrent": True, "transition": {"duration": 300,
                                                                        "easing": "quadratic-in-out"}}],
                    "label": "Play",
                    "method": "animate"
                },
                {
                    "args": [[None], {"frame": {"duration": 0, "redraw": False},
                                    "mode": "immediate",
                                    "transition": {"duration": 0}}],
                    "label": "Pause",
                    "method": "animate"
                }
            ],
            "direction": "left",
            "pad": {"r": 10, "t": 87},
            "showactive": True,
            "type": "buttons",
            "x": 0.1,
            "xanchor": "right",
            "y": 0,
            "yanchor": "top"
        }
    ]
    # Slider for year
    sliders_dict = {
        "active": 0,
        "yanchor": "top",
        "xanchor": "left",
        "currentvalue": {
            "font": {"size": 20},
            "prefix": "Year:",
            "visible": True,
            "xanchor": "right"
        },
        "transition": {"duration": 300, "easing": "cubic-in-out"},
        "pad": {"b": 10, "t": 50},
        "len": 0.9,
        "x": 0.1,
        "y": 0,
        "steps": []
    }

    # Make frames
    composer_freq = pd.Series(np.zeros(len(uniq_composers)), index=uniq_composers) # create composer frequency from zero
    # TODO: simplify this bc years list is not needed since we're generatin data at same time
    composer_trends = {composer: ([], []) for composer in uniq_composers}
    for year in years:
        frame = {"data": [], "name": str(year)}
        for y in range(year, min(year + year_range, end_year + 1)):
            # Loop through all works in this year and update composer
            if y in works_by_year.groups:
                works_by_year.get_group(y)['composer'].apply(update_freq, args=(composer_trends, composer_freq, year))
    
        # Get top_N composers
        top_composers = composer_freq.nlargest(top_N)

        # Update line data
        frame["data"] = [go.Scatter(x=composer_trends[composer][0], 
                                    y=composer_trends[composer][1],
                                    mode='lines',
                                    name=composer)
                                    for composer in top_composers.index]

        fig_dict["frames"].append(frame)

        # Update step association for slider
        slider_step = {"args": [
                [year],
                {"frame": {"duration": 300, "redraw": False},
                "mode": "immediate",
                "transition": {"duration": 300}}
            ],
            "label": str(year),
            "method": "animate"}
        sliders_dict["steps"].append(slider_step)

    # Update slider info
    fig_dict["layout"]["sliders"] = [sliders_dict]

    return go.Figure(fig_dict)


app = Dash()

app.layout = [
    html.H1(children='Composer Popularity Over Time', style={'textAlign':'center'}),
    html.Div([dcc.Graph(figure=create_animation_fig(), id='line-graph')]),
    html.Div([html.Label("Number of Top Composers"),
              dcc.Dropdown(options=[5,10,15,20], value=10, id='top-N-selector')]),
]

@callback(
    Output('line-graph', 'figure'),
    Input('top-N-selector','value')
)
def update_topN(value):
    return create_animation_fig(top_N=value)


if __name__ == '__main__':
    app.run(debug=True)