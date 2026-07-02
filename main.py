import asyncio
import json
import logging
import random
from starlette.applications import Starlette
from starlette.responses import JSONResponse, RedirectResponse, PlainTextResponse, Response
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

import database
import gmail_client
import meta_client
import config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Active Server-Sent Events clients
sse_queues = set()

# Initialize DB on start
database.init_db()

# Custom queues for dispatching events to browser client
async def broadcast_event(event_type, data):
    payload = {"type": event_type, "data": data}
    for q in list(sse_queues):
        try:
            await q.put(payload)
        except Exception as e:
            logger.error(f"Error putting event in client queue: {e}")

# ==========================================
# API ENDPOINTS
# ==========================================

async def get_contacts(request):
    contacts = database.get_contacts()
    return JSONResponse(contacts)

async def create_contact(request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON payload"}, status_code=400)
        
    name = body.get("name")
    if not name:
        return JSONResponse({"error": "Name field is required"}, status_code=400)
        
    email = body.get("email")
    phone = body.get("phone")
    status = body.get("status", "lead")
    
    contact_id = database.create_contact(name, email, phone, status=status)
    contact = database.get_contact_by_id(contact_id)
    
    # Broadcast update
    await broadcast_event("contact_created", contact)
    return JSONResponse(contact)

async def get_conversations(request):
    conversations = database.get_conversations()
    return JSONResponse(conversations)

async def get_messages(request):
    conv_id = int(request.path_params["id"])
    messages = database.get_messages(conv_id)
    return JSONResponse(messages)

async def send_message(request):
    conv_id = int(request.path_params["id"])
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON"}, status_code=400)
        
    content = body.get("content", "").strip()
    if not content:
        return JSONResponse({"error": "Content cannot be empty"}, status_code=400)
        
    # Get last message to determine the channel type
    messages = database.get_messages(conv_id)
    channel_type = "whatsapp" # default fallback
    if messages:
        channel_type = messages[-1]["channel_type"]
        
    # Check if simulator is enabled
    simulator_enabled = database.get_setting("simulator_enabled") == "1"
    
    # Attempt real API call if simulator is disabled
    api_sent = False
    if not simulator_enabled:
        if channel_type == "gmail":
            api_sent = gmail_client.send_gmail_reply(conv_id, content)
        elif channel_type in ["whatsapp", "messenger", "instagram"]:
            api_sent = meta_client.send_meta_message(conv_id, channel_type, content)
            
    # If API call was skipped or returned false, execute in mock/local mode
    if simulator_enabled or not api_sent:
        logger.info(f"Using Simulator/Local mode to dispatch message to conv {conv_id} on {channel_type}")
        msg_id = database.create_message(
            conversation_id=conv_id,
            sender_type="user",
            channel_type=channel_type,
            content=content,
            status="sent"
        )
        
        # Broadcast user reply to frontend
        with database.get_db() as conn:
            row = conn.execute("SELECT * FROM messages WHERE id = ?;", (msg_id,)).fetchone()
            msg_dict = dict(row)
            
        await broadcast_event("message_received", msg_dict)
        
        # Trigger simulated customer reply in background after 3 seconds
        asyncio.create_task(simulate_incoming_reply(conv_id, channel_type, content))
        return JSONResponse({"status": "success", "mode": "simulator", "message_id": msg_id})
        
    # Real message successfully sent
    # Get latest message
    messages = database.get_messages(conv_id)
    latest_msg = messages[-1] if messages else {}
    await broadcast_event("message_received", latest_msg)
    return JSONResponse({"status": "success", "mode": "production", "message": latest_msg})

async def get_ai_draft(request):
    conv_id = int(request.path_params["id"])
    messages = database.get_messages(conv_id)
    
    # Get last few messages for context
    context = ""
    for m in messages[-6:]:
        sender = "Customer" if m["sender_type"] == "contact" else "Agent"
        context += f"{sender}: {m['content']}\n"
        
    gemini_key = database.get_setting("gemini_api_key", "")
    draft = ""
    
    if gemini_key:
        try:
            from google import genai
            client = genai.Client(api_key=gemini_key)
            prompt = (
                "You are an AI sales assistant built into a unified CRM called QariCrm.\n"
                "Review the following conversation history between the customer and our agent, "
                "and draft a professional, friendly response from the agent.\n"
                "Keep the response concise, clear, and relevant. Do not include subject lines or greetings if unnecessary, "
                "just draft the direct reply.\n\n"
                f"Conversation History:\n{context}\n\n"
                "Agent Draft:"
            )
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )
            draft = response.text.strip()
        except Exception as e:
            logger.error(f"Gemini API generation failed: {e}")
            draft = ""
            
    # Fallback to local rule-based smart responses if API fails or is not configured
    if not draft:
        last_customer_message = ""
        for m in reversed(messages):
            if m["sender_type"] == "contact":
                last_customer_message = m["content"].lower()
                break
                
        # Handle English & Arabic queries
        if any(w in last_customer_message for w in ["pricing", "price", "enterprise", "سعر", "أسعار"]):
            draft = (
                "Hi there! Thanks for asking about our pricing. We offer standard plans starting at $29/user/month, "
                "and custom enterprise packages with dedicated support. Would you like me to send over our full brochure or schedule a quick 10-minute demo?"
            )
        elif any(w in last_customer_message for w in ["zoom", "call", "meeting", "اتصال", "اجتماع"]):
            draft = (
                "Hi! I'd be happy to jump on a call with you. You can pick a time that works best for you here: "
                "https://calendly.com/qaricrm/demo. Looking forward to speaking with you!"
            )
        elif any(w in last_customer_message for w in ["setup", "integration", "database", "تثبيت", "ربط"]):
            draft = (
                "Hello! Our CRM supports standard integration hooks and webhooks to sync with external databases. "
                "I can send you our API documentation, or we can connect you with one of our integration engineers to help you set it up. What works best?"
            )
        elif any(w in last_customer_message for w in ["thanks", "thank you", "great", "شكرا", "شكرًا"]):
            draft = (
                "You're very welcome! If you have any other questions, feel free to reach out anytime. Have a wonderful day!"
            )
        else:
            draft = (
                "Hi! Thanks for reaching out. I've received your message and would love to help. Could you provide a bit more detail, "
                "or shall we set up a quick call to discuss?"
            )
            
    return JSONResponse({"draft": draft})

