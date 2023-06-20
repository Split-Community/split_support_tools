import os
import glob
import logging
import csv
import subprocess
import requests
import json
import time
from dotenv import load_dotenv
from splitapiclient.main import get_client

# Set up logging
logging.basicConfig(level=logging.DEBUG)

load_dotenv()
# Load API key from .env file
API_KEY = os.environ.get("ADMIN_API_KEY")
APPROVER_KEY = os.environ.get("APPROVER_API_KEY")

# Initialize the client connection
client = get_client({'apikey': API_KEY})

workspace = "Default"
environment = "Prod-Default"
workspace_id = client.workspaces.find(workspace).id
environment_id = client.environments.find(environment, workspace_id).id
# List of CSV files to process
csv_files = ['early_adopter_users', 'early_adopter_accounts', 'holdout_users', 'holdout_accounts']

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



def segments_sync():
    # Remove all CSV files in current directory
    remove_csv_files('.')
    # Download files from S3 bucket
    download_from_s3('split-prod-gainsight', '.')
    for file in csv_files:
        csv_file = f'{file}.csv'
        if os.path.exists(csv_file):
            keys = process_csv(csv_file)
            segDef = client.segment_definitions.find(file, environment_id, workspace_id)

            # Get existing keys from the segment
            existing_keys = segDef.get_keys()
            print(existing_keys)
            # Remove existing keys
            open_change_request_id = submit_change_request(workspace_id, environment_id, file, existing_keys)
            #approve_change_request(open_change_request_id)
            remove_status = wait_for_approval(open_change_request_id)
            # Submit a change request to add new keys
            if remove_status:
                add_members_request_id = submit_add_members_change_request(workspace_id, environment_id, file, keys)
            # Approve the change request to add new keys
            # approve_change_request(add_members_request_id)
            #segDef.import_keys_from_json("true", {"keys": keys, "comment": "a comment"})
            #print(segDef.get_keys())
        else:
            print(f"CSV file {csv_file} does not exist. Skipping segment {file}.")


def wait_for_approval(change_request_id):
    while True:
        status = get_change_request_status(change_request_id)
        print(f"Status is: {status}")
        if status == "PUBLISHED":
            break
        else:
            time.sleep(5)  # Sleep for 5 minutes (300 seconds)
    return True

def submit_change_request(workspace_id, environment_id, segment_name, keys):
    url = f'https://api.split.io/internal/api/v2/changeRequests/ws/{workspace_id}/environments/{environment_id}'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}'
    }
    data = {
        "segment": {"name": segment_name, "keys": keys},
        "operationType": "ARCHIVE",
        "title": "Some CR Title",
        "comment": "Some CR Comment",
        "approvers": ["tin.tran+1@split.io"]
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    response_data = response.json()
    print(response_data)
    open_change_request_id = response_data['id']
    print(f"Request_Id: {open_change_request_id}")
    return open_change_request_id

def submit_add_members_change_request(workspace_id, environment_id, segment_name, keys):
    url = f'https://api.split.io/internal/api/v2/changeRequests/ws/{workspace_id}/environments/{environment_id}'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}'
    }
    data = {
        "segment": {"name": segment_name, "keys": keys},
        "operationType": "CREATE",
        "title": "Some CR Title",
        "comment": "Some CR Comment",
        "approvers": ["tin.tran+1@split.io"]
    }
    response = requests.post(url, headers=headers, json=data)
    response_data = response.json()
    print(response_data)
    open_change_request_id = response_data['id']
    print(f"Request_Id: {open_change_request_id}")
    return open_change_request_id

def get_change_request_status(change_request_id):
    url = f'https://api.split.io/internal/api/v2/changeRequests/{change_request_id}'
    headers = {
        'Authorization': f'Bearer {API_KEY}'
    }
    response = requests.get(url, headers=headers)
    response_data = response.json()
    return response_data['status']


def approve_change_request(change_request_id):
    url = f'https://api.split.io/internal/api/v2/changeRequests/{change_request_id}'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {APPROVER_KEY}'
    }
    data = {
        "status": "APPROVED",
        "comment": "withdrawing from Admin API"
    }
    requests.put(url, headers=headers, data=json.dumps(data))

segments_sync()


