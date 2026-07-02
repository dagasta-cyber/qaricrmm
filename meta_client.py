import logging
import requests
import database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GRAPH_API_VERSION = "v19.0"
GRAPH_API_URL = "https://graph.facebook.com"

def verify_webhook(mode, token, challenge):
    """Verifies the webhook token sent by Meta during verification phase."""
    saved_token = database.get_setting("meta_verify_token", "qari_crm_verify_token")
    if mode == "subscribe" and token == saved_token:
        logger.info("Meta Webhook verified successfully.")
        return challenge
    logger.warning("Meta Webhook verification failed. Token mismatch.")
    return None

def process_webhook_payload(payload):
    """
    Parses incoming webhook payload from Meta.
    Supports: Messenger ('page' object), Instagram DMs ('instagram' object), and WhatsApp ('whatsapp_business_account' object).
    """
    obj = payload.get("object")
    
    if obj == "page":
        # Messenger webhook
        return parse_messenger_payload(payload)
    elif obj == "instagram":
        # Instagram DM webhook
        return parse_instagram_payload(payload)
    elif obj == "whatsapp_business_account":
        # WhatsApp Webhook
        return parse_whatsapp_payload(payload)
    else:
        logger.warning(f"Unsupported Meta Webhook object: {obj}")
        return False

def parse_messenger_payload(payload):
    """Extracts message, sender PSID, and registers message in DB for Facebook Messenger."""
    entries = payload.get("entry", [])
    processed = False
    
    for entry in entries:
        messaging_events = entry.get("messaging", [])
        for event in messaging_events:
            sender_id = event.get("sender", {}).get("id")
            message = event.get("message", {})
            text = message.get("text")
            message_id = message.get("mid")
            
            # Skip echoes (messages sent by our own page) or empty messages
            if not text or message.get("is_echo"):
                continue
                
            logger.info(f"Incoming Messenger message from {sender_id}: {text}")
            
            # Resolve or create conversation
            # For Messenger/Instagram, we check if we can get contact info from Meta Graph API
            contact_name = get_meta_profile_name(sender_id, "messenger")
            conv_id = database.get_or_create_conversation_by_channel("messenger", sender_id, contact_name)
            
            # Create message in SQLite
            database.create_message(
                conversation_id=conv_id,
                sender_type="contact",
                channel_type="messenger",
                content=text,
                external_id=message_id,
                status="read"
            )
            processed = True
            
    return processed

def parse_instagram_payload(payload):
    """Extracts message, sender IGSID, and registers message in DB for Instagram DMs."""
    entries = payload.get("entry", [])
    processed = False
    
    for entry in entries:
        messaging_events = entry.get("messaging", [])
        for event in messaging_events:
            sender_id = event.get("sender", {}).get("id")
            message = event.get("message", {})
            text = message.get("text")
            message_id = message.get("mid")
            
            # Skip echoes or empty messages
            if not text or message.get("is_echo"):
                continue
                
            logger.info(f"Incoming Instagram message from {sender_id}: {text}")
            
            contact_name = get_meta_profile_name(sender_id, "instagram")
            conv_id = database.get_or_create_conversation_by_channel("instagram", sender_id, contact_name)
            
            database.create_message(
                conversation_id=conv_id,
                sender_type="contact",
                channel_type="instagram",
                content=text,
                external_id=message_id,
                status="read"
            )
            processed = True
            
    return processed

def parse_whatsapp_payload(payload):
    """Extracts WhatsApp messages and sender contact info and registers in DB."""
    entries = payload.get("entry", [])
    processed = False
    
    for entry in entries:
        changes = entry.get("changes", [])
        for change in changes:
            value = change.get("value", {})
            if "messages" in value:
                metadata = value.get("metadata", {})
                phone_id = metadata.get("phone_number_id")
                
                # Fetch profile names from contacts array in payload
                contacts_info = value.get("contacts", [])
                profile_name = "WhatsApp User"
                if contacts_info:
                    profile_name = contacts_info[0].get("profile", {}).get("name", profile_name)
                
                messages_events = value.get("messages", [])
                for msg in messages_events:
                    sender_phone = msg.get("from") # E.g. "15550100"
                    message_id = msg.get("id")
                    msg_type = msg.get("type")
                    
                    text = ""
                    if msg_type == "text":
                        text = msg.get("text", {}).get("body", "")
                    elif msg_type == "button":
                        text = msg.get("button", {}).get("text", "")
                    else:
                        text = f"[{msg_type.upper()} message received]"
                        
                    if not text:
                        continue
                        
                    logger.info(f"Incoming WhatsApp message from {sender_phone}: {text}")
                    
                    # Create or resolve conversation
                    conv_id = database.get_or_create_conversation_by_channel("whatsapp", f"+{sender_phone}", profile_name)
                    
                    # Register message
                    database.create_message(
                        conversation_id=conv_id,
                        sender_type="contact",
                        channel_type="whatsapp",
                        content=text,
                        external_id=message_id,
                        status="read"
                    )
                    processed = True
                    
    return processed

