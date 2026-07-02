import sqlite3
import os
from contextlib import contextmanager
import config

# Helper context manager for database connections
@contextmanager
def get_db():
    conn = sqlite3.connect(config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def init_db():
    """Initializes the SQLite database schemas and seeds it with default data if empty."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 1. Contacts Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            avatar TEXT,
            status TEXT DEFAULT 'lead',
            facebook_psid TEXT,
            instagram_igsid TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # 2. Conversations Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id INTEGER NOT NULL,
            last_message_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_message_preview TEXT,
            FOREIGN KEY(contact_id) REFERENCES contacts(id) ON DELETE CASCADE
        );
        """)
        
        # 3. Messages Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            sender_type TEXT NOT NULL,
            channel_type TEXT NOT NULL,
            content TEXT NOT NULL,
            external_id TEXT,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'sent',
            FOREIGN KEY(conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
        );
        """)
        
        # 4. Deals Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS deals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            value REAL NOT NULL,
            stage TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(contact_id) REFERENCES contacts(id) ON DELETE CASCADE
        );
        """)
        
        # 5. Settings Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        );
        """)
        
        # Seed default data if database is brand new and contacts are empty
        cursor.execute("SELECT COUNT(*) FROM contacts;")
        if cursor.fetchone()[0] == 0:
            seed_data(cursor)

def seed_data(cursor):
    """Populates the database with initial mock contacts, messages, and deals."""
    # Insert Settings defaults
    settings = [
        ("simulator_enabled", "1"),
        ("google_client_id", config.GOOGLE_CLIENT_ID),
        ("google_client_secret", config.GOOGLE_CLIENT_SECRET),
        ("google_redirect_uri", config.GOOGLE_REDIRECT_URI),
        ("meta_verify_token", config.META_VERIFY_TOKEN),
        ("meta_page_access_token", config.META_PAGE_ACCESS_TOKEN),
        ("meta_whatsapp_phone_number_id", config.META_WHATSAPP_PHONE_NUMBER_ID),
        ("meta_whatsapp_access_token", config.META_WHATSAPP_ACCESS_TOKEN)
    ]
    cursor.executemany("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?);", settings)
    
    # Insert Contacts
    contacts = [
        ("Sarah Jenkins", "sarah.j@enterprise.com", "+14155552671", "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150", "lead", None, None),
        ("Alex Rivera", "alex.r@techcorp.io", "+14155559812", "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150", "contacted", "fb_alex_rivera_psid", None),
        ("Liam Chen", "liam.chen@creative.agency", "+14155553049", "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150", "customer", None, "ig_liam_chen_igsid")
    ]
    
    contact_ids = []
    for name, email, phone, avatar, status, psid, igsid in contacts:
        cursor.execute(
            """INSERT INTO contacts (name, email, phone, avatar, status, facebook_psid, instagram_igsid) 
               VALUES (?, ?, ?, ?, ?, ?, ?);""",
            (name, email, phone, avatar, status, psid, igsid)
        )
        contact_ids.append(cursor.lastrowid)
        
    # Insert Conversations
    # Sarah Jenkins: Gmail
    cursor.execute(
        "INSERT INTO conversations (contact_id, last_message_preview, last_message_at) VALUES (?, ?, datetime('now', '-30 minutes'));",
        (contact_ids[0], "Hi Qari CRM Team, I saw your pricing page and wanted to check if you offer enterprise rates?")
    )
    conv1_id = cursor.lastrowid
    
    # Alex Rivera: WhatsApp
    cursor.execute(
        "INSERT INTO conversations (contact_id, last_message_preview, last_message_at) VALUES (?, ?, datetime('now', '-10 minutes'));",
        (contact_ids[1], "Perfect, that setup makes total sense. I will discuss it with the team and get back to you shortly.")
    )
    conv2_id = cursor.lastrowid
    
    # Liam Chen: Instagram
    cursor.execute(
        "INSERT INTO conversations (contact_id, last_message_preview, last_message_at) VALUES (?, ?, datetime('now', '-2 hours'));",
        (contact_ids[2], "Great! Let's get the contract signed this afternoon.")
    )
    conv3_id = cursor.lastrowid
    
    # Insert Messages
    # Sarah Jenkins Messages
    cursor.execute(
        "INSERT INTO messages (conversation_id, sender_type, channel_type, content, sent_at, status) VALUES (?, 'contact', 'gmail', ?, datetime('now', '-30 minutes'), 'read');",
        (conv1_id, "Hi Qari CRM Team, I saw your pricing page and wanted to check if you offer enterprise rates?")
    )
    
    # Alex Rivera Messages
    cursor.execute(
        "INSERT INTO messages (conversation_id, sender_type, channel_type, content, sent_at, status) VALUES (?, 'contact', 'whatsapp', ?, datetime('now', '-25 minutes'), 'read');",
        (conv2_id, "Hello! I am trying to figure out if your system integrates with our current database setup.")
    )
    cursor.execute(
        "INSERT INTO messages (conversation_id, sender_type, channel_type, content, sent_at, status) VALUES (?, 'user', 'whatsapp', ?, datetime('now', '-18 minutes'), 'read');",
        (conv2_id, "Hi Alex! Yes, we have a fully open API and can map custom payloads to your database endpoints directly.")
    )
    cursor.execute(
        "INSERT INTO messages (conversation_id, sender_type, channel_type, content, sent_at, status) VALUES (?, 'contact', 'whatsapp', ?, datetime('now', '-10 minutes'), 'read');",
        (conv2_id, "Perfect, that setup makes total sense. I will discuss it with the team and get back to you shortly.")
    )
    
    # Liam Chen Messages
    cursor.execute(
        "INSERT INTO messages (conversation_id, sender_type, channel_type, content, sent_at, status) VALUES (?, 'contact', 'instagram', ?, datetime('now', '-3 hours'), 'read');",
        (conv3_id, "Hey! Can we configure custom roles for Instagram operators?")
    )
    cursor.execute(
        "INSERT INTO messages (conversation_id, sender_type, channel_type, content, sent_at, status) VALUES (?, 'user', 'instagram', ?, datetime('now', '-2 hours', '-30 minutes'), 'read');",
        (conv3_id, "Absolutely. You can assign different permissions to your agents in the dashboard settings.")
    )
    cursor.execute(
        "INSERT INTO messages (conversation_id, sender_type, channel_type, content, sent_at, status) VALUES (?, 'contact', 'instagram', ?, datetime('now', '-2 hours'), 'read');",
        (conv3_id, "Great! Let's get the contract signed this afternoon.")
    )
    
    # Insert Deals
    deals = [
        (contact_ids[0], "Sarah Jenkins - Enterprise SaaS", 5200.0, "lead"),
        (contact_ids[1], "Alex Rivera - Database Setup Project", 3100.0, "proposal"),
        (contact_ids[2], "Liam Chen - Custom Branding Campaign", 7800.0, "won")
    ]
    cursor.executemany("INSERT INTO deals (contact_id, name, value, stage) VALUES (?, ?, ?, ?);", deals)


# ==========================================
# SETTINGS CRUD HELPERS
# ==========================================

def get_setting(key, default=None):
    """Retrieves a setting value, falling back to config file constants."""
    with get_db() as conn:
        row = conn.execute("SELECT value FROM settings WHERE key = ?;", (key,)).fetchone()
        if row:
            return row["value"]
    
    # Fallback to config.py constants
    env_key = key.upper()
    return getattr(config, env_key, default)

def get_all_settings():
    """Gets all settings as a dict."""
    with get_db() as conn:
        rows = conn.execute("SELECT key, value FROM settings;").fetchall()
        settings_dict = {row["key"]: row["value"] for row in rows}
    
    # Populate missing settings from config defaults
    expected_keys = [
        "simulator_enabled", "google_client_id", "google_client_secret",
        "google_redirect_uri", "meta_verify_token", "meta_page_access_token",
        "meta_whatsapp_phone_number_id", "meta_whatsapp_access_token",
        "gemini_api_key"
    ]
    for k in expected_keys:
        if k not in settings_dict:
            settings_dict[k] = get_setting(k, "")
            
    return settings_dict

def save_settings(settings_dict):
    """Updates settings in bulk."""
    with get_db() as conn:
        for k, v in settings_dict.items():
            conn.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?);",
                (k, str(v))
            )


# ==========================================
# CONTACTS CRUD HELPERS
# ==========================================

def get_contacts():
    """Gets all contacts, sorted alphabetically by name."""
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM contacts ORDER BY name ASC;").fetchall()
        return [dict(r) for r in rows]

def get_contact_by_id(contact_id):
    """Fetches a contact by ID."""
    with get_db() as conn:
        row = conn.execute("SELECT * FROM contacts WHERE id = ?;", (contact_id,)).fetchone()
        return dict(row) if row else None

def create_contact(name, email=None, phone=None, avatar=None, status="lead"):
    """Creates a new contact and an associated conversation thread."""
    if not avatar:
        # Default placeholder avatar from initials/placeholder services
        avatar = f"https://api.dicebear.com/7.x/initials/svg?seed={name.replace(' ', '+')}"
        
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO contacts (name, email, phone, avatar, status) VALUES (?, ?, ?, ?, ?);",
            (name, email, phone, avatar, status)
        )
        contact_id = cursor.lastrowid
        
        # Create conversation row
        cursor.execute(
            "INSERT INTO conversations (contact_id, last_message_preview, last_message_at) VALUES (?, ?, ?);",
            (contact_id, "No messages yet", conn.execute("SELECT datetime('now')").fetchone()[0])
        )
        return contact_id

def update_contact_status(contact_id, status):
    """Updates the contact stage (lead, contacted, customer, etc.)"""
    with get_db() as conn:
        conn.execute(
            "UPDATE contacts SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?;",
            (status, contact_id)
        )


# ==========================================
# CONVERSATIONS & MESSAGES HELPERS
# ==========================================

def get_conversations():
    """Gets all conversations enriched with contact details."""
    query = """
        SELECT 
            c.id as conversation_id,
            c.contact_id,
            co.name as contact_name,
            co.email as contact_email,
            co.phone as contact_phone,
            co.avatar as contact_avatar,
            co.status as contact_status,
            c.last_message_at,
            c.last_message_preview
        FROM conversations c
        JOIN contacts co ON c.contact_id = co.id
        ORDER BY c.last_message_at DESC;
    """
    with get_db() as conn:
        rows = conn.execute(query).fetchall()
        return [dict(r) for r in rows]

def get_messages(conversation_id):
    """Gets all messages for a specific conversation."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM messages WHERE conversation_id = ? ORDER BY sent_at ASC;",
            (conversation_id,)
        ).fetchall()
        return [dict(r) for r in rows]