async def get_deals(request):
    deals = database.get_deals()
    return JSONResponse(deals)

async def create_deal(request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON"}, status_code=400)
        
    contact_id = body.get("contact_id")
    name = body.get("name")
    value = body.get("value")
    stage = body.get("stage", "lead")
    
    if not contact_id or not name or value is None:
        return JSONResponse({"error": "contact_id, name, and value are required"}, status_code=400)
        
    deal_id = database.create_deal(contact_id, name, value, stage)
    
    # Fetch enriched deal
    with database.get_db() as conn:
        row = conn.execute("""
            SELECT d.id as deal_id, d.name as deal_name, d.value as deal_value, d.stage as deal_stage,
                   d.contact_id, c.name as contact_name, c.avatar as contact_avatar
            FROM deals d JOIN contacts c ON d.contact_id = c.id WHERE d.id = ?;""", (deal_id,)).fetchone()
        deal_dict = dict(row)
        
    await broadcast_event("deal_updated", deal_dict)
    return JSONResponse(deal_dict)

async def update_deal_stage(request):
    deal_id = int(request.path_params["id"])
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON"}, status_code=400)
        
    stage = body.get("stage")
    if not stage:
        return JSONResponse({"error": "stage field is required"}, status_code=400)
        
    database.update_deal_stage(deal_id, stage)
    
    with database.get_db() as conn:
        row = conn.execute("""
            SELECT d.id as deal_id, d.name as deal_name, d.value as deal_value, d.stage as deal_stage,
                   d.contact_id, c.name as contact_name, c.avatar as contact_avatar
            FROM deals d JOIN contacts c ON d.contact_id = c.id WHERE d.id = ?;""", (deal_id,)).fetchone()
        deal_dict = dict(row)
        
    await broadcast_event("deal_updated", deal_dict)
    return JSONResponse(deal_dict)

async def get_settings(request):
    settings = database.get_all_settings()
    # Mask secrets for safety
    masked = {}
    for k, v in settings.items():
        if k in ["google_client_secret", "meta_page_access_token", "meta_whatsapp_access_token", "gmail_credentials"] and v:
            masked[k] = "••••••••••••••••"
        else:
            masked[k] = v
    return JSONResponse(masked)

async def save_settings(request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON"}, status_code=400)
        
    # Filter out masked entries to avoid overwriting real secrets with dots
    to_save = {}
    for k, v in body.items():
        if v == "••••••••••••••••":
            continue
        to_save[k] = v
        
    database.save_settings(to_save)
    return JSONResponse({"status": "success", "message": "Settings updated successfully."})

# ==========================================
# GMAIL OAUTH ENDPOINTS
# ==========================================

async def gmail_auth_redirect(request):
    auth_url = gmail_client.get_auth_url()
    if not auth_url:
        return RedirectResponse("/#settings?error=gmail_not_configured")
    return RedirectResponse(auth_url)

async def gmail_auth_callback(request):
    code = request.query_params.get("code")
    if not code:
        return PlainTextResponse("Authorization code not found in request.", status_code=400)
        
    success = gmail_client.exchange_code_for_credentials(code)
    if success:
        # Redirect back to the CRM settings panel (served statically at /#settings)
        return RedirectResponse("/#settings?gmail=connected")
    return PlainTextResponse("OAuth exchange failed. Check console logs.", status_code=500)

# ==========================================
# META WEBHOOK ENDPOINTS
# ==========================================

async def meta_webhook(request):
    if request.method == "GET":
        # Verification Flow
        params = request.query_params
        mode = params.get("hub.mode")
        token = params.get("hub.verify_token")
        challenge = params.get("hub.challenge")
        
        verified = meta_client.verify_webhook(mode, token, challenge)
        if verified:
            return PlainTextResponse(verified)
        return Response("Verification failed", status_code=403)
        
    elif request.method == "POST":
        # Inbound Message Flow
        try:
            payload = await request.json()
        except Exception:
            return JSONResponse({"error": "Invalid payload"}, status_code=400)
            
        # Parse payload asynchronously and register message
        processed = meta_client.process_webhook_payload(payload)
        if processed:
            # Fetch latest conversations state and broadcast to UI
            # For simplicity, we trigger client reload or broadcast message event
            # We can find the conversation that updated
            conversations = database.get_conversations()
            await broadcast_event("conversations_updated", conversations)
            
        return Response("EVENT_RECEIVED", status_code=200)

# ==========================================
# REAL-TIME BROADCAST STREAM (SSE)
# ==========================================

async def sse_endpoint(request):
    async def event_generator():
        queue = asyncio.Queue()
        sse_queues.add(queue)
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    # Non-blocking check for new broadcasts, timeout helps verify socket state
                    event = await asyncio.wait_for(queue.get(), timeout=12.0)
                    yield {
                        "event": event["type"],
                        "data": json.dumps(event["data"])
                    }
                except asyncio.TimeoutError:
                    # Send keepalive ping to maintain connection
                    yield {
                        "event": "ping",
                        "data": "keep-alive"
                    }
        finally:
            sse_queues.remove(queue)
            
    return EventSourceResponse(event_generator())

# ==========================================
# MOCK CONVERSATION SIMULATOR SYSTEM
# ==========================================

async def toggle_simulator(request):
    try:
        body = await request.json()
        enabled = body.get("enabled", True)
    except Exception:
        enabled = True
        
    database.save_settings({"simulator_enabled": "1" if enabled else "0"})
    return JSONResponse({"status": "success", "simulator_enabled": enabled})

async def trigger_simulated_message(request):
    """Manually spawns an incoming message from a chosen contact and channel."""
    try:
        body = await request.json()
    except Exception:
        body = {}
        
    channel = body.get("channel", random.choice(["whatsapp", "gmail", "messenger", "instagram"]))
    
    # Pick a random contact
    contacts = database.get_contacts()
    if not contacts:
        # Create a fallback contact
        database.create_contact("Test Lead", "test.lead@crm.com", "+15551000", status="lead")
        contacts = database.get_contacts()
        
    contact = random.choice(contacts)
    
    # Generate mock message body
    content_pool = [
        "Hey! Just checking in on that proposal we discussed.",
        "Could you send me your pricing options again?",
        "Hi, are you available for a brief Zoom meeting tomorrow?",
        "Hello, I ran into an issue with the setup. Is there a manual I can read?",
        "Awesome product! Do you have any discounts for non-profits?"
    ]
    content = random.choice(content_pool)
    if channel == "gmail":
        content = f"Subject: Inquiry regarding services\n\n{content}"
        
    # Resolve or create conversation
    identifier = contact["email"] if channel == "gmail" else contact["phone"]
    if not identifier:
        identifier = f"sim_{contact['id']}"
        
    conv_id = database.get_or_create_conversation_by_channel(channel, identifier, contact["name"])
    
    msg_id = database.create_message(
        conversation_id=conv_id,
        sender_type="contact",
        channel_type=channel,
        content=content,
        status="read"
    )
    
    # Broadcast to frontend
    with database.get_db() as conn:
        row = conn.execute("SELECT * FROM messages WHERE id = ?;", (msg_id,)).fetchone()
        msg_dict = dict(row)
        
    await broadcast_event("message_received", msg_dict)
    
    # Update conversations preview
    conversations = database.get_conversations()
    await broadcast_event("conversations_updated", conversations)
    
    return JSONResponse({"status": "success", "message": msg_dict})

async def simulate_incoming_reply(conversation_id, channel_type, user_content):
    """Simulates a customer reply 3 seconds after an agent answers."""
    await asyncio.sleep(3.0)
    
    reply_pool = [
        "That works for me! Thanks for the prompt reply.",
        "Perfect, I'll review it and get back to you.",
        "Got it, let's schedule a Zoom call to discuss this in detail.",
        "Appreciate the support. I'll let the team know.",
        "Thanks! Looking forward to working together."
    ]
    reply_content = random.choice(reply_pool)
    if channel_type == "gmail":
        reply_content = f"Subject: Re: QariCrm Followup\n\n{reply_content}"
        
    msg_id = database.create_message(
        conversation_id=conversation_id,
        sender_type="contact",
        channel_type=channel_type,
        content=reply_content,
        status="read"
    )
    
    # Broadcast to UI
    with database.get_db() as conn:
        row = conn.execute("SELECT * FROM messages WHERE id = ?;", (msg_id,)).fetchone()
        msg_dict = dict(row)
        
    await broadcast_event("message_received", msg_dict)
    
    # Update conversations preview
    conversations = database.get_conversations()
    await broadcast_event("conversations_updated", conversations)

async def simulator_background_loop():
    """Background task that polls Gmail and periodically spawns random conversations."""
    logger.info("Simulator and Poller background loop started.")
    while True:
        try:
            # 1. Periodically fetch real emails from Gmail API if credentials exist
            gmail_client.fetch_new_emails()
            
            # 2. Simulate random customer messages if Simulator Mode is toggled
            is_enabled = database.get_setting("simulator_enabled") == "1"
            if is_enabled:
                # 30% chance to spawn a message each interval to make it feel natural
                if random.random() < 0.35:
                    logger.info("Spawning random simulated incoming message...")
                    
                    channel = random.choice(["whatsapp", "gmail", "messenger", "instagram"])
                    contacts = database.get_contacts()
                    
                    if contacts:
                        contact = random.choice(contacts)
                        identifier = contact["email"] if channel == "gmail" else contact["phone"]
                        if not identifier:
                            identifier = f"sim_{contact['id']}"
                            
                        # Content pool
                        content_pool = [
                            "Hey! Just looking for an update on my ticket.",
                            "Hello, do you support international payments?",
                            "Quick question: are contracts monthly or annual?",
                            "Could we jump on a call sometime later today?",
                            "Awesome dashboard! How long does it take to deploy?"
                        ]
                        content = random.choice(content_pool)
                        if channel == "gmail":
                            content = f"Subject: Customer Question\n\n{content}"
                            
                        conv_id = database.get_or_create_conversation_by_channel(channel, identifier, contact["name"])
                        msg_id = database.create_message(
                            conversation_id=conv_id,
                            sender_type="contact",
                            channel_type=channel,
                            content=content,
                            status="read"
                        )
                        
                        # Broadcast
                        with database.get_db() as conn:
                            row = conn.execute("SELECT * FROM messages WHERE id = ?;", (msg_id,)).fetchone()
                            msg_dict = dict(row)
                            
                        await broadcast_event("message_received", msg_dict)
                        
                        # Update conversation panels
                        conversations = database.get_conversations()
                        await broadcast_event("conversations_updated", conversations)
            
        except Exception as e:
            logger.error(f"Error in background simulator loop: {e}")
            
        # Sleep for interval
        interval = int(database.get_setting("simulator_interval_seconds", config.SIMULATOR_INTERVAL_SECONDS))
        await asyncio.sleep(interval)


# ==========================================
# APP LIFECYCLE
# ==========================================

async def handle_startup():
    # Start the background simulator / Gmail polling loop
    asyncio.create_task(simulator_background_loop())
    logger.info("Startup sequence finished.")

async def handle_shutdown():
    logger.info("Shutdown sequence finished.")

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app):
    await handle_startup()
    yield
    await handle_shutdown()

# Route mappings
routes = [
    Route("/api/contacts", get_contacts, methods=["GET"]),
    Route("/api/contacts", create_contact, methods=["POST"]),
    Route("/api/conversations", get_conversations, methods=["GET"]),
    Route("/api/conversations/{id:int}/messages", get_messages, methods=["GET"]),
    Route("/api/conversations/{id:int}/messages", send_message, methods=["POST"]),
    Route("/api/conversations/{id:int}/ai-draft", get_ai_draft, methods=["POST"]),
    Route("/api/deals", get_deals, methods=["GET"]),
    Route("/api/deals", create_deal, methods=["POST"]),
    Route("/api/deals/{id:int}/stage", update_deal_stage, methods=["PUT"]),
    Route("/api/settings", get_settings, methods=["GET"]),
    Route("/api/settings", save_settings, methods=["POST"]),
    Route("/api/auth/gmail", gmail_auth_redirect, methods=["GET"]),
    Route("/api/auth/gmail/callback", gmail_auth_callback, methods=["GET"]),
    Route("/api/webhooks/meta", meta_webhook, methods=["GET", "POST"]),
    Route("/api/stream", sse_endpoint, methods=["GET"]),
    Route("/api/simulator/toggle", toggle_simulator, methods=["POST"]),
    Route("/api/simulator/trigger", trigger_simulated_message, methods=["POST"]),
    # Serve Frontend SPA
    Mount("/", app=StaticFiles(directory="static", html=True), name="static")
]

app = Starlette(
    routes=routes,
    lifespan=lifespan
)

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting QariCrm server on http://{config.HOST}:{config.PORT}...")
    uvicorn.run("main:app", host=config.HOST, port=config.PORT, reload=True)
