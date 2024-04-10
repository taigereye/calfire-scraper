import subprocess
import argparse

from utils import constants as C

class ScraperRunner:
    def __init__(self, **kwargs):
        self.script_path = kwargs.get('script_path', C.PATH_TO_SCRAPER)
        self.run_type = kwargs.get('run_type')
        self.description = kwargs.get('parser_description')
        self.years = []

    def initialize_args(self):
        self.arg_parser = ScraperArgParser(
            run_type=self.run_type,
            description=self.description
        )
        self.arg_parser.add_args()
        self.arg_parser.parse()
        if self.arg_parser.run_type == C.SINGLE:
            self.years = [self.arg_parser.args.y]
        elif self.arg_parser.run_type == C.MULTIPLE:
            if self.arg_parser.args.y:
                self.years = [self.arg_parser.args.y]
            elif self.arg_parser.args.yr:
                year_start = int(self.arg_parser.args.yr[0])
                year_end = int(self.arg_parser.args.yr[1])
                self.years = list(range(year_start, year_end+1))
            self.n_years = len(self.years)
        else:
           self.arg_parser.raise_invalid_type()
        self.save_raw = self.arg_parser.args.r

    def run(self, year):
        print("\n")
        if self.save_raw:
            subprocess.run(["python", self.script_path, "-y", str(year), "-r"])
        else:
            subprocess.run(["python", self.script_path, "-y", str(year)])

    def run_one(self):
        self.initialize_args()
        self.run(self.years[0])

    def run_all(self):
        self.initialize_args()
        for y in self.years:
            self.run(y)


class ScraperArgParser:
    def __init__(self, **kwargs):
        self.run_type = kwargs.get('run_type')
        self.description = kwargs.get('parser_description')
        self.parser = argparse.ArgumentParser(self.description)
    
    def add_args(self):
        if self.run_type == C.SINGLE:
            self.parser.add_argument("-y", required=True, help="year of fire season in YYYY form")
        elif self.run_type == C.MULTIPLE:
            self.parser.add_argument("-y", nargs='+', help="year(s) of fire season in YYYY format no spaces, averages computed for all values")
            self.parser.add_argument("-yr", nargs=2, help="exactly 2 year(s) of fire season in YYYY format no spaces, averages computed for all years in inclusive range")
        else:
            self.raise_invalid_type()
        self.parser.add_argument("-r", action='store_true', help="also save raw data in separate file(s)")

    def raise_invalid_args(self, message):
        raise ValueError("Invalid args for running: {}".format(message))
    
    def raise_invalid_type(self):
        raise ValueError("Invalid type for running: {}".format(self.run_type))
        
    def parse(self):
        self.args = self.parser.parse_args()
        if not self.args.y and not self.args.yr:
            self.raise_invalid_args("must specify either -y or -yr to run scraper")