def get_meta_profile_name(scoped_id, channel_type):
    """Queries Meta Graph API to fetch sender's profile name if available."""
    token = database.get_setting("meta_page_access_token")
    if not token:
        return f"New {channel_type.capitalize()} Contact"
        
    try:
        url = f"{GRAPH_API_URL}/{GRAPH_API_VERSION}/{scoped_id}"
        params = {"fields": "first_name,last_name", "access_token": token}
        
        # Instagram profiles use different fields or endpoint depending on API
        if channel_type == "instagram":
            params = {"fields": "username", "access_token": token}
            
        r = requests.get(url, params=params, timeout=5)
        if r.status_code == 200:
            data = r.json()
            if channel_type == "instagram":
                return data.get("username", "Instagram Contact")
            return f"{data.get('first_name', '')} {data.get('last_name', '')}".strip()
    except Exception as e:
        logger.error(f"Error fetching Meta profile: {e}")
        
    return f"New {channel_type.capitalize()} Contact"

def send_meta_message(conversation_id, channel_type, content):
    """Dispatches a response back to the user via Meta Messenger, Instagram, or WhatsApp."""
    
    # Retrieve target contact platform ID details
    with database.get_db() as conn:
        c_row = conn.execute(
            """SELECT co.phone, co.email, co.name, co.facebook_psid, co.instagram_igsid 
               FROM conversations c 
               JOIN contacts co ON c.contact_id = co.id 
               WHERE c.id = ?;""",
            (conversation_id,)
        ).fetchone()
        
    if not c_row:
        logger.error(f"Conversation not found for ID: {conversation_id}")
        return False
        
    recipient_name = c_row["name"]
    recipient_phone = c_row["phone"]

    # Retrieve tokens from database settings
    page_access_token = database.get_setting("meta_page_access_token")
    wa_phone_number_id = database.get_setting("meta_whatsapp_phone_number_id")
    wa_access_token = database.get_setting("meta_whatsapp_access_token")
    
    try:
        if channel_type in ["messenger", "instagram"]:
            if not page_access_token:
                logger.warning(f"Cannot send Meta {channel_type} message: Access token not configured.")
                return False
                
            # Expose the correct Page-Scoped User ID (PSID) or Instagram-Scoped ID (IGSID)
            target_id = c_row["facebook_psid"] if channel_type == "messenger" else c_row["instagram_igsid"]
            if not target_id:
                logger.error(f"Cannot send {channel_type} message: Contact does not have a registered scoped {channel_type} ID.")
                return False
                
            url = f"{GRAPH_API_URL}/{GRAPH_API_VERSION}/me/messages"
            params = {"access_token": page_access_token}
            payload = {
                "recipient": {"id": target_id},
                "message": {"text": content}
            }
            
            r = requests.post(url, params=params, json=payload, timeout=8)
            r.raise_for_status()
            res_data = r.json()
            msg_id = res_data.get("message_id")
            
        elif channel_type == "whatsapp":
            if not wa_phone_number_id or not wa_access_token:
                logger.warning("Cannot send WhatsApp message: Phone ID or Access Token not configured.")
                return False
                
            clean_phone = recipient_phone.replace("+", "").replace(" ", "").strip() if recipient_phone else None
            if not clean_phone:
                logger.error("Cannot send WhatsApp message: Contact does not have a phone number.")
                return False
                
            url = f"{GRAPH_API_URL}/{GRAPH_API_VERSION}/{wa_phone_number_id}/messages"
            headers = {"Authorization": f"Bearer {wa_access_token}"}
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": clean_phone,
                "type": "text",
                "text": {"body": content}
            }
            
            r = requests.post(url, headers=headers, json=payload, timeout=8)
            r.raise_for_status()
            res_data = r.json()
            msg_id = res_data.get("messages", [{}])[0].get("id")
            
        else:
            logger.error(f"Invalid channel type for Meta dispatch: {channel_type}")
            return False
            
        # Log successful message in DB
        database.create_message(
            conversation_id=conversation_id,
            sender_type="user",
            channel_type=channel_type,
            content=content,
            external_id=msg_id,
            status="sent"
        )
        return True
        
    except Exception as e:
        logger.error(f"Error calling Meta Graph API for {channel_type}: {e}")
        return False
