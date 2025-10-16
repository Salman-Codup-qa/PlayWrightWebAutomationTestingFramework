from __future__ import print_function
import os
import base64
from email.message import EmailMessage
import re
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# --- CONFIG ---
# The SCOPES define which Gmail permissions we need (Read-only access)
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
# File containing your client ID and secret, downloaded from Google Cloud

# # SALMAN NAME YOUR SECRETS FILE HERE
# CLIENT_SECRETS_FILE = os.getcwd()+r'\utils\credentials.json'

# # File where the script saves your access/refresh token after first login
# TOKEN_FILE = os.getcwd()+r'\utils\token.json'

# SALMAN NAME YOUR SECRETS FILE HERE
CLIENT_SECRETS_FILE = os.getcwd()+r'\utils\credentials.json'

# File where the script saves your access/refresh token after first login
TOKEN_FILE = os.getcwd()+r'\utils\token.json'
print(CLIENT_SECRETS_FILE, TOKEN_FILE)


def get_gmail_service():
    """Authenticate and return Gmail service object."""
    creds = None

    # 1. Check for existing token file
    # Note: Corrected file paths to use simple name, assuming files are in the CWD
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # 2. If no valid credentials, initiate login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # 3. Save the new/refreshed credentials
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)


def extract_text_from_message(msg):
    """Recursively extract the plain text body from a message payload."""
    payload = msg.get('payload', {})
    parts = payload.get('parts')

    if parts:
        # If the message has parts, recurse to find the text/plain part
        for part in parts:
            if part.get('mimeType') == 'text/plain' and 'data' in part['body']:
                body_data = part['body']['data']
                return base64.urlsafe_b64decode(body_data).decode('utf-8')
            # Handle nested parts
            if 'parts' in part:
                result = extract_text_from_message({'payload': part})
                if result:
                    return result

    # If it's a simple message, check the main body
    elif 'data' in payload.get('body', {}):
        body_data = payload['body']['data']
        return base64.urlsafe_b64decode(body_data).decode('utf-8')

    return ""


def extract_otp(msg):
    """
    Extracts a 6-digit OTP from the email body using regular expressions.
    :param msg: The full message object returned by the Gmail API.
    :return: The 6-digit OTP string or None if not found.
    """
    print("\nAttempting to extract OTP...")

    # Get the raw decoded text content
    email_text = extract_text_from_message(msg)

    # Regex: Look for a sequence of exactly 6 digits (\d{6})
    # surrounded by a word boundary (\b) to avoid matching larger numbers.
    otp_regex = r'\b(\d{6})\b'

    match = re.search(otp_regex, email_text)

    if match:
        otp_code = match.group(1)
        print(f"✅ OTP found: {otp_code}")
        return otp_code
    else:
        print("❌ 6-digit OTP pattern not found in the email body.")
        return None


def get_latest_email(query=""):
    """
    Fetch and display the most recent email matching the query, 
    and attempt to extract a 6-digit OTP.
    
    :param query: Optional Gmail search query (e.g., "subject:code from:sender").
    :return: The extracted OTP code (string) or None.
    """
    try:
        service = get_gmail_service()
    except FileNotFoundError:
        print(f"ERROR: Client secrets file '{CLIENT_SECRETS_FILE}' not found.")
        print("Please ensure credentials.json is in the correct location.")
        return None
    except Exception as e:
        print(f"An error occurred during authentication: {e}")
        return None

    # Get list of messages (latest first)
    results = service.users().messages().list(
        userId='me', maxResults=1, q=query).execute()  # Use the optional query
    messages = results.get('messages', [])

    if not messages:
        print("No emails found.")
        return None

    # Get the latest email
    msg_id = messages[0]['id']
    msg = service.users().messages().get(
        userId='me', id=msg_id, format='full').execute()

    headers = msg['payload']['headers']
    subject = next((h['value']
                    for h in headers if h['name'] == 'Subject'), '(No Subject)')
    sender = next((h['value'] for h in headers if h['name']
                   == 'From'), '(Unknown Sender)')
    snippet = msg.get('snippet', '')

    print("====================================")
    print("📨 Latest Email Fetched Successfully:")
    print("====================================")
    print(f"From: {sender}")
    print(f"Subject: {subject}")
    print(f"Snippet: {snippet}")

    # CALL THE NEW OTP EXTRACTION FUNCTION
    otp = extract_otp(msg)

    return otp


# if __name__ == '__main__':
#     # You can customize the query here to filter for specific senders or subjects
#     # Example: query="subject:code from:dmflighting.com"
#     otp_code = get_latest_email(query="subject:code")

#     if otp_code:
#         print(f"\nFinal Extracted OTP for use: {otp_code}")
#     else:
#         print("\nOTP extraction failed. Check email content and regex.")
