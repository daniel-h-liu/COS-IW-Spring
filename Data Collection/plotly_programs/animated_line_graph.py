import pandas as pd
import numpy as np
import plotly.graph_objects as go
from dash import Dash, dcc, html, callback, Output, Input
import common

# Import necessary dataframes and get list of composers
concerts, works = common.setup()
uniq_composers = works["composer"].unique()
uniq_composers.sort()
uniq_works = works["title"].unique()
uniq_works.sort()

# Get unique works with their associated composers
uniq_works_df = works[["composer", "title"]].drop_duplicates()
uniq_works_with_composers = sorted(uniq_works_df["composer"].str.cat(uniq_works_df["title"], sep=': ').tolist())

# Group works by their year
works_by_year = works.groupby(works.date.dt.year)
start_year = 1842 # start date of animation, first date of concerts
end_year = 2025

#----------------------------------------------------------------------#
#--------------------------COMPOSER TRENDS-----------------------------#
#----------------------------------------------------------------------#
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

# Return animation figure of total concert programming counts based off of tuning parameter
# year_range = adjust specificity of animation using period of frames
# top_N = number of top composers to display on graph
def create_overall_fig(year_range = 5, top_N = 10, selected_composers = None, markers = False, uniq_conc = False):
    fig_dict = {"data": [], "layout": {}, "frames": []}
    fig_dict["data"] = [go.Scatter(x=[0], y=[0], mode="lines", name=i+1, showlegend=True) for i in range(top_N)]

    # Fill in layout
    years = np.append(np.arange(start_year, end_year, step=year_range), end_year)
    fig_dict["layout"]["xaxis"] = {"range": [start_year, end_year], "title": "Year", "tickvals": years}
    fig_dict["layout"]["yaxis"] = {"range": [0, 6000], "title": "Popularity (Cumulative Times Programmed)"}
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

    composers = uniq_composers if selected_composers==None else selected_composers
    # Make frames
    composer_freq = pd.Series(np.zeros(len(composers)), dtype=int, index=composers) # create composer frequency from zero
    # TODO: simplify this bc years list is not needed since we're generatin data at same time
    composer_trends = {composer: ([], []) for composer in composers}
    for i, year in enumerate(years):
        if i == 0:
            continue

        frame = {"data": [], "name": str(year)}
        for y in range(years[i - 1], year + 1):
            # Loop through all works in this year and update composer
            if y in works_by_year.groups:
                if not uniq_conc:
                    works_by_year.get_group(y)['composer'].apply(update_freq, args=(composer_trends, composer_freq, year))
                else:
                    year_df = works_by_year.get_group(y)
                    # Group by programId, then get unique composers per program
                    composers_in_year = year_df.groupby('programID')['composer'].unique()
                    
                    # Flatten list of unique composers for the whole year
                    unique_composers = pd.Series(np.concatenate(composers_in_year.values))

                    unique_composers.apply(update_freq, args=(composer_trends, composer_freq, year))

    
        # Get top_N composers
        top_composers = composer_freq.nlargest(top_N)

        # Update line data
        frame["data"] = [go.Scatter(x=composer_trends[composer][0], 
                                    y=composer_trends[composer][1],
                                    mode='lines+markers' if markers else 'lines',
                                    name=composer,
                                    showlegend=True)
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

    #fig_dict["layout"]["yaxis"] = {"range": [0, max(100, int(composer_freq.nlargest(1).iloc[0] * 1.1)]), "title": "Popularity (Times Programmed)"}

    return go.Figure(fig_dict)



# Update function for frequency of Kagi chart
def update_kagi_freq(composer, composer_trends, curr_year):
    if composer in composer_trends:
        years, freqs = composer_trends[composer]
        # first entry in trend
        if len(years) == 0:
            years.append(curr_year - 1)
            freqs.append(0)
            years.append(curr_year) # kagi vertical line
            freqs.append(0) # kagi vertical line
            years.append(curr_year)
            freqs.append(1)
        # already added this year
        elif years[-1] == curr_year:
            freqs[-1] += 1
        # add this year for the first time
        else:
            years.append(curr_year)
            freqs.append(freqs[-1])
            years.append(curr_year)
            freqs.append(1)

# Return animation figure of popularity PER YEAR
def create_pop_by_year_fig(year_range = 5, top_N = 10, selected_composers = None, markers = False, uniq_conc = False):
    fig_dict = {"data": [], "layout": {}, "frames": []}
    fig_dict["data"] = [go.Scatter(x=[0], y=[0], mode="lines", name=i, showlegend=True) for i in range(top_N)]

    # Fill in layout
    years = np.append(np.arange(start_year, end_year, step=year_range), end_year)
    fig_dict["layout"]["xaxis"] = {"range": [start_year, end_year], "title": "Year", "tickvals": years}
    fig_dict["layout"]["yaxis"] = {"range": [0, 1000], "title": "Popularity (Times Programmed Per Year)"}
    # Set up play/pause buttons
    fig_dict["layout"]["updatemenus"] = [
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

    composers = uniq_composers if selected_composers==None else selected_composers
    # Make frames
    #composer_freq = pd.Series(np.zeros(len(composers)), dtype=int, index=composers) # create composer frequency from zero
    # TODO: simplify this bc years list is not needed since we're generatin data at same time
    composer_trends = {composer: ([], []) for composer in composers}
    for i, year in enumerate(years):
        if i == 0:
            continue

        frame = {"data": [], "name": str(year)}
        for y in range(years[i - 1], year + 1):
            # Loop through all works in this year and update composer
            if y in works_by_year.groups:
                if not uniq_conc:
                    works_by_year.get_group(y)['composer'].apply(update_kagi_freq, args=(composer_trends, year))
                else:
                    year_df = works_by_year.get_group(y)
                    # Group by programId, then get unique composers per program
                    composers_in_year = year_df.groupby('programID')['composer'].unique()
                    
                    # Flatten list of unique composers for the whole year
                    unique_composers = pd.Series(np.concatenate(composers_in_year.values))

                    unique_composers.apply(update_kagi_freq, args=(composer_trends, year))
    
        # Get top_N composers
        composer_freq = {
            composer: freqs[-1] if len(freqs) > 0 and years[-1] == year else 0
            for composer, (years, freqs) in composer_trends.items()
        }
        top_composers = sorted(composer_freq, key=composer_freq.get, reverse=True)[:top_N]

        # Update line data
        frame["data"] = [go.Scatter(x=composer_trends[composer][0], 
                                    y=composer_trends[composer][1],
                                    mode='lines+markers' if markers else 'lines',
                                    name=composer,
                                    showlegend=True)
                                    for composer in top_composers]

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

    #fig_dict["layout"]["yaxis"] = {"range": [0, max(100, int(composer_freq.nlargest(1).iloc[0] * 1.1)]), "title": "Popularity (Times Programmed)"}

    return go.Figure(fig_dict)


#----------------------------------------------------------------------#
#----------------------------WORK TRENDS-------------------------------#
#----------------------------------------------------------------------#
# Function to update comp_freq with data from specific year_range
def update_work_freq(work_title, work_trends, work_freq, curr_year):
    if work_title in work_trends:
        years, freqs = work_trends[work_title]
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

    if work_title in work_freq:
        work_freq[work_title] += 1

# Return animation figure of total concert programming counts based off of tuning parameter
# year_range = adjust specificity of animation using period of frames
# top_N = number of top composers to display on graph
def create_overall_work_fig(year_range = 5, top_N = 10, selected_works = None, markers = False):
    fig_dict = {"data": [], "layout": {}, "frames": []}
    fig_dict["data"] = [go.Scatter(x=[0], y=[0], mode="lines", name=i, showlegend=True) for i in range(top_N)]

    # Fill in layout
    years = np.append(np.arange(start_year, end_year, step=year_range), end_year)
    fig_dict["layout"]["xaxis"] = {"range": [start_year, end_year], "title": "Year", "tickvals": years}
    fig_dict["layout"]["yaxis"] = {"range": [0, 2000], "title": "Popularity (Cumulative Times Programmed)"}
    # Set up play/pause buttons
    fig_dict["layout"]["updatemenus"] = [
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

    works_list = uniq_works if selected_works==None else selected_works
    # Make frames
    work_freq = pd.Series(np.zeros(len(works_list)), dtype=int, index=works_list) # create work frequency from zero
    # TODO: simplify this bc years list is not needed since we're generating data at same time
    work_trends = {work: ([], []) for work in works_list}
    for i, year in enumerate(years):
        if i == 0:
            continue

        frame = {"data": [], "name": str(year)}
        for y in range(years[i - 1], year + 1):
            # Loop through all works in this year and update composer
            if y in works_by_year.groups:
                works_by_year.get_group(y)['title'].apply(update_work_freq, args=(work_trends, work_freq, year))
    
        # Get top_N composers
        top_works = work_freq.nlargest(top_N)

        # Update line data
        frame["data"] = [go.Scatter(x=work_trends[work][0], 
                                    y=work_trends[work][1],
                                    mode='lines+markers' if markers else 'lines',
                                    name=work + " - " + works[works.title == work].iloc[0]["composer"],
                                    showlegend=True)
                                    for work in top_works.index]

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

    #fig_dict["layout"]["yaxis"] = {"range": [0, max(100, int(composer_freq.nlargest(1).iloc[0] * 1.1)]), "title": "Popularity (Times Programmed)"}

    return go.Figure(fig_dict)

# Update function for frequency of Kagi chart
def update_work_kagi_freq(work, work_trends, curr_year):
    if work in work_trends:
        years, freqs = work_trends[work]
        # first entry in trend
        if len(years) == 0:
            years.append(curr_year - 1)
            freqs.append(0)
            years.append(curr_year) # kagi vertical line
            freqs.append(0) # kagi vertical line
            years.append(curr_year)
            freqs.append(1)
        # already added this year
        elif years[-1] == curr_year:
            freqs[-1] += 1
        # add this year for the first time
        else:
            years.append(curr_year)
            freqs.append(freqs[-1])
            years.append(curr_year)
            freqs.append(1)

# Return animation figure of popularity PER YEAR
def create_work_pop_by_year_fig(year_range = 5, top_N = 10, selected_works = None, markers = False):
    fig_dict = {"data": [], "layout": {}, "frames": []}
    fig_dict["data"] = [go.Scatter(x=[0], y=[0], mode="lines", name=i, showlegend=True) for i in range(top_N)]

    # Fill in layout
    years = np.append(np.arange(start_year, end_year, step=year_range), end_year)
    fig_dict["layout"]["xaxis"] = {"range": [start_year, end_year], "title": "Year", "tickvals": years}
    fig_dict["layout"]["yaxis"] = {"range": [0, 200], "title": "Popularity (Times Programmed Per Year)"}
    # Set up play/pause buttons
    fig_dict["layout"]["updatemenus"] = [
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

    works_list = uniq_works if selected_works==None else selected_works
    # Make frames
    #composer_freq = pd.Series(np.zeros(len(composers)), dtype=int, index=composers) # create composer frequency from zero
    # TODO: simplify this bc years list is not needed since we're generatin data at same time
    work_trends = {work: ([], []) for work in works_list}
    for i, year in enumerate(years):
        if i == 0:
            continue

        frame = {"data": [], "name": str(year)}
        for y in range(years[i - 1], year + 1):
            # Loop through all works in this year and update composer
            if y in works_by_year.groups:
                works_by_year.get_group(y)['title'].apply(update_work_kagi_freq, args=(work_trends, year))
    
        # Get top_N composers
        work_freq = {
            work: freqs[-1] if len(freqs) > 0 and years[-1] == year else 0
            for work, (years, freqs) in work_trends.items()
        }
        top_works = sorted(work_freq, key=work_freq.get, reverse=True)[:top_N]

        # Update line data
        frame["data"] = [go.Scatter(x=work_trends[work][0], 
                                    y=work_trends[work][1],
                                    mode='lines+markers' if markers else 'lines',
                                    name=work + " - " + works[works.title == work].iloc[0]["composer"],
                                    showlegend=True)
                                    for work in top_works]

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

    #fig_dict["layout"]["yaxis"] = {"range": [0, max(100, int(composer_freq.nlargest(1).iloc[0] * 1.1)]), "title": "Popularity (Times Programmed)"}

    return go.Figure(fig_dict)

#----------------------------------------------------------------------#
#----------------------------APP LAYOUT--------------------------------#
#----------------------------------------------------------------------#

app = Dash(suppress_callback_exceptions=True)

app.layout = [
    # Header
    html.H1("Is Mozart Really That Popular?", style={'textAlign':'center'}),
    html.H2("An Analysis of the New York Philharmonic's Performance History and Concert Programming", style={'textAlign':'center'}),
    html.P("Daniel Liu, Princeton University • Appendix Analysis Tool", style={'textAlign':'center'}),
    html.Hr(),
    dcc.Tabs(id='graph-tabs', children=[
        dcc.Tab(label='Home', value='home-tab'),
        dcc.Tab(label='Composer Trends', value='composer-popularity-tab'),
        dcc.Tab(label='Work Trends', value='work-popularity-tab'),
    ]),
    html.Div(id='tab-content'),
    # Separator
    #html.Div(style={'clear': 'both', 'margin-bottom': '5%'}), 

    
]

# Callback function to update tuning parameters of the cumulative graph
@callback(
    output=Output(component_id = 'composer-line-graph', component_property = 'figure'),
    inputs=dict(year_range = Input(component_id='cu-year-range-selector', component_property='value'),
                top_N = Input(component_id='cu-top-N-selector', component_property='value'),
                composers = Input(component_id='cu-composers-selector', component_property='value'),
                markers = Input(component_id='cu-markers-selector', component_property='value'))
)
def update_cu_composer_graph(year_range, top_N, composers, markers):
    marker = False if markers == None or 'Markers?' not in markers else True
    uniq = False if markers == None or 'Unique Per Concert?' not in markers else True
    if composers == None:
        return create_overall_fig(year_range, top_N, markers=marker, uniq_conc=uniq)
    else:
        return create_overall_fig(year_range, top_N=len(composers), selected_composers=composers, markers=marker, uniq_conc=uniq)

# Callback function to update tuning parameters of the kagi graph
@callback(
    output=Output(component_id = 'composer-kagi-graph', component_property = 'figure'),
    inputs=dict(year_range = Input(component_id='kagi-year-range-selector', component_property='value'),
                top_N = Input(component_id='kagi-top-N-selector', component_property='value'),
                composers = Input(component_id='kagi-composers-selector', component_property='value'),
                markers = Input(component_id='kagi-markers-selector', component_property='value'))
)
def update_kagi_composer_graph(year_range, top_N, composers, markers):
    marker = False if markers == None or 'Markers?' not in markers else True
    uniq = False if markers == None or 'Unique Per Concert?' not in markers else True
    if composers == None:
        return create_pop_by_year_fig(year_range, top_N, markers=marker, uniq_conc=uniq)
    else:
        return create_pop_by_year_fig(year_range, top_N=len(composers), selected_composers=composers, markers=marker, uniq_conc=uniq)

# Callback function to update tuning parameters of the cumulative work graph
@callback(
    output=Output(component_id = 'work-line-graph', component_property = 'figure'),
    inputs=dict(year_range = Input(component_id='cu-work-year-range-selector', component_property='value'),
                top_N = Input(component_id='cu-work-top-N-selector', component_property='value'),
                works = Input(component_id='cu-works-selector', component_property='value'),
                markers = Input(component_id='cu-works-markers-selector', component_property='value'))
)
def update_cu_composer_graph(year_range, top_N, works, markers):
    if works == None:
        return create_overall_work_fig(year_range, top_N, markers=False if markers == None else True)
    else:
        return create_overall_work_fig(year_range, top_N=len(works), selected_works=works, markers=False if markers == None else True)

# Callback function to update tuning parameters of the kagi work graph
@callback(
    output=Output(component_id = 'work-kagi-graph', component_property = 'figure'),
    inputs=dict(year_range = Input(component_id='work-kagi-year-range-selector', component_property='value'),
                top_N = Input(component_id='work-kagi-top-N-selector', component_property='value'),
                works = Input(component_id='kagi-works-selector', component_property='value'),
                markers = Input(component_id='work-kagi-markers-selector', component_property='value'))
)
def update_kagi_composer_graph(year_range, top_N, works, markers):
    if works == None:
        return create_work_pop_by_year_fig(year_range, top_N, markers=False if markers == None else True)
    else:
        return create_work_pop_by_year_fig(year_range, top_N=len(works), selected_works=works, markers=False if markers == None else True)


# Callback function for rendering various tabs
@callback(Output('tab-content', 'children'), 
          Input('graph-tabs', 'value'))
def render_tab(tab):
    if tab == 'home-tab':
        return [dcc.Markdown('''
            ### About This Tool
            **Purpose:** Analyze almost 200 years of concert programming trends (1842-present) at America's oldest symphony orchestra.  
            **Goals:**  
            - Track 1,200+ composers' performance frequency 
            - Track repertoire diversity across historical eras
            - Identify cultural movement correlations  
            - Export data for academic research
            
            *Data Source:* [NY Philharmonic Archives](https://archives.nyphil.org)  
            *Data current as of February 2025. Fully up-to-date data can be found [here](https://github.com/nyphilarchive/PerformanceHistory?tab=readme-ov-file)*
            ''', style={'margin': '5%'}),
            
            dcc.Markdown('''
            ### How to Use
            1. **Adjust Timeframe**  
            Use the year slider to select any period between 1842-2025. Depending on the desired
            specificity of the timeframe, play around with "Years Between Each Tick".
            2. **Set Scope of Analysis**  
            Choose top 5, 10, 15, 20 composers or filter specific names. The latter offers
            the most flexibility and customizability, especially when performing case studies. 
            3. **Visualize Patterns**  
            Hover over markers for details or zoom in on datum easily by dragging out a box on the plot.  
            Double click to reset the plot to the original view.
                * Plotly does not currently support dynamic labels for the legend. To see the labels for a specific frame, click on the legend to update it.
            4. **To Unique Concert or Not Unique Concert?**  
            The toggle for "Unique per Concert?" refers to the fact that sometimes composers are featured multiple times
            per concert in the data, either due to movements of a single piece being counted separately, or other
            issues of overcounting that is caused by the way the database was chosen to be represented by
            the original creator. Checking this box will ensure that composers are counted ONLY ONCE per
            program/concert, yielding significantly different results in frequency. Users should use
            this option however it aligns with their research interests.
            5. **Export Results**  
            Download plots as pngs by clicking the camera icon in the top right corner of each graph.
                         
            
            ''', style={'margin': '5%'}),

            dcc.Markdown('''
            Tool developed by Daniel Liu using Python Pandas, Plotly, and Dash. ChatGPT was used sporadically to help with implementing parts of the code.
            ''', style={'margin': '5%'})
        ]
    elif tab == 'composer-popularity-tab':
        return html.Div([
            html.H2(children='Composer Popularity Over Time', style={'textAlign':'center'}),
            html.Div(dcc.Graph(figure=create_overall_fig(), id='composer-line-graph', style={'textAlign':'center'})),
            html.Div([ # year_range and top_N tuners
                html.Div([html.Label("Years Between Each Tick", htmlFor='cu-year-range-selector'),
                        dcc.Dropdown(options=[1,5,10,25], value=5, id='cu-year-range-selector')]),
                html.Div([html.Label("Number of Top Composers", htmlFor='cu-top-N-selector'),
                        dcc.Dropdown(options=[5,10,15,20], value=10, id='cu-top-N-selector')], style={'padding-top': 25}),
            ], style={'width': '45%', 'float': 'right', 'display': 'inline-block'}),
            html.Div([ # composer filter and marker selector
                html.Div([html.Label("Filter by composer", htmlFor='cu-composers-selector'),
                        dcc.Dropdown(options=uniq_composers, id='cu-composers-selector', multi=True)]),
                html.Div(dcc.Checklist(['Markers?', 'Unique Per Concert?'], id='cu-markers-selector'), style={'padding-top': 25}),
            ], style={'width': '45%', 'float': 'left', 'display': 'inline-block'}),

            # Separator
            html.Div(style={'clear': 'both', 'margin-bottom': '10%'}),
            html.Hr(),

            # Kagi chart graph
            html.H2(children='Composer Popularity Per Year', style={'textAlign':'center'}),
            html.Div([dcc.Graph(figure=create_pop_by_year_fig(), id='composer-kagi-graph')]),
            html.Div([ # year_range and top_N tuners
                html.Div([html.Label("Years Between Each Tick", htmlFor='kagi-year-range-selector'),
                        dcc.Dropdown(options=[1,5,10,25], value=5, id='kagi-year-range-selector')]),
                html.Div([html.Label("Number of Top Composers", htmlFor='kagi-top-N-selector'),
                        dcc.Dropdown(options=[5,10,15,20], value=10, id='kagi-top-N-selector')], style={'padding-top': 25}),
            ], style={'width': '45%', 'float': 'right', 'display': 'inline-block'}),
            html.Div([ # composer filter and marker selector
                html.Div([html.Label("Filter by composer", htmlFor='kagi-composers-selector'),
                        dcc.Dropdown(options=uniq_composers, id='kagi-composers-selector', multi=True)]),
                html.Div(dcc.Checklist(['Markers?', 'Unique Per Concert?'], id='kagi-markers-selector'), style={'padding-top': 25})
            ], style={'width': '45%', 'float': 'left', 'display': 'inline-block'})])
    elif tab == 'work-popularity-tab':
        return html.Div([
            html.H2(children='Work Popularity Over Time', style={'textAlign':'center'}),
            html.Div(dcc.Graph(figure=create_overall_work_fig(), id='work-line-graph', style={'textAlign':'center'})),

            html.Div([ # year_range and top_N tuners
                html.Div([html.Label("Years Between Each Tick", htmlFor='cu-work-year-range-selector'),
                        dcc.Dropdown(options=[1,5,10,25], value=5, id='cu-work-year-range-selector')]),
                html.Div([html.Label("Number of Top Works", htmlFor='cu-work-top-N-selector'),
                        dcc.Dropdown(options=[5,10,15,20], value=10, id='cu-work-top-N-selector')], style={'padding-top': 25}),
            ], style={'width': '45%', 'float': 'right', 'display': 'inline-block'}),
            html.Div([ # composer filter and marker selector
                html.Div([html.Label("Filter by work", htmlFor='cu-works-selector'),
                        dcc.Dropdown(options=uniq_works_with_composers, id='cu-works-selector', multi=True)]),
                html.Div(dcc.Checklist(['Markers?'], id='cu-works-markers-selector'), style={'padding-top': 25})
            ], style={'width': '45%', 'float': 'left', 'display': 'inline-block'}),

            # Separator
            html.Div(style={'clear': 'both', 'margin-bottom': '10%'}),
            html.Hr(),

            # Kagi chart graph
            html.H2(children='Work Popularity Per Year', style={'textAlign':'center'}),
            html.Div([dcc.Graph(figure=create_work_pop_by_year_fig(), id='work-kagi-graph')]),
            html.Div([ # year_range and top_N tuners
                html.Div([html.Label("Years Between Each Tick", htmlFor='work-kagi-year-range-selector'),
                        dcc.Dropdown(options=[1,5,10,25], value=5, id='work-kagi-year-range-selector')]),
                html.Div([html.Label("Number of Top Composers", htmlFor='work-kagi-top-N-selector'),
                        dcc.Dropdown(options=[5,10,15,20], value=10, id='work-kagi-top-N-selector')], style={'padding-top': 25}),
            ], style={'width': '45%', 'float': 'right', 'display': 'inline-block'}),
            html.Div([ # composer filter and marker selector
                html.Div([html.Label("Filter by work", htmlFor='kagi-works-selector'),
                        dcc.Dropdown(options=uniq_works_with_composers, id='kagi-works-selector', multi=True)]),
                html.Div(dcc.Checklist(['Markers?'], id='work-kagi-markers-selector'), style={'padding-top': 25})
            ], style={'width': '45%', 'float': 'left', 'display': 'inline-block'})
        ])







if __name__ == '__main__':
    app.run(debug=True)