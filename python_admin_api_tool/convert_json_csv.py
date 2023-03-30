import csv
import json
import os
import glob

def json_to_csv(json_file, csv_file):
    with open(json_file, "r") as file:
        data = json.load(file)

    if isinstance(data, dict):
        keys = set()
        for obj in data.values():
            if isinstance(obj, list):
                for item in obj:
                    if isinstance(item, dict):
                        keys |= set(item.keys())
            elif isinstance(obj, dict):
                keys |= set(obj.keys())

        with open(csv_file, "w", newline="") as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys)
            dict_writer.writeheader()

            for obj in data.values():
                if isinstance(obj, list):
                    for item in obj:
                        if isinstance(item, dict):
                            dict_writer.writerow(item)
                elif isinstance(obj, dict):
                    dict_writer.writerow(obj)

def convert_all_json_to_csv():
    for json_file in glob.glob("*.json"):
        csv_file = os.path.splitext(json_file)[0] + ".csv"
        json_to_csv(json_file, csv_file)
        print(f"Converted {json_file} to {csv_file}")

convert_all_json_to_csv()
