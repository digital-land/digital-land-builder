#!/usr/bin/env python3

# create a database for exploring collection, specification, configuration and logs

import os
import sys
import csv
import logging
import sqlite3
from digital_land.package.sqlite import SqlitePackage


tables = {
    "organisation": "var/cache",

    "source": "collection",
    "endpoint": "collection",
    "resource": "collection",
    "old-resource": "collection",
    "log": "collection",

    "collection": "specification",
    "theme": "specification",
    "typology": "specification",
    "dataset": "specification",
    "dataset-field": "specification",
    "field": "specification",
    "datatype": "specification",
    "prefix": "specification",
    "severity": "specification",
    "issue-type": "specification",
    "attribution": "specification",
    "licence": "specification",
    "cohort": "specification",
    "include-exclude": "specification",
    "role": "specification",
    "role-organisation": "specification",
    "role-organisation-rule": "specification",
    "project": "specification",
    "project-organisation": "specification",
    "project-status": "specification",
    "provision": "specification",
    "provision-rule": "specification",
    "provision-reason": "specification",
    "specification": "specification",
    "specification-status": "specification",

    "column": "pipeline",
    "combine": "pipeline",
    "concat": "pipeline",
    "convert": "pipeline",
    "default": "pipeline",
    "default-value": "pipeline",
    "patch": "pipeline",
    "skip": "pipeline",
    "transform": "pipeline",
    "filter": "pipeline",
    "lookup": "pipeline",

    "issue": "issues",

    "column-field": "column-field",

    "expectation-result": "expectations",
    "expectation-issue": "expectations",
}

indexes = {
    "source": ["endpoint"],
    "issue": ["resource", "field", "issue-type"],
    "issue-type": ["severity"],
    "log": ["endpoint", "resource"],
    "resource_dataset": ["resource", "dataset"],
    "resource_endpoint": ["resource", "endpoint"],
    "resource_organisation": ["resource", "organisation"],
    "specification_dataset": ["specification", "dataset"],
    "provision": ["organisation", "dataset", "project", "cohort", "provision_reason"],
    "expectation-issue": ["expectation-result"],
}


if __name__ == "__main__":
    level = logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(message)s")
    path = sys.argv[1] if len(sys.argv) > 1 else "dataset/digital-land.sqlite3"
    package = SqlitePackage("digital-land", path=path, tables=tables, indexes=indexes)
    package.create()

    conn = sqlite3.connect(path)
    conn.execute("""
    CREATE TABLE reporting_most_recent_log AS
    select t1.*
        from log t1 
        inner join (
            SELECT endpoint,max(date(entry_date)) as most_recent_log_date
            FROM log 
            GROUP BY endpoint
            ) t2 on t1.endpoint = t2.endpoint
        where date(t1.entry_date) = t2.most_recent_log_date
    """)

    conn.execute("""
    CREATE TABLE reporting_historic_endpoints AS
    SELECT
        s.organisation,
        o.name,
        s.collection,
        sp.pipeline,
        l.endpoint,
        e.endpoint_url,
        l.status,
        l.exception,
        l.resource,

        max(l.entry_date) as latest_log_entry_date,
        e.entry_date as endpoint_entry_date,
        e.end_date as endpoint_end_date,
        r.start_date as resource_start_date,
        r.end_date as resource_end_date

    FROM
        log l
        INNER JOIN source s on l.endpoint = s.endpoint
        INNER JOIN endpoint e on l.endpoint = e.endpoint
        INNER JOIN organisation o on o.organisation = replace(s.organisation, '-eng', '')
        INNER JOIN source_pipeline sp on s.source = sp.source
        LEFT JOIN resource r on l.resource = r.resource

    WHERE
        s.collection IN ("article-4-direction", "conservation-area", "listed-building", "tree-preservation-order")
        
    GROUP BY
        1, 2, 3, 4, 5, 6, 7, 8, 9

    ORDER BY
        s.organisation, o.name, s.collection, sp.pipeline, latest_log_entry_date DESC
    """)

    conn.execute("""
    CREATE TABLE reporting_latest_endpoints AS
        SELECT * 
            from (
            SELECT
                s.organisation,
                o.name,
                s.collection,
                sp.pipeline,
                l.endpoint,
                e.endpoint_url,
                l.status,
                t2.days_since_200,
                l.exception,
                l.resource,

                max(l.entry_date) as latest_log_entry_date,
                e.entry_date as endpoint_entry_date,
                e.end_date as endpoint_end_date,
                r.start_date as resource_start_date,
                r.end_date as resource_end_date,
            
                row_number() over (partition by s.organisation,sp.pipeline order by e.entry_date desc, l.entry_date desc) as rn

            FROM
                log l
                INNER JOIN source s on l.endpoint = s.endpoint
                INNER JOIN endpoint e on l.endpoint = e.endpoint
                INNER JOIN organisation o on o.organisation = replace(s.organisation, '-eng', '')
                INNER JOIN source_pipeline sp on s.source = sp.source
                LEFT JOIN resource r on l.resource = r.resource
                LEFT JOIN (
                    SELECT
                        endpoint,
                        cast(julianday('now') - julianday(max(entry_date)) as int) as days_since_200
                    FROM
                        log
                    WHERE
                        status=200
                    GROUP BY
                        endpoint
                ) t2 on e.endpoint = t2.endpoint

            WHERE
                s.collection IN ("article-4-direction", "conservation-area", "listed-building", "tree-preservation-order")
                and e.end_date=''
            GROUP BY
                1, 2, 3, 4, 5, 6, 7, 8, 9

            ORDER BY
                s.organisation, o.name, s.collection, sp.pipeline, endpoint_entry_date DESC
            ) t1
        where t1.rn = 1              
    """)
    conn.close()
