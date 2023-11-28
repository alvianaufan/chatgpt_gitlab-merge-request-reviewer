import openai
import time
from flask import Flask, request
import requests
import os

app = Flask(__name__)

# Read OpenAI API key from environment variable
openai.api_key = "insert_chatgpt_apikey_here"

# Model for API requests
model = "text-davinci-003"

# GitLab API endpoint and personal access token
gitlab_url = "https://gitlab.server.com/api/v4"
access_token = "insert-gitlab-access-token-here"

# Headers for API requests
headers = {
    "Private-Token": access_token
}

def get_project_id(payload):
    return payload.get("project_id")

def get_merge_request_iid(payload):
    return payload.get("merge_request", {}).get("iid")

def make_reply(project_id, mr_iid, generated_response):
    reply_url = f"{gitlab_url}/projects/{project_id}/merge_requests/{mr_iid}/notes"
    reply_data = {
        "body": generated_response,
    }
    requests.post(reply_url, headers=headers, data=reply_data)

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        payload = request.get_json()
        print("Received payload:", payload)

        # Check if the payload contains a Comment event
        if payload.get("object_kind") == "note":
            # Extract relevant information from the GitLab webhook payload
            project_id = get_project_id(payload)
            mr_iid = get_merge_request_iid(payload)
            comment_body = payload.get("object_attributes", {}).get("note")

            if project_id is not None and mr_iid is not None and comment_body is not None:
                # Check for different commands
                if "/analyze" in comment_body:
                    handle_analyze_command(project_id, mr_iid)
                elif "/checkcode" in comment_body:
                    handle_checkcode_command(project_id, mr_iid)
                elif "/optimization" in comment_body:
                    handle_custom_command(project_id, mr_iid)
                # Add more commands here as needed

                return "Webhook processed successfully", 200
            else:
                return "Incomplete information in the webhook payload", 200
        else:
            return "Not a Comment event", 200

    except Exception as e:
        return f"Error processing webhook: {str(e)}", 500

def handle_analyze_command(project_id, mr_iid):
    # Your logic for handling the /analyze command
    # Fetch code changes, send to OpenAI, post the response, etc.
    prompt = "tolong analisis penggunaan code ini."

    # Prompt the bot with the custom prompt and generate a response
    response = openai.Completion.create(
        engine=model,
        prompt=prompt,
        max_tokens=500,
    )
    generated_response = response['choices'][0]['text']

    # Make a reply to the merge request with the generated response
    make_reply(project_id, mr_iid, generated_response)

def handle_checkcode_command(project_id, mr_iid):
    # Your logic for handling the /checkstyle command
    # Implement the specific checks, provide feedback, etc.
    prompt = "apakah ada yang salah di code ini?"

    # Prompt the bot with the custom prompt and generate a response
    response = openai.Completion.create(
        engine=model,
        prompt=prompt,
        max_tokens=500,
    )
    generated_response = response['choices'][0]['text']

    # Make a reply to the merge request with the generated response
    make_reply(project_id, mr_iid, generated_response)

def handle_custom_command(project_id, mr_iid):
    # Your logic for handling a custom command
    # Define a specific prompt and response for this command
    prompt = "apakah ada yang dapat di optimasikan di code ini?"

    # Prompt the bot with the custom prompt and generate a response
    response = openai.Completion.create(
        engine=model,
        prompt=prompt,
        max_tokens=500,
    )
    generated_response = response['choices'][0]['text']

    # Make a reply to the merge request with the generated response
    make_reply(project_id, mr_iid, generated_response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