def create_message(conversation_id, sender_type, channel_type, content, external_id=None, status="sent"):
    """Inserts a new message and updates the corresponding conversation."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO messages (conversation_id, sender_type, channel_type, content, external_id, status)
               VALUES (?, ?, ?, ?, ?, ?);""",
            (conversation_id, sender_type, channel_type, content, external_id, status)
        )
        
        # Update last message details in conversations
        cursor.execute(
            """UPDATE conversations 
               SET last_message_at = CURRENT_TIMESTAMP, last_message_preview = ? 
               WHERE id = ?;""",
            (content[:100], conversation_id)
        )
        
        # Automatically transition 'lead' contacts to 'contacted' when an agent replies
        if sender_type == "user":
            cursor.execute(
                """UPDATE contacts 
                   SET status = 'contacted', updated_at = CURRENT_TIMESTAMP 
                   WHERE id = (SELECT contact_id FROM conversations WHERE id = ?) AND status = 'lead';""",
                (conversation_id,)
            )
            
        return cursor.lastrowid

def get_or_create_conversation_by_channel(channel_type, identifier, contact_name=None):
    """
    Resolves a conversation using platform identifiers.
    - For Gmail: identifier is client email.
    - For Meta: identifier is page-scoped user id (PSID), Instagram id, or WhatsApp phone.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        row = None
        if channel_type == "gmail":
            row = cursor.execute("SELECT id FROM contacts WHERE email = ?;", (identifier,)).fetchone()
        elif channel_type == "messenger":
            row = cursor.execute("SELECT id FROM contacts WHERE facebook_psid = ?;", (identifier,)).fetchone()
        elif channel_type == "instagram":
            row = cursor.execute("SELECT id FROM contacts WHERE instagram_igsid = ?;", (identifier,)).fetchone()
        elif channel_type == "whatsapp":
            clean_id = identifier.replace("+", "").replace(" ", "").strip()
            row = cursor.execute("SELECT id FROM contacts WHERE replace(replace(phone, '+', ''), ' ', '') = ?;", (clean_id,)).fetchone()
            
        if row:
            contact_id = row["id"]
        else:
            name = contact_name or f"New {channel_type.capitalize()} Contact ({identifier[:8]})"
            email = identifier if channel_type == "gmail" else None
            phone = identifier if channel_type == "whatsapp" else None
            psid = identifier if channel_type == "messenger" else None
            igsid = identifier if channel_type == "instagram" else None
            
            cursor.execute(
                """INSERT INTO contacts (name, email, phone, facebook_psid, instagram_igsid, status) 
                   VALUES (?, ?, ?, ?, ?, 'lead');""",
                (name, email, phone, psid, igsid)
            )
            contact_id = cursor.lastrowid
            
        # Check if conversation exists
        conv_row = cursor.execute("SELECT id FROM conversations WHERE contact_id = ?;", (contact_id,)).fetchone()
        if conv_row:
            return conv_row["id"]
        else:
            cursor.execute(
                "INSERT INTO conversations (contact_id, last_message_preview) VALUES (?, 'No messages yet');",
                (contact_id,)
            )
            return cursor.lastrowid


# ==========================================
# DEALS CRUD HELPERS
# ==========================================

def get_deals():
    """Gets all pipeline deals enriched with contact details."""
    query = """
        SELECT 
            d.id as deal_id,
            d.name as deal_name,
            d.value as deal_value,
            d.stage as deal_stage,
            d.contact_id,
            c.name as contact_name,
            c.avatar as contact_avatar
        FROM deals d
        JOIN contacts c ON d.contact_id = c.id;
    """
    with get_db() as conn:
        rows = conn.execute(query).fetchall()
        return [dict(r) for r in rows]

def create_deal(contact_id, name, value, stage="lead"):
    """Creates a new deal in the sales pipeline."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO deals (contact_id, name, value, stage) VALUES (?, ?, ?, ?);",
            (contact_id, name, float(value), stage)
        )
        return cursor.lastrowid

def update_deal_stage(deal_id, stage):
    """Updates a deal's board stage (lead, contacted, proposal, won, etc.)"""
    with get_db() as conn:
        conn.execute(
            "UPDATE deals SET stage = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?;",
            (stage, deal_id)
        )
