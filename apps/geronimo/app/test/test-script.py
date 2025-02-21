"""
This is a manual testing function that loads test data from a CSV file, processes each entry using the `parallel_chain_caller` function, 
and saves the results to a JSON file. It simulates lead information processing and measures response time for each entry,
allowing validation of the parallel execution flow.
"""

import os
import csv
import json
import sys
import time
import utils.constants as constants

# Add the project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from utils.report_generator import parallel_chain_caller


# Define LeadInfo class
class LeadInfo:
    def __init__(self, firstName, lastName, jobTitle, company, country):
        self.firstName = firstName
        self.lastName = lastName
        self.jobTitle = jobTitle
        self.company = company
        self.country = country


# Load test data from a CSV
def load_test_data(file_path):
    with open(file_path, mode="r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        return [row for row in reader]


# Create lead_info dictionary
def create_lead_info(row):
    name_parts = row["name"].split(" ", 1)
    return {
        "firstName": name_parts[0],
        "lastName": name_parts[1] if len(name_parts) > 1 else "",
        "jobTitle": row["job_title"],
        "company": row["company_name"],
        "country": row["country"],
        "state": "",
        "areaOfInterest": "",
        "contactReason": "",
        "industry": "",
        "canHelpComment": "",
    }


# Main function
def main():
    base_dir = os.path.dirname(__file__)
    test_data_path = os.path.join(base_dir, "test_data", "test-data-2.csv")
    response_dir = os.path.join(base_dir, "response")
    os.makedirs(response_dir, exist_ok=True)
    response_path = os.path.join(response_dir, "response-final-2-sel.json")

    # Load test data from CSV
    try:
        test_data = load_test_data(test_data_path)
    except FileNotFoundError:
        return

    # Initialize results list
    results = []

    # Process each row in the test data
    for row in test_data:
        try:

            name_parts = row["name"].split()
            first_name = name_parts[0]
            last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

            # Create LeadInfo object
            lead_info = LeadInfo(
                firstName=first_name,
                lastName=last_name,
                jobTitle=row["job_title"],
                company=row["company_name"],
                country=row["country"],
            )

            start_time = time.time()
            result = parallel_chain_caller(lead_info)
            time.sleep(5)  # Wait before next execution
            end_time = time.time()
            response_time = end_time - start_time

            results.append(
                {"input": row, "output": result, "response_time": response_time}
            )
        except Exception as e:
            results.append({"input": row, "error": str(e), "response_time": None})

        # Save results to a JSON file
        try:
            with open(response_path, mode="w", encoding="utf-8") as jsonfile:
                json.dump(results, jsonfile, indent=4)
        except Exception as e:
            constants.LOGGER.error(f"Error Saving Results: {str(e)}")


# Entry point
if __name__ == "__main__":
    main()
