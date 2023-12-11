import os
import sys
import zipfile
import boto3
from botocore.exceptions import NoCredentialsError, ClientError

# Use this script to very quickly update the code of the AWS Lambda function


def zip_dir(path, ziph):
    """Zip the contents of an entire directory (recursively)."""
    for root, dirs, files in os.walk("."):
        for file in files:
            file_path = os.path.join(root, file)
            ziph.write(file_path)


def update_lambda_function(session, function_name, zip_file):
    """Update the AWS Lambda function code."""
    lambda_client = session.client("lambda")
    with open(zip_file, "rb") as f:
        try:
            response = lambda_client.update_function_code(
                FunctionName=function_name, ZipFile=f.read()
            )
            return response
        except (NoCredentialsError, ClientError) as e:
            print(f"An error occurred: {e}")
            return None


if __name__ == "__main__":
    function_dir = "./router"
    zip_file = "soccer-db-router.zip"
    function_name = "soccer-db-router"

    # Get profile from arguments (python update_api_code.py <profile_name>)
    # Optional, if not passed use default profile
    profile = "default"
    if len(sys.argv) > 1:
        profile = sys.argv[1]

    session = boto3.Session(profile_name=profile)

    # Zipping the function directory
    with zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED) as zipf:
        os.chdir(function_dir)
        zip_dir(function_dir, zipf)

    os.chdir("../")

    # Update the Lambda function
    response = update_lambda_function(session, function_name, zip_file)
    if response:
        print("Lambda function updated successfully.")
