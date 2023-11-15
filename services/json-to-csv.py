import csv
import json


def json_to_csv(json_data, csv_filename):
    # Assuming json_data is a list of dictionaries as in your example
    # and csv_filename is the desired name for the CSV file

    # Extracting headers from the first dictionary in the JSON data
    headers = json_data[0].keys()

    # Writing to CSV file
    with open(csv_filename, 'w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)

        # Write headers
        writer.writeheader()

        # Write data
        writer.writerows(json_data)


file_path = "../data/ratings.json"
# Load data2 from the JSON file
with open(file_path, "r") as json_file:
    data = json.load(json_file)

csv_filename = "../data/ratings_data.csv"

json_to_csv(data, csv_filename)
print(f"Data exported to {csv_filename}")
