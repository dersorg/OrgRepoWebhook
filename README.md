# OrgRepoWebhook
Lambda code to create a GitHub org webhook recieving repository events.

## Requirements to run the webhook

- AWS account to run the webhook. They are free to set up, this project will use resources in the 'free' tier of AWS.
- GitHub org created.
- GitHub Personal Access Token created with 'repo' permissions. We will use this later to make GitHub API requests.


## Setup to run the webhook

### AWS Setup
**Secret Manager**
- Log into your AWS account and navigate to Secrets Manager.
- Create a new secret of type 'Other'. Populate the key:value with the 'key' as `gh_token` and the 'value' the Personal Access Token you created earlier.
- Name the secret whatever you like, be sure to collect the arn as we will need it when entering the Lambda code.

**IAM**
- Navigate to the IAM portion of AWS.
- Select the `Roles` portion of the page and click `Create Role` in the upper right corner.
- Select `AWS service` as the trusted entity, and `Lambda` as the use case.
- On the `Add Permissions` page, click `Create Policy` in the upper right corner. This should navigate you to a new page.
- On this new page, select the JSON editor and populate this page with the `lambda_policy.json` policy dock. Notice that you will have to change some values based on your account and region.
- Follow the rest of the creation steps and create the policy.
- Return to the IAM tab and refresh the page. Find the policy you just created, check the box next to it and click `Next`.
- Name the role and complete the role creation.

**Lambda**
- Now navitate to the Lambda portion of AWS.
- Create a new Lambda function. Select `Author from scratch`, name the function however you like, and chose the `Python 3.9` runtime. Under Permissions, chante the Execution role to `Use an existing role` and select the role you just created.
- Copy the code code in the `lambda_code.py` file in this repo into the `lambda_function` window. Keep in mind that you will have to replace some values, notibly your AWS region and your secret arn.
- When you are ready, click `Deploy` to save the function.

**API Gateway**
- Navigate to the API Gateway portion of AWS.
- Click `Create API`.
- Select a `HTTP API`.
- Select `Add integration` and add the Lambda function you just created. Name the integration whatever you like. Click next.
- Configure the route path to be whatever you like. Perhaps name it, `/org_repo_events`. Click next.
- Do not change the default on `Stages`. Click next, then click Create.
- On this landing page you will see an `Invoke URL`. Copy this URL, it's time to finish the GitHub setup.

### GitHub Setup
**Configure Webhook**
- Navigate to your GitHub org settings page, go the Webhooks section and add a new webhook.
- Populate the `Payload URL` with the Invoke URL you got from AWS. Do not forget to include the path you created along with it.
- Set the Content type to `application/json`.
- Update the event options to only send only `Repositories` events, then click `Add Webhook`.

### Time to test!
- To test this function, go to your GitHub org and create a new repo. Make sure the repo is public and initiate it with a README.md file.

