#!/usr/bin/env python3

import sys
import csv
import glob
import re
import os
import click

@click.command()
@click.option(
    "--column-field-dir", 
    default="column-field//", 
    help="Directory where column-field.csv will be stored"
)
@click.option(
    "--input-dir", 
    default="var/column-field/", 
    help="Directory containing column-field CSV files"
)
def process_column_fields(column_field_dir, input_dir):
    """Processes indivisual column fields CSV files and writes output."""
  

    fields = ["dataset", "resource", "column", "field",  "entry-date", "end-date", "start-date"]

    column_field_dir = "column-field/"
    os.makedirs(column_field_dir, exist_ok=True)

    with open(os.path.join(column_field_dir, "column-field.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fields)
        w.writeheader()


        for path in glob.glob(f"{input_dir}/*/*.csv"):
            m = re.search(r"/([a-zA-Z0-9_-]+)/([a-f0-9]+).csv$", path)
            pipeline = m.group(1)
            resource = m.group(2)

            with open(path, newline="") as infile:
                    for row in csv.DictReader(infile):
                        row["resource"] = resource
                        row["dataset"] = pipeline
                        w.writerow(row)

if __name__ == "__main__":
    process_column_fields()
