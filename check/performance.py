import logging
import sqlite3
from digital_land.expectations.operation import (
    check_columns
)

logger = logging.getLogger("__name__")

EXPECTED = {
    "endpoint_dataset_issue_type_summary": ['organisation', 'organisation_name', 'cohort', 'dataset', 'collection', 'pipeline', 'endpoint', 'endpoint_url', 'resource', 'resource_start_date', 'resource_end_date', 'latest_log_entry_date', 'count_issues', 'date', 'issue_type', 'severity', 'responsibility', 'field'],
    "endpoint_dataset_resource_summary": ['organisation', 'organisation_name', 'cohort', 'dataset', 'collection', 'pipeline', 'endpoint', 'endpoint_url', 'resource', 'resource_start_date', 'resource_end_date', 'latest_log_entry_date', 'mapping_field', 'non_mapping_field'],
    "endpoint_dataset_summary": ['organisation', 'dataset', 'endpoint', 'endpoint_url', 'documentation_url', 'resource', 'latest_status', 'latest_exception', 'latest_log_entry_date', 'entry_date', 'end_date', 'latest_resource_start_date', 'resource_end_date'],
    "provision_summary": ['organisation', 'organisation_name', 'dataset', 'provision_reason', 'provision_end_date', 'active_endpoint_count', 'error_endpoint_count', 'count_issue_error_internal', 'count_issue_error_external', 'count_issue_warning_internal', 'count_issue_warning_external', 'count_issue_notice_internal', 'count_issue_notice_external'],
    "reporting_historic_endpoints": ['organisation', 'name', 'organisation_name', 'dataset', 'collection', 'pipeline', 'endpoint', 'endpoint_url', 'documentation_url', 'licence', 'latest_status', 'latest_exception', 'resource', 'latest_log_entry_date', 'endpoint_entry_date', 'endpoint_end_date', 'resource_start_date', 'resource_end_date'],
    "reporting_latest_endpoints": ['organisation', 'name', 'organisation_name', 'dataset', 'collection', 'pipeline', 'endpoint', 'endpoint_url', 'licence', 'latest_status', 'days_since_200', 'latest_exception', 'resource', 'latest_log_entry_date', 'endpoint_entry_date', 'endpoint_end_date', 'resource_start_date', 'resource_end_date', 'rn']
}

def check_performance_columns():
    try:
        conn = sqlite3.connect("dataset/performance.sqlite3").cursor()
        result, message, details = check_columns(conn, EXPECTED)
        if not result:
            logging.error("Column check failed for performance DB")
            logging.error(message)
            for item in details:
                if not item["success"]:
                    logging.error(f"{item['table']} did not have all expected columns. Missing columns: {item['missing']}")
                    logging.error(f"Columns found: {item['actual']}")
            raise Exception(f"Performance DB check failed: {message}")
    finally:
        conn.close()


if __name__ == "__main__":
    check_performance_columns()