#!/usr/bin/env python3

# create a database for exploring collection, specification, configuration and logs

import os
import sys
import csv
import logging
import sqlite3
import duckdb

from pathlib import Path
from urllib.error import HTTPError
from  datetime import datetime

from urllib.request import urlretrieve
import pandas as pd
from digital_land.specification import Specification

from file_downloader import download_urls

spec = Specification('specification')
cache_exp_dir = 'var/expectations'
Path(cache_exp_dir).mkdir(parents=True, exist_ok=True)
now = datetime.now()
timestamp = int(now.replace(minute=0, second=0, microsecond=0).timestamp())

datasets = spec.dataset
url_map =  {}
for dataset_obj in datasets.values():
    if dataset_obj['collection']:
        s3="https://files.planning.data.gov.uk"
        dataset = dataset_obj['dataset']
        url = f"https://files.planning.data.gov.uk/log/expectation/dataset={dataset}/{dataset}.parquet?version={timestamp}"
        output_path = cache_exp_dir + f"/{dataset}.parquet"
        url_map[url] = output_path

download_urls(url_map)

conn = duckdb.connect()
Path('expectation').mkdir(parents=True, exist_ok=True)
conn.execute(
    f"""
        COPY (
            SELECT * FROM parquet_scan('{cache_exp_dir}/*.parquet',union_by_name=True)
        ) 
        TO 'expectation/expectation.csv' (FORMAT CSV, HEADER TRUE)
    """
)
