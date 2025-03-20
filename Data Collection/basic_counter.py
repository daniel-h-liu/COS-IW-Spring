import pandas as pd
import numpy as np
from common import *

# Unpickle dataframes
concerts = pd.read_pickle(DF_FILE_LOC + "concerts.pkl")
works = pd.read_pickle(DF_FILE_LOC + "works.pkl")

# Clean works df
works = works.query('id != "0*"') # remove all entries that are intermissions

# Count frequency of composers
composer_freq = works["composer"].value_counts()
print(composer_freq)

# Count frequency of works
work_freq = works["title"].value_counts()
print(work_freq)


# work_freq = {}
# for work in works:
#     try: 
#         work_freq[work.title] = work_freq.get(work.title, 0) + 1
#     except:
#         continue
#        # print("Error hashing title: " + str(work.title))
    

#print({k: v for k, v in sorted(work_freq.items(), key=lambda item: item[1])})

print("Total # of concerts: " + str(len(concerts)))
print("Total # of works: " + str(len(works)))
print("Avg # of works per concert: " + str((len(works) / len(concerts))))