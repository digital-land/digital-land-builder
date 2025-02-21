#!/usr/bin/env python3

# create a database for exploring collection, specification, configuration and logs


import os
import sys
import logging
import duckdb
import click

from pathlib import Path
from datetime import datetime
from digital_land.specification import Specification
from file_downloader import download_urls


@click.command()
@click.option(
    "--spec-dir",
    default="specification",
    help="Directory containing the dataset specification"
)
@click.option(
    "--cache-dir",
    default="var/expectations",
    help="Directory to store downloaded expectation files"
)
@click.option(
    "--output-dir",
    default="expectation",
    help="Directory to store the final expectation CSV"
)
def process_expectations(spec_dir, cache_dir, output_dir):
    """Fetch expectation Parquet files and convert them to CSV."""

    Path(cache_dir).mkdir(parents=True, exist_ok=True)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    now = datetime.now()
    timestamp = int(now.replace(minute=0, second=0, microsecond=0).timestamp())

    spec = Specification(spec_dir)
    datasets = spec.dataset

    url_map = {}
    for dataset_obj in datasets.values():
        if dataset_obj["collection"]:
            dataset = dataset_obj["dataset"]
            url = (
                f"https://files.planning.data.gov.uk/log/expectation/dataset={dataset}/{dataset}.parquet?version={timestamp}"
            )
            output_path = os.path.join(cache_dir, f"{dataset}.parquet")
            url_map[url] = output_path

    download_urls(url_map)

    expectation_csv = os.path.join(output_dir, "expectation.csv")

    with duckdb.connect() as conn:
        conn.execute(
            f"""
            COPY (
                SELECT * FROM parquet_scan('{cache_dir}/*.parquet', union_by_name=True)
            ) 
            TO '{expectation_csv}' (FORMAT CSV, HEADER TRUE)
            """
        )


if __name__ == "__main__":
    process_expectations()
