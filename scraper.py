import argparse
from collections import defaultdict
from datetime import datetime
import json
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import constants as C

### INITIALIZE ###

now = datetime.now().strftime("%Y-%m-%d_%H--%M--%S")

parser = argparse.ArgumentParser(description="Web scraper for stats on California wildfire season")

parser.add_argument("-y", required=True, help="year of fire season in YYYY form")
parser.add_argument("-r", action='store_true', help="also save raw data in a separate file")
args = parser.parse_args()
year = args.y

print("\n")

# # Headless browser to improve load time
# browser_options = Options()
# browser_options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})

# Spin up browser to scrape + interact with webpage
url = "https://fire.ca.gov/incidents/{}".format(year)
driver = webdriver.Firefox()
driver.set_page_load_timeout(30)
driver.get(url)

### SCRAPE ###

print("Scraping CalFire...\n\n")

while True:
    try:
        driver.find_element(By.TAG_NAME, 'body')
    except NoSuchElementException:
        print("Page failed to load.")

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Write the contents of soup to a file
    with open("soup.html", "w") as file:
        file.write(str(soup))

    # Desired results
    topline_summary_stats = []

    # Summary statistics
    #   Collect elements
    stat_selector = ".factoid__data.fw-bold.display-5"
    label_selector = ".factoid__label"
    stat_elements = soup.select(stat_selector)
    label_elements = soup.select(label_selector)
    #   Create data struct
    for (s, l) in zip(stat_elements, label_elements):
        topline_summary_stats.append({
            "label": l.text.split(":")[0].strip(),
            "value": s.text.strip()
        })

    # Wildfires by county
    #   Collect outer elements
    row_selector = "#incidents tbody tr"
    row_elements = soup.select(row_selector)
    #   Create data struct
    all_wildfires = []
    for r in row_elements:
        property_elements = r.select('td')
        # Counties
        counties = property_elements[0].text.strip()
        # Date started
        started = property_elements[1].text.strip()
        # Acres burned
        acres = property_elements[2].text.strip().replace(',', '')
        if "External Incident Link" in acres or len(acres) == 0:
            continue
        # Containment
        containment = property_elements[3].text.strip()
        wildfire = {
            "counties": counties.split(", "),
            "started_date": datetime.strptime(started, "%m/%d/%Y").date(),
            "acres_burned": int(acres),
            "containment": int(containment.replace('%', ''))
        }
        all_wildfires.append(wildfire)

    # Find the "Next" button and click it, or end the loop if there's no button
    try:
        
        next_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'next-button')))
        next_button.click()
    except:
        break

# Close browser
driver.quit()

    
### ENRICH ###

print("Calculating additional statistics...\n\n")

for wildfire in all_wildfires:
    wildfire["is_northern"] = wildfire["counties"][0] in C.NORTHERN_CA_COUNTIES
    wildfire["is_pge"] = wildfire["counties"][0] in C.PGE_SERVICE_COUNTIES

# Number of wildfires per county
wildfires_per_county = [{"county": c, "n_wildfires": 0} for c in C.ALL_COUNTIES]
for wildfire in all_wildfires:
    for c in wildfire["counties"]:
        if c in C.ALL_COUNTIES:
            wildfires_per_county[C.ALL_COUNTIES.index(c)]["n_wildfires"] += 1
        else:
            continue

# Totals for Northern and Southern CA vs PG&E service area
template = {
    "northern_ca": 0,
    "southern_ca": 0,
    "pge_area": 0
}
acres_burned_by_region = template.copy()
n_wildfires_by_region = template.copy()

for wildfire in all_wildfires:
    if wildfire["is_northern"]:
        n_wildfires_by_region["northern_ca"] += 1
        acres_burned_by_region["northern_ca"] += wildfire["acres_burned"]
    else:
        n_wildfires_by_region["southern_ca"] += 1
        acres_burned_by_region["southern_ca"] += wildfire["acres_burned"]
    if wildfire["is_pge"]:
        n_wildfires_by_region["pge_area"] += 1
        acres_burned_by_region["pge_area"] += wildfire["acres_burned"]

    
### WRITE RAW DATA ###

if args.r:
    print("Writing raw data to text file...\n\n")

    raw_file = "calfire_{}_raw_data_{}.txt".format(year, now)

    data_to_format = [
        topline_summary_stats,
        wildfires_per_county,
        n_wildfires_by_region,
        acres_burned_by_region
    ]
    data = "\n\n".join(
        [json.dumps(d, indent=4) for d in data_to_format]
    )

    file = open(raw_file, "w")
    file.write(data)
    file.close()


### WRITE RESULTS ###

print("Writing results to markdown file...\n\n")

results_file = "calfire_{}_summary_{}.md".format(year, now)

title = "# {} California Wildfire Statistics: {}\n\n".format(year, now)
results = "\n".join([
    "## Summary\n",
    "\n".join(["{}: {}".format(s["label"], s["value"]) for s in topline_summary_stats]),
    "\n",
    "## Wildfires by county\n",
    "\n".join(["{}: {}\n".format(w["county"], w["n_wildfires"]) for w in wildfires_per_county]),
    "\n",
    "## Wildfires by region\n",
    "### {}:".format(C.NORTHERN_CA_STR),
    "Total fires: {}".format(n_wildfires_by_region["northern_ca"]),
    "Total acres burned: {}\n".format(acres_burned_by_region["northern_ca"]),
    "### {}:".format(C.SOUTHERN_CA_STR),
    "Total fires: {}".format(n_wildfires_by_region["southern_ca"]),
    "Total acres burned: {}\n".format(acres_burned_by_region["southern_ca"]),
    "### {}:".format(C.PGE_STR),
    "Total fires: {}".format(n_wildfires_by_region["pge_area"]),
    "Total acres burned: {}\n".format(acres_burned_by_region["pge_area"])
])

file = open(results_file, "w")
file.write(title)
file.write(results)
file.close()

print("Done.\n")
