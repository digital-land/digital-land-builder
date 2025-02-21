#!/usr/bin/env python3

import sys
import csv
import hashlib
from datetime import datetime
import click

dataset = sys.argv[1]
output_path = sys.argv[2]
paths = sys.argv[3:]


def as_timestamp(date):
    if not date:
        return ""
    if len(date) >= 20:
        dt = datetime.strptime(date[:19], "%Y-%m-%dT%H:%M:%S")
    elif len(date) == 20:
        dt = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
    elif len(date) == 10:
        dt = datetime.strptime(date, "%Y-%m-%d")
    elif len(date) == 7:
        dt = datetime.strptime(date, "%Y-%m")
    elif len(date) == 4:
        dt = datetime.strptime(date, "%Y")
    else:
        print("unknown date format", date)
        sys.exit(2)

    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def as_date(date):
    if not date:
        return ""
    if len(date) == 10:
        dt = datetime.strptime(date, "%Y-%m-%d")
    elif len(date) == 7:
        dt = datetime.strptime(date, "%Y-%m")
    elif len(date) == 4:
        dt = datetime.strptime(date, "%Y")
    else:
        print("unknown date format", date)
        sys.exit(2)

    return dt.strftime("%Y-%m-%d")

@click.command()
@click.argument("dataset")
@click.argument("output_path")
@click.argument("paths", nargs=-1, type=click.Path(exists=True))
def process_data(dataset, output_path, paths):
    fieldnames = []
    with open("specification/schema-field.csv", "r", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = [row["field"] for row in reader if row["schema"] == dataset]

    with open(output_path, "w", newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for path in paths:
            with open(path, "r", newline="") as f_in:
                reader = csv.DictReader(f_in)
                for row in reader:
                    if dataset == "source" and row.get("source", ""):
                        key = f"{row['collection']}|{row['organisation']}|{row['endpoint']}"
                        row["source"] = hashlib.md5(key.encode()).hexdigest()

                    if "dataset" in fieldnames and not row.get("dataset", ""):
                        row["dataset"] = row.get("pipeline", "")

                    for col in row:
                        if col == "entry-date":
                            row[col] = as_timestamp(row[col])
                        elif col.endswith("-date"):
                            row[col] = as_date(row[col])

                    writer.writerow(row)



if __name__ == "__main__":
    process_data()
