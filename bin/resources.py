#!/usr/bin/env python3

import sys
import csv
import click

@click.command()
@click.option(
    "--input-dir", 
    default="collection/", 
    help="Directory containing the CSV files"
)
def process_data(input_dir):
    """Process CSV files to map resources, endpoints, and pipelines."""
    
    endpoints = {}
    resources = {}

    # Load endpoints
    try:
        with open(f"{input_dir}/endpoint.csv", newline="") as f:
            for row in csv.DictReader(f):
                endpoint = row["endpoint"]
                endpoints[endpoint] = row
                endpoints[endpoint].setdefault("pipelines", {})
                endpoints[endpoint].setdefault("collection", "")
    except FileNotFoundError:
        print("Error: endpoint.csv not found", file=sys.stderr)
        sys.exit(1)

    # Load sources
    try:
        with open(f"{input_dir}/source.csv", newline="") as f:
            for row in csv.DictReader(f):
                endpoint = row["endpoint"]
                if endpoint and endpoint in endpoints:
                    for pipeline in row["pipelines"].split(";"):
                        endpoints[endpoint]["pipelines"][pipeline] = True
                        endpoints[endpoint]["collection"] = row["collection"]
    except FileNotFoundError:
        print("Error: source.csv not found", file=sys.stderr)
        sys.exit(1)

    # Load old-resource mapping
    old_resources_map = {}
    try:
        with open(f"{input_dir}/old-resource.csv", newline="") as f:
            for row in csv.DictReader(f):
                old_resources_map[row["old-resource"]] = row["resource"]
    except FileNotFoundError:
        pass  # If the file doesn't exist, we just skip it.

    # Load resources
    try:
        with open(f"{input_dir}/resource.csv", newline="") as f:
            for row in csv.DictReader(f):
                resource = row["resource"]
                if resource in old_resources_map:
                    continue  # Skip old resources
                
                resources[resource] = row
                resources[resource].setdefault("pipelines", {})
                resources[resource]["endpoints"] = row["endpoints"].split(";")

                # Add collections and pipelines
                for endpoint in resources[resource]["endpoints"]:
                    if endpoint in endpoints:
                        endpoints[endpoint].setdefault("resource", {})
                        endpoints[endpoint][resource] = True
                        resources[resource]["collection"] = endpoints[endpoint]["collection"]

                        for pipeline in endpoints[endpoint]["pipelines"]:
                            resources[resource]["pipelines"][pipeline] = True
    except FileNotFoundError:
        print("Error: resource.csv not found", file=sys.stderr)
        sys.exit(1)

    # Print results
    for resource in resources:
        collection = resources[resource]["collection"]
        for pipeline in resources[resource]["pipelines"]:
            print(collection, pipeline, resource)

if __name__ == "__main__":
    process_data()
