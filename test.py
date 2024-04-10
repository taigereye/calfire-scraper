import argparse
from collections import defaultdict
import glob
import math
import re

import utils.constants as C

parser = argparse.ArgumentParser(description="Simple tests to see if data scraped correctly")

parser.add_argument("-f", required=True, help="which file to check")
args = parser.parse_args()
filename = args.f

print("\n")

files = glob.glob("calfire_summary_2024-04-08_00--56--25.md")
if len(files) == 0:
    print("File not found.\n")
else:
    with open(files[0], 'r') as file:
        contents = file.read()

    # Extract total acres burned as calculated from wildfires_per_county data
    regions = [C.NORTHERN_CA_STR, C.SOUTHERN_CA_STR, C.PGE_STR]
    acres = defaultdict(int)
    for r in regions:
        acres_match = re.search(fr"{r}:\nTotal fires: \d+\nTotal acres burned: (\d+)", contents)
        if acres_match:
            acres[r] = int(acres_match.group(1).replace(',', ''))

    # Extract total acres burned as calculated on CalFire
    total_match = re.search(r"Acres Burned: ([\d,]+)", contents)
    if total_match:
        total = int(total_match.group(1).replace(',', ''))

    assert total is not None, "Could not find total acres burned value from CalFire"
    calculated_total = acres[C.NORTHERN_CA_STR] + acres[C.SOUTHERN_CA_STR]

    print("CalFire total: {}\n".format(total))
    print("Calculated total: {}\n".format(calculated_total))
    for r in regions:
        print("{}: {}\n".format(r, acres[r]))
    
    assert math.isclose(total, calculated_total, rel_tol=0.1), "CalFire total and calculated total are more than 10%% apart"

    print("\nDone.")
