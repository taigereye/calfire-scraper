import argparse
from datetime import datetime
import glob
import os
import re
import subprocess

import utils.constants as C
import utils.classes as I

now = datetime.now().strftime("%Y-%m-%d_%H--%M--%S")

### SCRAPE ###

scraper_runner = I.ScraperRunner(
    run_type=C.MULTIPLE,
    description="Average wildfire data for a range of years"
)
scraper_runner.initialize_args()
scraper_runner.run_all()

regions = [C.NORTHERN_CA_STR, C.SOUTHERN_CA_STR, C.PGE_STR]
totals = {r: {"n_wildfires": 0, "acres_burned": 0} for r in regions}


### EXTRACT ###

for y in scraper_runner.years:
    files = glob.glob(f"data/calfire_{y}_summary_*.md")
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

results_file = "data/calfire_avg_{}.md".format(now)

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
