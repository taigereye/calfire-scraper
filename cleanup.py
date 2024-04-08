import argparse
import os
import glob

parser = argparse.ArgumentParser(description="Cleanup old raw and/or results files from previous runs")

parser.add_argument("-f", help="which files to delete: raw or results")
args = parser.parse_args()
type = args.f

print("\n")

raw_files = glob.glob('*calfire_raw_data*')
results_files = glob.glob('*calfire_summary*')

files = raw_files if type == "raw" else results_files

for file in files:
    confirm = input(f"Are you sure you want to delete {file}? (yes/no) ")

    if confirm.lower() in ["yes", "y"]:
        # Delete the file
        os.remove(file)
        print(f"\nDeleted: {file}")
    else:
        print(f"\nSkipped: {file}")

if len(files) >= 1:
    print("\nDone.")
else:
    print("No files to delete.")