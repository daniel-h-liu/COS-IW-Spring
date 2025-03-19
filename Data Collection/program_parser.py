import json
from Classes import Concert, Work

concerts = []
works = []


# Create lists of concerts and works
with open("complete.json") as file:
    programs = json.load(file)["programs"]

    for concert in programs:
        c = Concert(concert["id"], concert["season"], concert["concerts"][0], concert["works"])
        concerts.append(c)

        for work in concert["works"]:         
            w = Work(work.get("ID", "unknown_id"), 
                     work.get("composerName", "unknown_composer"), 
                     work.get("workTitle", "unknown_title"), 
                     work.get("conductorName", "unknown_conductor"), 
                     work.get("soloists", []))
            works.append(w)


# Count frequency of composers
composer_freq = {}
for work in works:
    composer_freq[work.composer] = composer_freq.get(work.composer, 0) + 1

print({k: v for k, v in sorted(composer_freq.items(), key=lambda item: item[1])})

# Count frequency of works
work_freq = {}
for work in works:
    try: 
        work_freq[work.title] = work_freq.get(work.title, 0) + 1
    except:
        print("Error hashing title: " + str(work.title))
    

#print({k: v for k, v in sorted(work_freq.items(), key=lambda item: item[1])})

print("Total # of concerts: " + str(len(concerts)))
print("Total # of works: " + str(len(works)))
print("Avg # of works per concert: " + str((len(works) / len(concerts))))