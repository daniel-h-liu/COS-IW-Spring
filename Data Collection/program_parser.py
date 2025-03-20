import json
import pandas as pd
from Classes import Concert, Work
from common import *

concerts = []
works = []


# Create lists of concerts and works
with open("complete.json") as file:
    programs = json.load(file)["programs"]

    #normalized_programs_df = pd.json_normalize(programs)
    #print(list(normalized_programs_df))

    for concert in programs:
        c = Concert(concert["id"], concert["programID"], concert["orchestra"], concert["season"], concert["concerts"], concert["works"])
        concerts.append(c)

        for work in concert["works"]:         
            w = Work(work.get("ID", "unknown_id"), 
                     work.get("composerName", "Unknown,"), 
                     work.get("workTitle", "unknown_title"),
                     work.get("movement", ""),
                     work.get("conductorName", "Not conducted"), 
                     work.get("soloists", []))
            works.append(w)

# Convert to Pandas Dataframe
concerts_df = pd.DataFrame([vars(c) for c in concerts])
works_df = pd.DataFrame([vars(w) for w in works])

concerts_df.to_pickle(DF_FILE_LOC + "concerts.pkl")
works_df.to_pickle(DF_FILE_LOC + "works.pkl")
print("Concerts + works parsed and saved to pickles.")