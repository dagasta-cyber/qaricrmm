import base64
import json
import logging
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
import database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify"
]

def get_oauth_flow():
    """Builds and returns the Google OAuth flow using settings from database."""
    client_id = database.get_setting("google_client_id")
    client_secret = database.get_setting("google_client_secret")
    redirect_uri = database.get_setting("google_redirect_uri")
    
    if not client_id or not client_secret:
        logger.warning("Gmail OAuth credentials (client_id/client_secret) are not configured.")
        return None
        
    client_config = {
        "web": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [redirect_uri]
        }
    }
    
    return Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=redirect_uri
    )

def get_auth_url():
    """Generates the authorization URL to redirect the user to."""
    flow = get_oauth_flow()
    if not flow:
        return None
    authorization_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent"
    )
    return authorization_url

def exchange_code_for_credentials(code):
    """Exchanges authorization code for access/refresh tokens and stores them."""
    flow = get_oauth_flow()
    if not flow:
        return False
    
    flow.fetch_token(code=code)
    creds = flow.credentials
    
    # Store credentials in settings table
    creds_dict = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": creds.scopes
    }
    
    database.save_settings({"gmail_credentials": json.dumps(creds_dict)})
    logger.info("Gmail OAuth credentials saved successfully.")
    return True

def get_gmail_service():
    """Creates a Gmail API service instance, refreshing tokens dynamically if needed."""
    creds_json = database.get_setting("gmail_credentials")
    if not creds_json:
        return None
        
    try:
        creds_dict = json.loads(creds_json)
        creds = Credentials(
            token=creds_dict.get("token"),
            refresh_token=creds_dict.get("refresh_token"),
            token_uri=creds_dict.get("token_uri"),
            client_id=creds_dict.get("client_id"),
            client_secret=creds_dict.get("client_secret"),
            scopes=creds_dict.get("scopes")
        )
        
        # Check if expired and refresh
        if creds.expired and creds.refresh_token:
            from google.auth.transport.requests import Request
            creds.refresh(Request())
            # Save refreshed credentials back
            creds_dict["token"] = creds.token
            database.save_settings({"gmail_credentials": json.dumps(creds_dict)})
            logger.info("Gmail access token refreshed and saved.")
            
        return build("gmail", "v1", credentials=creds)
    except Exception as e:
        logger.error(f"Error initializing Gmail API service: {e}")
        return None

def parse_email_body(payload):
    """Recursively parses a MIME email payload to extract the text content."""
    body = ""
    if "parts" in payload:
        for part in payload["parts"]:
            # Prefer plain text, fallback to html if needed
            mime_type = part.get("mimeType", "")
            if mime_type == "text/plain":
                data = part.get("body", {}).get("data", "")
                if data:
                    body += base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
            elif mime_type == "text/html" and not body:
                data = part.get("body", {}).get("data", "")
                if data:
                    body += base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
            elif "parts" in part:
                body += parse_email_body(part)
    else:
        # Single part email
        data = payload.get("body", {}).get("data", "")
        if data:
            body = base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
            
    return body.strip()

def fetch_new_emails():
    """Polls Gmail for recent messages and registers them in the CRM database."""
    service = get_gmail_service()
    if not service:
        logger.info("Gmail service not available (not authenticated or configured).")
        return 0
        
    try:
        # Fetch unread messages in inbox
        results = service.users().messages().list(userId="me", q="is:unread label:INBOX", maxResults=20).execute()
        messages = results.get("messages", [])
        
        imported_count = 0
        for msg in messages:
            msg_id = msg["id"]
            
            # Check if we already imported this message to avoid double-processing
            with database.get_db() as conn:
                existing = conn.execute("SELECT id FROM messages WHERE external_id = ?;", (msg_id,)).fetchone()
                if existing:
                    continue
            
            # Retrieve full message detail
            full_msg = service.users().messages().get(userId="me", id=msg_id, format="full").execute()
            payload = full_msg.get("payload", {})
            headers = payload.get("headers", [])
            
            # Parse headers
            subject = ""
            sender = ""
            for h in headers:
                if h["name"].lower() == "subject":
                    subject = h["value"]
                elif h["name"].lower() == "from":
                    sender = h["value"]
            
            # Parse Sender details: e.g. "John Doe <john.doe@gmail.com>"
            sender_name = "Gmail Contact"
            sender_email = sender
            if "<" in sender and ">" in sender:
                parts = sender.split("<")
                sender_name = parts[0].strip().strip('"')
                sender_email = parts[1].split(">")[0].strip()
                
            body = parse_email_body(payload)
            if not body:
                body = f"[Subject: {subject}] (No readable plain text body)"
            else:
                body = f"Subject: {subject}\n\n{body}"
                
            # Get or create conversation in SQLite
            conv_id = database.get_or_create_conversation_by_channel("gmail", sender_email, sender_name)
            
            # Create message in database
            database.create_message(
                conversation_id=conv_id,
                sender_type="contact",
                channel_type="gmail",
                content=body,
                external_id=msg_id,
                status="read"
            )
            
            # Mark the message as read in Gmail (or remove UNREAD label) so we don't fetch it next time
            service.users().messages().modify(
                userId="me",
                id=msg_id,
                body={"removeLabelIds": ["UNREAD"]}
            ).execute()
            
            imported_count += 1
            
        return imported_count
    except Exception as e:
        logger.error(f"Error fetching emails from Gmail: {e}")
        return 0

def send_gmail_reply(conversation_id, content):
    """Composes and sends an email via Gmail API and records it locally."""
    service = get_gmail_service()
    
    # Retrieve contact email
    convs = database.get_conversations()
    target_conv = None
    for c in convs:
        if c["conversation_id"] == conversation_id:
            target_conv = c
            break
            
    if not target_conv or not target_conv["contact_email"]:
        raise ValueError("Invalid conversation ID or contact does not have a registered email.")
        
    recipient_email = target_conv["contact_email"]
    recipient_name = target_conv["contact_name"]
    
    # If service is offline, return false so the controller knows to throw an error/mock it
    if not service:
        logger.warning("Cannot send mail: Gmail API service is not authenticated.")
        return False
        
    try:
        # Create MIME message
        message = MIMEText(content)
        message["to"] = f"{recipient_name} <{recipient_email}>"
        message["from"] = "me"
        message["subject"] = f"Re: QariCrm Followup"
        
        # Encode message
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
        
        # Send mail via API
        sent_msg = service.users().messages().send(userId="me", body={"raw": raw}).execute()
        
        # Log message in DB
        database.create_message(
            conversation_id=conversation_id,
            sender_type="user",
            channel_type="gmail",
            content=content,
            external_id=sent_msg.get("id"),
            status="sent"
        )
        return True
    except Exception as e:
        logger.error(f"Error sending email through Gmail API: {e}")
        raise e
