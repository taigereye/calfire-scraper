import argparse
import os
import glob

parser = argparse.ArgumentParser(description="Remove old raw and/or results files from previous runs")

parser.add_argument("-f", help="which files to delete: raw or results")
args = parser.parse_args()
type = args.f

print("\n")

raw_files = glob.glob('data/*calfire_raw_data*')
summary_files = glob.glob('data/*calfire_*_summary*')
avg_files = glob.glob('data/*calfire_avg*')

files = raw_files if type == "raw" else summary_files + avg_files

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