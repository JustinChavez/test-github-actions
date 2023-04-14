import requests
import json
from decouple import config

# Set your GitHub personal access token here
GITHUB_TOKEN = config('GITHUB_TOKEN')

# Set the repository owner and name here
owner = config('GITHUB_REPO_OWNER')
repo = config('GITHUB_REPO_NAME')

# Set the Unique Identifier for the autolabeler
UNIQUE_IDENTIFIER = config('UNIQUE_IDENTIFIER')

def autolabel_issues(label):

    # Define the API endpoint for searching issues with the label
    api_url = f'https://api.github.com/search/issues?q=repo:{owner}/{repo}+label:{label}+state:open'

    # Make a request to the GitHub API with authentication headers
    response = requests.get(api_url, headers={'Authorization': GITHUB_TOKEN})

    # If the response is not successful, raise an exception with the error message
    response.raise_for_status()

    # Parse the response JSON
    data = json.loads(response.text)

    # Loop through each issue found and update its description if needed
    for issue in data['items']:
        issue_url = issue['url']
        issue_number = issue['number']
        issue_description = issue['body']
        
        # Check if the issue description already contains the autolabeler tag
        if f'{UNIQUE_IDENTIFIER}:{label}' not in issue_description:

            # Check and remove any previous instances of a different autolabeler text
            if '{UNIQUE_IDENTIFIER}:' in issue_description:
                lines = issue_description.split("\n")
                updated_lines = []
                for line in lines:
                    if line.startswith("{UNIQUE_IDENTIFIER}:"):
                        if len(line.split()) == 1:
                            print(f'Removed existing tag {line.split()} from Issue {issue_number}')
                        else:
                            updated_lines.append(line)
                    else:
                        updated_lines.append(line)
                issue_description = "\n".join(updated_lines)
            
            # Append the autolabeler tag to the end of the issue description
            updated_description = issue_description + f'\n\n{UNIQUE_IDENTIFIER}:{label}'

            # Make a PATCH request to the GitHub API with the updated description
            response = requests.patch(
                issue_url,
                headers={
                    'Authorization': f'token {GITHUB_TOKEN}',
                    'Accept': 'application/vnd.github.v3+json'
                },
                json={'body': updated_description}
            )
            # If the response is not successful, raise an exception with the error message
            response.raise_for_status()
            
            print(f'Updated description for issue {issue_number}')
        else:
            print(f'Issue {issue_number} already has autolabeler:{label}')

autolabel_issues(config("LABEL"))