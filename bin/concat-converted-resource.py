#!/usr/bin/env python3

import sys
import csv
import glob
import re
import os
import click

@click.command()
@click.option(
    "--input-dir",
    default="var/converted-resource/",
    help="Directory containing converted resource CSV files"
)
@click.option(
    "--output-dir",
    default="converted-resource/",
    help="Directory where the processed CSV file will be saved"
)
def process_converted_resources(input_dir, output_dir):
    """Processes converted resource CSV files and writes output."""

    fields = ["dataset", "resource", "elapsed", "status", "exception"]
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, "converted-resource.csv")

    with open(output_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fields)
        writer.writeheader()

        for path in glob.glob(f"{input_dir}/*/*.csv"):
            m = re.search(r"/([a-zA-Z0-9_-]+)/([a-f0-9]+).csv$", path)

            dataset = m.group(1)
            resource = m.group(2)

            with open(path, newline="") as infile:
                for row in csv.DictReader(infile):
                    if row["dataset"] != dataset:
                        print(f"Dataset mismatch. dir={dataset} file={row['dataset']}")
                    if row["resource"] != resource:
                        print(f"Resource mismatch. dir={resource} file={row['resource']}")

                    writer.writerow(row)

if __name__ == "__main__":
    process_converted_resources()
