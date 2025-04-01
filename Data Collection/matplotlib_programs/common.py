import pandas as pd

# CONSTANTS
DF_FILE_LOC_MPL = "../dataframes/"
DF_FILE_LOC = "./dataframes/"

# Normalize title if it is a dictionary
def normalize_title(title):
    if isinstance(title, dict):
        return title.get("em", "") + " " + title.get("_", "")
    else:
        return title
    
# MAIN SETUP FUNCTION
def setup():
    # Unpickle dataframes
    concerts = pd.read_pickle(DF_FILE_LOC_MPL + "concerts.pkl")
    works = pd.read_pickle(DF_FILE_LOC_MPL + "works.pkl")

    # Clean works df
    works = works.query('id != "0*"') # remove all entries that are intermissions

    works['n_title'] = works['title'].apply(normalize_title)

    ## Add Date column to concerts and works
    # extract date from concert-info dictionary as new column
    concerts['date'] = concerts['concerts'].apply(lambda x : x[0].get('Date', None))
    # Convert extracted date to ISO8601, UTC datetime format
    concerts['date'] = pd.to_datetime(concerts['date'], utc=True)
    # Merge works with the datetime column
    works = works.merge(concerts[['programID', 'date']], on='programID', how='left')

    return concerts, works