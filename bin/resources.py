import csv
import sys

endpoints = {}
resources = {}
pipelines = {}

def get_endpoints():
    # TBD: replace with a single SQL query on a collection database ..
    for row in csv.DictReader(open("collection/endpoint.csv", newline="")):
        endpoint = row["endpoint"]
        endpoints[endpoint] = row
        endpoints[endpoint].setdefault("pipelines", {})
        endpoints[endpoint].setdefault("collection", "")

# load sources
    for row in csv.DictReader(open("collection/source.csv", newline="")):
        endpoint = row["endpoint"]

        if endpoint:
            if endpoint not in endpoints:
                print("unknown endpoint", row, file=sys.stderr)
            else:
                # add collection and pipelines to each endpoint
                for pipeline in row["pipelines"].split(";"):
                    endpoints[endpoint]["pipelines"][pipeline] = True
                    endpoints[endpoint]["collection"] = row["collection"]
    return endpoints

def get_old_resources():
    old_resources_map = {}
    # Load old-resource.csv to create a mapping of old to updated resources
    for row in csv.DictReader(open("collection/old-resource.csv", newline="")):
        old_resource = row["old-resource"]
        updated_resource = row["resource"]
        old_resources_map[old_resource] = updated_resource
    
    return old_resources_map

def get_resources(endpoints,old_resources_map):
    # load resources
    for row in csv.DictReader(open("collection/resource.csv", newline="")):
        resource = row["resource"]

    # Skip this resource if it's an old resource
        if resource in old_resources_map:
            continue

        resources[resource] = row
        resources[resource].setdefault("pipelines", {})
        resources[resource]["endpoints"] = row["endpoints"].split(";")

        # add collections to the resource
        for endpoint in resources[resource]["endpoints"]:
            if endpoint in endpoints:
                endpoints[endpoint].setdefault("resource", {})
                endpoints[endpoint][resource] = True
                resources[resource]["collection"] = endpoints[endpoint]["collection"]

                # add pipelines to resource
                for pipeline in endpoints[endpoint]["pipelines"]:
                    resources[resource]["pipelines"][pipeline] = True
        
    return resources

if __name__=="__main__":
    resources = get_resources()
    for resource in resources:
        collection = resources[resource]["collection"]
        for pipeline in resources[resource]["pipelines"]:
            print(collection, pipeline, resource)
