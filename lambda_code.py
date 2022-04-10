import json
import os
import boto3
import base64
import urllib3
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    # Collecting payload from 
    payload = json.loads(event["body"])
    # Http request handler
    http = urllib3.PoolManager()
    
    # Exit webhook early as we only want to handle created event types
    if payload["action"] != "created":
        return {
            'statusCode': 200,
            'body': json.dumps('Thanks for chatting!')
        }
    # Collect repo information from webhook payload
    repo_owner = payload["repository"]["owner"]["login"]
    repo_name = payload["repository"]["name"]
    default_branch = payload["repository"]["default_branch"]
    # Placeholder for token so it can be used later
    token = ""
    
    # Get GH token from Secrets Manager, this code is provided by AWS when for querying secrets
    
    # POPULATE SOMETHING HERE
    secret_name = "Place your secret ARN HERE" 
    region_name = "us-east-1"
    
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    
    # Wrap the secret query in a try block
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print("The requested secret " + secret_name + " was not found")
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            print("The request was invalid due to:", e)
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            print("The request had invalid params:", e)
        elif e.response['Error']['Code'] == 'DecryptionFailure':
            print("The requested secret can't be decrypted using the provided KMS key:", e)
        elif e.response['Error']['Code'] == 'InternalServiceError':
            print("An error occurred on service side:", e)
    else:
        if 'SecretString' in get_secret_value_response:
            token = json.loads(get_secret_value_response['SecretString'])
        else:
            token = base64.b64decode(get_secret_value_response['SecretBinary'])
    
    # Creating and making Github branch protection request
    # Replace the 'teams' contents with the code reviewer team in your github org
    bp_body = json.dumps({
        "required_status_checks": None,
        "enforce_admins": True,
        "required_pull_request_reviews": {
            "dismissal_restrictions": {
                "users": [],
                "teams": ["CHANGE TO CODE REVIEW TEAM"]
            },
            "dismiss_stale_reviews": True,
            "require_code_owner_reviews": True,
            "required_approving_review_count": 1,
            "bypass_pull_request_allowances": {
                "users": [],
                "teams": ["CHANGE TO CODE REVIEW TEAM"]
            }
        },
        "restrictions": None
    })
    bp_url = "https://api.github.com/repos/"+repo_owner+"/"+repo_name+"/branches/"+default_branch+"/protection"
    bp_headers = {'Authorization': 'bearer '+token["gh_token"]}
    bp_response = http.request('PUT', bp_url,
                 headers=bp_headers,
                 body=bp_body)
    
    # Creating and sending GitHub Issue request
    issue_body = json.dumps({
        "title":"Branch Protection on your new repo",
        "body": "Welcome to the org @"+ payload["sender"]["login"] +"! Thanks for creating the repo. Branch protection has been applied to the " + default_branch + " branch that requires code review from a team in this organization for all code going to that branch. Check out the group section of the org to reach out to someone who can help you get started."
    })
    issue_url = "https://api.github.com/repos/"+repo_owner+"/"+repo_name+"/issues"
    issue_headers = {'Authorization': 'bearer '+token["gh_token"], 'Accept': 'application/vnd.github.v3+json'}
    issue_response = http.request('POST', issue_url,
                 headers=issue_headers,
                 body=issue_body)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Repo was processed!')
    }