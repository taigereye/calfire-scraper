import argparse
from datetime import datetime
import glob
import os
import re
import subprocess

import constants as C

now = datetime.now().strftime("%Y-%m-%d_%H--%M--%S")

parser = argparse.ArgumentParser(description="Simple tests to see if data scraped correctly")

parser.add_argument("-y", nargs='+', help="Average exactly which year values are provided")
parser.add_argument("-yr", nargs=2, help="Average all years between and including 2 year values")
args = parser.parse_args()

# Which years to run scraper for
if args.y:
    years = args.y
else:
    years = range(args.yr[0], args.yr[1])
n_years = len(years)

regions = [C.NORTHERN_CA_STR, C.SOUTHERN_CA_STR, C.PGE_STR]
totals = {r: {"n_wildfires": 0, "acres_burned": 0} for r in regions}

for y in years:
    ### SCRAPE ###
    subprocess.run(["python", "scraper.py", "-y", str(y)])

    ### EXTRACT ###
    files = glob.glob(f"calfire_{y}_summary_*.md")
    filename = max(files, key=os.path.getmtime)

    print("Extracting totals from {}...\n\n".format(y))

    with open(filename, 'r') as file:
        contents = file.read()
        for r in regions:
            fires_match = re.search(fr"### {r}:\nTotal fires: (\d+)", contents)
            acres_match = re.search(fr"{r}:\nTotal fires: \d+\nTotal acres burned: (\d+)", contents)
            if fires_match and acres_match:
                totals[r]["n_wildfires"] += int(fires_match.group(1))
                totals[r]["acres_burned"] += int(acres_match.group(1))

### FINAL RESULTS ###

print("Writing results to markdown file...\n\n")

results_file = "calfire_avg_{}.md".format(now)

title = "# California Wildfire Statistics (Averaged): {}\n\n".format(now)
subtitle = "Years: {}\n\n".format(', '.join(years))
results = '\n'.join([
    "### {}:".format(C.NORTHERN_CA_STR),
    "Avg fires: {}".format(totals[C.NORTHERN_CA_STR]["n_wildfires"] / n_years),
    "Avg acres burned: {}\n".format(totals[C.NORTHERN_CA_STR]["acres_burned"] / n_years),
    "### {}:".format(C.SOUTHERN_CA_STR),
    "Avg fires: {}".format(totals[C.SOUTHERN_CA_STR]["n_wildfires"] / n_years),
    "Avg acres burned: {}\n".format(totals[C.SOUTHERN_CA_STR]["acres_burned"] / n_years),
    "### {}:".format(C.PGE_STR),
    "Avg fires: {}".format(totals[C.PGE_STR]["n_wildfires"] / n_years),
    "Avg acres burned: {}\n".format(totals[C.PGE_STR]["acres_burned"] / n_years)
])

file = open(results_file, 'w')
file.write(results)
file.close()

print("Done.\n")
