import os
import glob
import logging
import csv
import subprocess
from dotenv import load_dotenv
from splitapiclient.main import get_client

# Set up logging
logging.basicConfig(level=logging.DEBUG)

load_dotenv()
# Load API key from .env file
API_KEY = os.environ.get("ADMIN_API_KEY")
# Initialize the client connection
client = get_client({'apikey': API_KEY})

def remove_csv_files(directory):
    """
    Remove all CSV files from a directory.
    """
    files = glob.glob(f"{directory}/*.csv")
    for file in files:
        os.remove(file)

def download_from_s3(bucket, destination):
    """
    Download from S3
    """
    command = f"aws s3 cp s3://{bucket}/ {destination} --recursive"
    subprocess.run(command, shell=True, check=True)

def process_csv(file_name):
    with open(file_name, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip the header
        keys = [row[0] for row in reader]
    return keys

workspace = "Default"
environment = "Prod-Default"
workspace_id = client.workspaces.find(workspace).id
environment_id = client.environments.find(environment, workspace_id).id
# List of CSV files to process
csv_files = ['early_adopter_users', 'early_adopter_accounts', 'holdout_users', 'holdout_accounts']

def segments_sync():
    # Remove all CSV files in current directory
    remove_csv_files('.')
    # Download files from S3 bucket
    download_from_s3('split-prod-gainsight', '.')
    for file in csv_files:
        csv_file = f'{file}.csv'
        if os.path.exists(csv_file):
            keys = process_csv(csv_file)
            #print(keys)
            segDef = client.segment_definitions.find(file, environment_id, workspace_id)
            segDef.import_keys_from_json("true", {"keys": keys, "comment": "a comment"})
            #print (segDef.get_keys())
        else:
            print(f"CSV file {csv_file} does not exist. Skipping segment {file}.")

segments_sync()
