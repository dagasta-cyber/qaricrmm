/**
 * QariCrm Frontend Application Controller
 * Manages routing, state, templates, drag-and-drop, SSE stream, and Bilingual (EN/AR) translation
 */

// Bilingual Translation Dictionary
const translations = {
    en: {
        // Sidebar Navigation
        logo_sub: "Crm",
        nav_inbox: "Unified Inbox",
        nav_contacts: "Contacts",
        nav_pipeline: "Sales Pipeline",
        nav_settings: "Integrations",
        status_sim: "Simulator Live",
        status_sim_off: "Simulator Offline",
        connected: "Connected",
        disconnected: "Disconnected",
        add_contact: "Add Contact",
        add_deal: "Add Deal",
        
        // Inbox View
        search_conversations: "Search conversations...",
        no_conv_selected: "No Conversation Selected",
        no_conv_selected_desc: "Select a contact thread from the sidebar to view exchange history and send replies.",
        composer_placeholder: "Type your reply here... (press Enter to send)",
        retrieving_history: "Retrieving message history...",
        no_messages: "No messages in this chat yet.",
        email_addr: "Email Address",
        phone_num: "Phone Number",
        preferred_channel: "Preferred Channel",
        not_specified: "Not specified",
        via: "via",
        
        // Contacts View
        search_contacts: "Search contacts...",
        col_name: "Name",
        col_email: "Email",
        col_phone: "Phone",
        col_status: "Lead Status",
        col_created: "Date Created",
        no_contacts_found: "No contacts found. Click \"Add Contact\" to create one.",
        
        // Pipeline View
        col_lead: "Lead Column",
        col_contacted: "Contacted",
        col_proposal: "Proposal Sent",
        col_negotiation: "Negotiation",
        col_won: "Won",
        col_lost: "Lost",
        
        // Settings View
        sim_engine_title: "Conversation Simulation Engine",
        sim_engine_desc: "Turn on mock message events to test the Unified Inbox instantly without configuring API keys.",
        sim_auto_label: "Enable Automatic Incoming Chats",
        sim_freq_desc: "Fires a mock query every 40s",
        sim_trigger_title: "Trigger Immediate Message",
        gmail_title: "Google Gmail API Integration",
        gmail_desc: "Authorise access to mail accounts using credentials from Google Cloud Console.",
        g_client_id_label: "Google OAuth Client ID",
        g_client_secret_label: "Google OAuth Client Secret",
        g_redirect_label: "Authorized Redirect URI (Callback)",
        btn_save_g: "Save Google Keys",
        btn_connect_g: "Connect Gmail Account",
        meta_title: "Meta Graph APIs Integration (WhatsApp, FB, IG)",
        meta_desc: "Configure tokens to receive webhooks and send messages back on Meta's messaging networks.",
        m_verify_label: "Meta Webhook Verification Token (Configure in Meta Webhooks)",
        m_page_token_label: "Meta Page Access Token (Facebook Messenger / Instagram DMs)",
        m_wa_phone_label: "WhatsApp Cloud API Phone Number ID",
        m_wa_token_label: "WhatsApp Cloud API System Token",
        btn_save_meta: "Save Meta Credentials",
        
        // Modals
        modal_contact_title: "Create New Contact",
        modal_contact_name: "Full Name",
        modal_contact_email: "Email Address",
        modal_contact_phone: "Phone Number (with country code)",
        modal_contact_stage: "Lead Stage",
        modal_btn_cancel: "Cancel",
        modal_btn_create_contact: "Create Contact",
        
        modal_deal_title: "Create Sales Deal",
        modal_deal_name: "Deal Name",
        modal_deal_value: "Deal Value ($)",
        modal_deal_contact: "Associated Contact",
        modal_deal_stage: "Pipeline Stage",
        modal_btn_create_deal: "Add Deal",
        
        btn_ai_assist: "AI Assist",
        gemini_title: "Google Gemini AI Settings",
        gemini_desc: "Configure Gemini API credentials to enable auto-draft assistants in your chats.",
        gemini_key_label: "Gemini API Access Key",
        btn_save_gemini: "Save Gemini Key",
        
        link_get_gemini_key: "Get Gemini Key ↗",
        link_meta_portal: "Meta Developer Portal ↗",
        link_wa_setup: "WhatsApp Setup Guide ↗"
    },
    ar: {
        // Sidebar Navigation
        logo_sub: "سي ار ام",
        nav_inbox: "البريد الوارد الموحد",
        nav_contacts: "جهات الاتصال",
        nav_pipeline: "قناة المبيعات",
        nav_settings: "التكاملات",
        status_sim: "المحاكي نشط",
        status_sim_off: "المحاكي متوقف",
        connected: "متصل",
        disconnected: "غير متصل",
        add_contact: "إضافة جهة اتصال",
        add_deal: "إضافة صفقة",
        
        // Inbox View
        search_conversations: "البحث في المحادثات...",
        no_conv_selected: "لم يتم اختيار محادثة",
        no_conv_selected_desc: "اختر محادثة اتصال من القائمة الجانبية لعرض تاريخ المراسلات وإرسال الردود.",
        composer_placeholder: "اكتب ردك هنا... (اضغط Enter للإرسال)",
        retrieving_history: "جاري استرداد تاريخ الرسائل...",
        no_messages: "لا توجد رسائل في هذه المحادثة بعد.",
        email_addr: "البريد الإلكتروني",
        phone_num: "رقم الهاتف",
        preferred_channel: "القناة المفضلة",
        not_specified: "غير محدد",
        via: "عبر",
        
        // Contacts View
        search_contacts: "البحث في جهات الاتصال...",
        col_name: "الاسم",
        col_email: "البريد الإلكتروني",
        col_phone: "الهاتف",
        col_status: "حالة العميل",
        col_created: "تاريخ الإنشاء",
        no_contacts_found: "لم يتم العثور على جهات اتصال. انقر فوق \"إضافة جهة اتصال\" لإنشاء واحدة.",
        
        // Pipeline View
        col_lead: "عميل محتمل",
        col_contacted: "تم التواصل",
        col_proposal: "تم تقديم عرض",
        col_negotiation: "تفاوض",
        col_won: "مكتسبة",
        col_lost: "مفقودة",
        
        // Settings View
        sim_engine_title: "محرك محاكاة المحادثات",
        sim_engine_desc: "قم بتشغيل محاكاة الرسائل الواردة لاختبار البريد الموحد فوراً دون تكوين مفاتيح API.",
        sim_auto_label: "تمكين المحادثات الواردة التلقائية",
        sim_freq_desc: "يرسل رسالة تجريبية كل 40 ثانية",
        sim_trigger_title: "إرسال رسالة فورية تجريبية",
        gmail_title: "تكامل Google Gmail API",
        gmail_desc: "تخويل الوصول إلى حسابات البريد الإلكتروني باستخدام بيانات الاعتماد من Google Cloud Console.",
        g_client_id_label: "معرّف عميل Google OAuth Client ID",
        g_client_secret_label: "سر عميل Google OAuth Client Secret",
        g_redirect_label: "عنوان إعادة التوجيه المعتمد (Callback)",
        btn_save_g: "حفظ مفاتيح Google",
        btn_connect_g: "ربط حساب Gmail",
        meta_title: "تكامل Meta Graph APIs (واتساب، فيسبوك، إنستغرام)",
        meta_desc: "تكوين الرموز المميزة لتلقي إشعارات الويب وإرسال الرسائل مرة أخرى على شبكات Meta.",
        m_verify_label: "رمز التحقق من ويب هوك Meta (تكوينه في ويب هوك Meta)",
        m_page_token_label: "رمز وصول الصفحة لـ Meta (فيسبوك ماسنجر / إنستغرام DMs)",
        m_wa_phone_label: "معرف رقم الهاتف لـ WhatsApp Cloud API",
        m_wa_token_label: "الرمز البرمجي لـ WhatsApp Cloud API",
        btn_save_meta: "حفظ بيانات اعتماد Meta",
        
        // Modals
        modal_contact_title: "إنشاء جهة اتصال جديدة",
        modal_contact_name: "الاسم الكامل",
        modal_contact_email: "البريد الإلكتروني",
        modal_contact_phone: "رقم الهاتف (مع رمز الدولة)",
        modal_contact_stage: "حالة العميل المحتمل",
        modal_btn_cancel: "إلغاء",
        modal_btn_create_contact: "إنشاء جهة اتصال",
        
        modal_deal_title: "إنشاء صفقة مبيعات جديدة",
        modal_deal_name: "اسم الصفقة",
        modal_deal_value: "قيمة الصفقة ($)",
        modal_deal_contact: "جهة الاتصال المرتبطة",
        modal_deal_stage: "مرحلة الصفقة في القناة",
        modal_btn_create_deal: "إضافة الصفقة",
        
        btn_ai_assist: "مساعد الذكاء",
        gemini_title: "إعدادات Google Gemini AI",
        gemini_desc: "تكوين بيانات اعتماد Gemini لتفعيل مساعد الرد الذكي التلقائي في محادثاتك.",
        gemini_key_label: "مفتاح وصول Gemini API",
        btn_save_gemini: "حفظ مفتاح Gemini",
        
        link_get_gemini_key: "احصل على مفتاح Gemini ↗",
        link_meta_portal: "بوابة مطوري Meta ↗",
        link_wa_setup: "دليل إعداد WhatsApp ↗"
    }
};

// Global App State
const state = {
    contacts: [],
    conversations: [],
    messages: [],
    deals: [],
    currentView: 'inbox',
    activeConversationId: null,
    settings: {},
    language: localStorage.getItem('qari_crm_lang') || 'en'
};

// Translation helper
function t(key) {
    const lang = state.language;
    return translations[lang][key] || translations['en'][key] || key;
}

// ==========================================
// INITIALIZATION & SSE CONNECTION
// ==========================================

document.addEventListener('DOMContentLoaded', () => {
    initApp();
    setupSSE();
    setupGlobalEventListeners();
});

async function initApp() {
    updateLanguageUI();
    
    // Initial fetch of fundamental records
    try {
        state.contacts = await API.getContacts();
        state.settings = await API.getSettings();
        updateLanguageUI(); // Call again in case settings loads status
    } catch (e) {
        console.error("Failed to load initial data", e);
    }
    
    // Check URL Hash for routing
    window.addEventListener('hashchange', handleRouting);
    handleRouting();
}

function setupSSE() {
    const statusDot = document.querySelector('.pulse-dot');
    const statusText = document.querySelector('.status-text');
    const connectionStatus = document.getElementById('connection-status');
    
    const eventSource = new EventSource('/api/stream');
    
    eventSource.onopen = () => {
        console.log('SSE Stream connected.');
        if (connectionStatus) {
            connectionStatus.className = 'connection-badge connected';
            connectionStatus.querySelector('span').innerText = t('connected');
        }
        if (statusDot) statusDot.className = 'pulse-dot green';
    };
    
    eventSource.onerror = (err) => {
        console.error('SSE Stream error, attempting reconnect...', err);
        if (connectionStatus) {
            connectionStatus.className = 'connection-badge disconnected';
            connectionStatus.querySelector('span').innerText = t('disconnected');
        }
        if (statusDot) statusDot.className = 'pulse-dot';
    };
    
    // Listen for new messages
    eventSource.addEventListener('message_received', (event) => {
        const msg = JSON.parse(event.data);
        console.log("SSE New Message:", msg);
        
        // If current inbox message log belongs to active thread, append it
        if (state.currentView === 'inbox' && state.activeConversationId === msg.conversation_id) {
            // Append message bubble
            appendMessageBubble(msg);
            scrollChatToBottom();
            msg.status = 'read';
        }
        
        loadConversationsAndRefresh();
    });
    
    // Listen for updated conversations list
    eventSource.addEventListener('conversations_updated', (event) => {
        state.conversations = JSON.parse(event.data);
        if (state.currentView === 'inbox') {
            renderConversationsList();
        }
    });

    // Listen for pipeline updates
    eventSource.addEventListener('deal_updated', async () => {
        if (state.currentView === 'pipeline') {
            await loadDealsAndRefresh();
        }
    });
    
    // Listen for contact modifications
    eventSource.addEventListener('contact_created', async () => {
        state.contacts = await API.getContacts();
        if (state.currentView === 'contacts') {
            renderContactsView();
        }
    });
}

async function loadConversationsAndRefresh() {
    try {
        state.conversations = await API.getConversations();
        if (state.currentView === 'inbox') {
            renderConversationsList();
            updateUnreadBadge();
        }
    } catch (e) {
        console.error("Error refreshing conversations list", e);
    }
}

async function loadDealsAndRefresh() {
    try {
        state.deals = await API.getDeals();
        if (state.currentView === 'pipeline') {
            renderPipelineView();
        }
    } catch (e) {
        console.error("Error refreshing deals board", e);
    }
}

function updateUnreadBadge() {
    const badge = document.getElementById('unread-count');
    if (!badge) return;
    
    const unreadCount = state.conversations.filter(c => c.last_message_preview && c.last_message_preview.startsWith("New")).length;
    if (unreadCount > 0) {
        badge.innerText = unreadCount;
        badge.style.display = 'block';
    } else {
        badge.style.display = 'none';
    }
}

// ==========================================
// LANGUAGE SWITCHER ENGINE
// ==========================================

window.switchLanguage = function(lang) {
    state.language = lang;
    localStorage.setItem('qari_crm_lang', lang);
    updateLanguageUI();
    handleRouting(); // Re-render the active view in new language
};

function updateLanguageUI() {
    const lang = state.language;
    const isRtl = lang === 'ar';
    
    // Apply layout direction HTML tags
    document.documentElement.dir = isRtl ? 'rtl' : 'ltr';
    document.documentElement.lang = lang;
    
    // Toggle active buttons
    document.querySelectorAll('.lang-btn').forEach(btn => btn.classList.remove('active'));
    const activeBtn = document.getElementById(`lang-btn-${lang}`);
    if (activeBtn) activeBtn.classList.add('active');
    
    // 1. Translate Sidebar Links
    const logoSub = document.querySelector('.logo-text span');
    if (logoSub) logoSub.innerText = t('logo_sub');
    
    const navInbox = document.querySelector('#nav-inbox span:not(.badge)');
    if (navInbox) navInbox.innerText = t('nav_inbox');
    
    const navContacts = document.querySelector('#nav-contacts span');
    if (navContacts) navContacts.innerText = t('nav_contacts');
    
    const navPipeline = document.querySelector('#nav-pipeline span');
    if (navPipeline) navPipeline.innerText = t('nav_pipeline');
    
    const navSettings = document.querySelector('#nav-settings span');
    if (navSettings) navSettings.innerText = t('nav_settings');
    
    // Simulator Status in Sidebar
    const simStatusText = document.querySelector('.status-text');
    if (simStatusText) {
        const isSimEnabled = state.settings.simulator_enabled === "1";
        simStatusText.innerText = isSimEnabled ? t('status_sim') : t('status_sim_off');
    }
    
    // 2. Translate Header Connection Badge
    const connSpan = document.querySelector('#connection-status span');
    if (connSpan) {
        const isConnected = document.getElementById('connection-status').classList.contains('connected');
        connSpan.innerText = isConnected ? t('connected') : t('disconnected');
    }
    
    // 3. Translate Modals Static Labels
    // Contact Modal
    document.querySelector('#contact-modal h2').innerText = t('modal_contact_title');
    document.querySelector('label[for="c-name"]').innerText = t('modal_contact_name');
    document.querySelector('label[for="c-email"]').innerText = t('modal_contact_email');
    document.querySelector('label[for="c-phone"]').innerText = t('modal_contact_phone');
    document.querySelector('label[for="c-status"]').innerText = t('modal_contact_stage');
    
    const contactCancel = document.querySelector('#contact-form .btn-secondary');
    if (contactCancel) contactCancel.innerText = t('modal_btn_cancel');
    const contactSubmit = document.querySelector('#contact-form button[type="submit"]');
    if (contactSubmit) contactSubmit.innerText = t('modal_btn_create_contact');
    
    // Deal Modal
    document.querySelector('#deal-modal h2').innerText = t('modal_deal_title');
    document.querySelector('label[for="d-name"]').innerText = t('modal_deal_name');
    document.querySelector('label[for="d-value"]').innerText = t('modal_deal_value');
    document.querySelector('label[for="d-contact"]').innerText = t('modal_deal_contact');
    document.querySelector('label[for="d-stage"]').innerText = t('modal_deal_stage');
    
    const dealCancel = document.querySelector('#deal-form .btn-secondary');
    if (dealCancel) dealCancel.innerText = t('modal_btn_cancel');
    const dealSubmit = document.querySelector('#deal-form button[type="submit"]');
    if (dealSubmit) dealSubmit.innerText = t('modal_btn_create_deal');
}

// ==========================================
// NAVIGATION & ROUTING
// ==========================================

function handleRouting() {
    const hash = window.location.hash || '#inbox';
    const parts = hash.substring(1).split('?');
    const viewName = parts[0];
    const queryStr = parts[1] || '';
    
    document.querySelectorAll('.sidebar-nav a').forEach(a => {
        a.classList.remove('active');
    });
    const activeNav = document.getElementById(`nav-${viewName}`);
    if (activeNav) activeNav.classList.add('active');
    
    const titleEl = document.getElementById('page-title');
    const headerBtn = document.getElementById('header-action-btn');
    
    state.currentView = viewName;
    
    // Parse redirect indicator messages
    if (queryStr) {
        const urlParams = new URLSearchParams(queryStr);
        if (urlParams.get('gmail') === 'connected') {
            window.location.hash = '#' + viewName;
            setTimeout(() => alert(state.language === 'ar' ? "تم ربط حساب Gmail بنجاح!" : "Gmail account connected successfully!"), 300);
        } else if (urlParams.get('error') === 'gmail_not_configured') {
            window.location.hash = '#' + viewName;
            setTimeout(() => alert(state.language === 'ar' ? "يرجى إدخال وحفظ معرف العميل وسر العميل لـ Google أولاً!" : "Please enter and save your Google OAuth Client ID and Client Secret first!"), 300);
        }
    }
    
    if (viewName === 'inbox') {
        titleEl.innerText = t('nav_inbox');
        headerBtn.style.display = 'none';
        renderInboxView();
    } else if (viewName === 'contacts') {
        titleEl.innerText = t('nav_contacts');
        headerBtn.style.display = 'inline-flex';
        headerBtn.innerHTML = `<i data-lucide="plus"></i><span>${t('add_contact')}</span>`;
        headerBtn.onclick = () => showModal('contact-modal');
        renderContactsView();
    } else if (viewName === 'pipeline') {
        titleEl.innerText = t('nav_pipeline');
        headerBtn.style.display = 'inline-flex';
        headerBtn.innerHTML = `<i data-lucide="plus"></i><span>${t('add_deal')}</span>`;
        headerBtn.onclick = () => showModal('deal-modal');
        renderPipelineView();
    } else if (viewName === 'settings') {
        titleEl.innerText = t('nav_settings');
        headerBtn.style.display = 'none';
        renderSettingsView();
    }
    
    lucide.createIcons();
}

window.showModal = function(modalId) {
    if (modalId === 'deal-modal') {
        const select = document.getElementById('d-contact');
        if (select) {
            select.innerHTML = state.contacts.map(c => 
                `<option value="${c.id}">${c.name}</option>`
            ).join('');
        }
    }
    document.getElementById(modalId).classList.add('active');
    lucide.createIcons();
};

function setupGlobalEventListeners() {
    // Add Contact Submit
    const contactForm = document.getElementById('contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const contactData = {
                name: document.getElementById('c-name').value,
                email: document.getElementById('c-email').value,
                phone: document.getElementById('c-phone').value,
                status: document.getElementById('c-status').value
            };
            
            try {
                await API.createContact(contactData);
                document.getElementById('contact-modal').classList.remove('active');
                contactForm.reset();
                state.contacts = await API.getContacts();
                if (state.currentView === 'contacts') renderContactsView();
            } catch (err) {
                alert("Error: " + err.message);
            }
        });
    }
    
    // Add Deal Submit
    const dealForm = document.getElementById('deal-form');
    if (dealForm) {
        dealForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const dealData = {
                name: document.getElementById('d-name').value,
                value: parseFloat(document.getElementById('d-value').value),
                contact_id: parseInt(document.getElementById('d-contact').value),
                stage: document.getElementById('d-stage').value
            };
            
            try {
                await API.createDeal(dealData);
                document.getElementById('deal-modal').classList.remove('active');
                dealForm.reset();
                if (state.currentView === 'pipeline') loadDealsAndRefresh();
            } catch (err) {
                alert("Error: " + err.message);
            }
        });
    }
}

// ==========================================
// RENDER: UNIFIED INBOX VIEW
// ==========================================

function renderInboxView() {
    const viewport = document.getElementById('content-viewport');
    viewport.innerHTML = `
        <div class="inbox-layout">
            <!-- Left Thread Menu -->
            <div class="inbox-threads">
                <div class="threads-search-bar">
                    <div class="search-wrapper">
                        <i data-lucide="search"></i>
                        <input type="text" placeholder="${t('search_conversations')}" id="inbox-search">
                    </div>
                </div>
                <div class="threads-list" id="threads-list-container">
                </div>
            </div>
            
            <!-- Center Chat Frame -->
            <div class="inbox-chat" id="inbox-chat-pane">
                <div class="empty-state">
                    <i data-lucide="message-square"></i>
                    <h3>${t('no_conv_selected')}</h3>
                    <p>${t('no_conv_selected_desc')}</p>
                </div>
            </div>
            
            <!-- Right Contact Bio -->
            <div class="inbox-info" id="inbox-info-pane">
            </div>
        </div>
    `;
    
    const searchInput = document.getElementById('inbox-search');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const val = e.target.value.toLowerCase();
            document.querySelectorAll('.thread-item').forEach(item => {
                const name = item.querySelector('.thread-name').innerText.toLowerCase();
                const preview = item.querySelector('.thread-preview').innerText.toLowerCase();
                if (name.includes(val) || preview.includes(val)) {
                    item.style.display = 'flex';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    }
    
    loadConversationsAndRefresh();
}

function renderConversationsList() {
    const container = document.getElementById('threads-list-container');
    if (!container) return;
    
    if (state.conversations.length === 0) {
        container.innerHTML = `
            <div class="empty-state" style="padding: 30px 10px;">
                <p>No active conversations.</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = state.conversations.map(c => {
        const activeClass = state.activeConversationId === c.conversation_id ? 'active' : '';
        const timeStr = formatRelativeTime(c.last_message_at);
        const lastMsg = c.last_message_preview || "No messages";
        const channel = detectChannelFromMessagePreview(c);
        
        return `
            <div class="thread-item ${activeClass}" onclick="selectConversation(${c.conversation_id})" data-id="${c.conversation_id}">
                <div class="thread-avatar-container">
                    <img class="thread-avatar" src="${c.contact_avatar || 'https://api.dicebear.com/7.x/initials/svg?seed=' + c.contact_name}" alt="${c.contact_name}">
                    <span class="channel-badge ${channel}">
                        <i data-lucide="${getChannelIconName(channel)}"></i>
                    </span>
                </div>
                <div class="thread-details">
                    <div class="thread-meta">
                        <span class="thread-name">${c.contact_name}</span>
                        <span class="thread-time">${timeStr}</span>
                    </div>
                    <div class="thread-preview">${lastMsg}</div>
                </div>
            </div>
        `;
    }).join('');
    
    lucide.createIcons();
}

window.selectConversation = async function(convId) {
    state.activeConversationId = convId;
    
    document.querySelectorAll('.thread-item').forEach(item => {
        item.classList.remove('active');
        if (parseInt(item.dataset.id) === convId) {
            item.classList.add('active');
        }
    });
    
    const conv = state.conversations.find(c => c.conversation_id === convId);
    if (!conv) return;
    
    // Render Chat Pane Center
    const chatPane = document.getElementById('inbox-chat-pane');
    chatPane.innerHTML = `
        <div class="chat-header">
            <div class="chat-user-info">
                <div class="thread-avatar-container">
                    <img class="thread-avatar" src="${conv.contact_avatar || 'https://api.dicebear.com/7.x/initials/svg?seed=' + conv.contact_name}" alt="${conv.contact_name}">
                </div>
                <div class="chat-user-details">
                    <h3>${conv.contact_name}</h3>
                    <span class="chat-user-status">${t('col_' + (conv.contact_status || 'lead'))}</span>
                </div>
            </div>
        </div>
        <div class="chat-messages" id="chat-messages-container">
            <div class="empty-state">
                <i data-lucide="loader"></i>
                <p>${t('retrieving_history')}</p>
            </div>
        </div>
        <div class="chat-input-area">
            <form class="chat-form" id="chat-composer-form">
                <textarea id="chat-reply-input" required placeholder="${t('composer_placeholder')}" rows="1"></textarea>
                <button type="button" class="btn-ai-assist" id="ai-assist-btn" onclick="requestAiDraft(${conv.conversation_id})" title="${t('btn_ai_assist')}">
                    <i data-lucide="sparkles"></i>
                </button>
                <button type="submit">
                    <i data-lucide="send"></i>
                </button>
            </form>
        </div>
    `;
    
    lucide.createIcons();
    
    // Render Right Info Pane
    const infoPane = document.getElementById('inbox-info-pane');
    infoPane.innerHTML = `
        <div class="info-profile">
            <img class="info-avatar" src="${conv.contact_avatar || 'https://api.dicebear.com/7.x/initials/svg?seed=' + conv.contact_name}">
            <h3 class="info-name">${conv.contact_name}</h3>
            <span class="info-status ${conv.contact_status || 'lead'}">${t('col_' + (conv.contact_status || 'lead'))}</span>
        </div>
        <div class="info-details">
            <div class="info-item">
                <span class="info-item-label">${t('email_addr')}</span>
                <span class="info-item-val">${conv.contact_email || t('not_specified')}</span>
            </div>
            <div class="info-item">
                <span class="info-item-label">${t('phone_num')}</span>
                <span class="info-item-val">${conv.contact_phone || t('not_specified')}</span>
            </div>
            <div class="info-item">
                <span class="info-item-label">${t('preferred_channel')}</span>
                <span class="info-item-val" style="text-transform: capitalize;">${detectChannelFromMessagePreview(conv)}</span>
            </div>
        </div>
    `;
    
    try {
        state.messages = await API.getMessages(convId);
        renderMessagesHistory();
    } catch (e) {
        console.error("Failed to load messages", e);
    }
    
    // Bind reply events
    const replyForm = document.getElementById('chat-composer-form');
    const replyInput = document.getElementById('chat-reply-input');
    
    if (replyForm && replyInput) {
        replyInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                replyForm.requestSubmit();
            }
        });
        
        replyForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const text = replyInput.value.trim();
            if (!text) return;
            replyInput.value = '';
            
            try {
                await API.sendMessage(convId, text);
            } catch (err) {
                alert("Send Error: " + err.message);
            }
        });
    }
}

function renderMessagesHistory() {
    const container = document.getElementById('chat-messages-container');
    if (!container) return;
    
    if (state.messages.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <p>${t('no_messages')}</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = '';
    state.messages.forEach(msg => {
        appendMessageBubble(msg);
    });
    
    scrollChatToBottom();
}

function appendMessageBubble(msg) {
    const container = document.getElementById('chat-messages-container');
    if (!container) return;
    
    const emptyState = container.querySelector('.empty-state');
    if (emptyState) emptyState.remove();
    
    const direction = msg.sender_type === 'user' ? 'outgoing' : 'incoming';
    const channel = msg.channel_type || 'whatsapp';
    
    let displayContent = msg.content;
    if (channel === 'gmail' && msg.content.includes('Subject:')) {
        displayContent = msg.content.replace(/\n\n/, '<br><hr style="border:0;border-top:1px solid rgba(255,255,255,0.06);margin:8px 0;"><br>');
        displayContent = displayContent.replace(/\n/g, '<br>');
    } else {
        displayContent = displayContent.replace(/\n/g, '<br>');
    }
    
    const group = document.createElement('div');
    group.className = `message-group ${direction}`;
    group.innerHTML = `
        <div class="message-bubble">
            ${displayContent}
        </div>
        <div class="message-meta">
            <span class="message-time">${formatClockTime(msg.sent_at)}</span>
            <span class="message-channel" style="text-transform: capitalize;">${t('via')} ${channel}</span>
        </div>
    `;
    
    container.appendChild(group);
}

function scrollChatToBottom() {
    const container = document.getElementById('chat-messages-container');
    if (container) {
        container.scrollTop = container.scrollHeight;
    }
}

// ==========================================
// RENDER: CONTACTS DIRECTORY VIEW
// ==========================================

function renderContactsView() {
    const viewport = document.getElementById('content-viewport');
    viewport.innerHTML = `
        <div class="contacts-layout">
            <div class="contacts-controls">
                <div class="search-wrapper" style="width: 300px;">
                    <i data-lucide="search"></i>
                    <input type="text" placeholder="${t('search_contacts')}" id="contacts-search">
                </div>
            </div>
            
            <div class="contacts-table-container">
                <table class="contacts-table">
                    <thead>
                        <tr>
                            <th>${t('col_name')}</th>
                            <th>${t('col_email')}</th>
                            <th>${t('col_phone')}</th>
                            <th>${t('col_status')}</th>
                            <th>${t('col_created')}</th>
                        </tr>
                    </thead>
                    <tbody id="contacts-table-body">
                    </tbody>
                </table>
            </div>
        </div>
    `;
    
    const body = document.getElementById('contacts-table-body');
    if (state.contacts.length === 0) {
        body.innerHTML = `<tr><td colspan="5" style="text-align:center;padding:32px;color:var(--text-muted);">${t('no_contacts_found')}</td></tr>`;
        return;
    }
    
    body.innerHTML = state.contacts.map(c => `
        <tr>
            <td class="table-user-cell">
                <img class="table-user-avatar" src="${c.avatar || 'https://api.dicebear.com/7.x/initials/svg?seed=' + c.name}">
                <span>${c.name}</span>
            </td>
            <td>${c.email || '<span style="color:var(--text-dark);">—</span>'}</td>
            <td>${c.phone || '<span style="color:var(--text-dark);">—</span>'}</td>
            <td>
                <span class="info-status ${c.status}">${t('col_' + c.status)}</span>
            </td>
            <td>${formatDate(c.created_at)}</td>
        </tr>
    `).join('');
    
    const searchInput = document.getElementById('contacts-search');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const val = e.target.value.toLowerCase();
            document.querySelectorAll('#contacts-table-body tr').forEach(tr => {
                const text = tr.innerText.toLowerCase();
                tr.style.display = text.includes(val) ? '' : 'none';
            });
        });
    }
    
    lucide.createIcons();
}

// ==========================================
// RENDER: SALES PIPELINE VIEW (KANBAN BOARD)
// ==========================================

async function renderPipelineView() {
    const viewport = document.getElementById('content-viewport');
    
    const stages = [
        { key: 'lead', label: t('col_lead') },
        { key: 'contacted', label: t('col_contacted') },
        { key: 'proposal', label: t('col_proposal') },
        { key: 'negotiation', label: t('col_negotiation') },
        { key: 'won', label: t('col_won') },
        { key: 'lost', label: t('col_lost') }
    ];
    
    viewport.innerHTML = `
        <div class="pipeline-layout" id="pipeline-board">
            ${stages.map(st => `
                <div class="pipeline-column" data-stage="${st.key}">
                    <div class="column-header">
                        <span class="column-title">${st.label}</span>
                        <span class="column-count" id="count-${st.key}">0</span>
                    </div>
                    <div class="column-cards" id="column-${st.key}">
                    </div>
                </div>
            `).join('')}
        </div>
    `;
    
    await loadDealsAndRefreshState();
    
    stages.forEach(st => {
        const colContainer = document.getElementById(`column-${st.key}`);
        const countBadge = document.getElementById(`count-${st.key}`);
        const colDeals = state.deals.filter(d => d.deal_stage === st.key);
        
        countBadge.innerText = colDeals.length;
        
        if (colDeals.length === 0) {
            colContainer.innerHTML = '';
            return;
        }
        
        colContainer.innerHTML = colDeals.map(d => `
            <div class="deal-card" draggable="true" id="deal-${d.deal_id}" data-id="${d.deal_id}">
                <div class="deal-name">${d.deal_name}</div>
                <div class="deal-value">$${d.deal_value.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</div>
                <div class="deal-footer">
                    <img class="deal-avatar" src="${d.contact_avatar || 'https://api.dicebear.com/7.x/initials/svg?seed=' + d.contact_name}">
                    <span class="deal-contact-name">${d.contact_name}</span>
                </div>
            </div>
        `).join('');
    });
    
    setupDragAndDrop();
    lucide.createIcons();
}

async function loadDealsAndRefreshState() {
    try {
        state.deals = await API.getDeals();
    } catch (e) {
        console.error("Failed to load deals", e);
    }
}

function setupDragAndDrop() {
    const cards = document.querySelectorAll('.deal-card');
    const columns = document.querySelectorAll('.column-cards');
    
    cards.forEach(card => {
        card.addEventListener('dragstart', (e) => {
            e.dataTransfer.setData('text/plain', card.dataset.id);
            setTimeout(() => card.style.opacity = '0.4', 0);
        });
        
        card.addEventListener('dragend', () => {
            card.style.opacity = '1';
        });
    });
    
    columns.forEach(col => {
        col.addEventListener('dragover', (e) => {
            e.preventDefault();
            col.classList.add('drag-over');
        });
        
        col.addEventListener('dragleave', () => {
            col.classList.remove('drag-over');
        });
        
        col.addEventListener('drop', async (e) => {
            e.preventDefault();
            col.classList.remove('drag-over');
            
            const dealId = parseInt(e.dataTransfer.getData('text/plain'));
            const stage = col.parentElement.dataset.stage;
            
            if (isNaN(dealId)) return;
            
            try {
                await API.updateDealStage(dealId, stage);
                await loadDealsAndRefresh();
            } catch (err) {
                alert("Failed to move deal: " + err.message);
            }
        });
    });
}

// ==========================================
// RENDER: INTEGRATIONS / SETTINGS VIEW
// ==========================================

async function renderSettingsView() {
    const viewport = document.getElementById('content-viewport');
    
    try {
        state.settings = await API.getSettings();
    } catch (e) {
        console.error("Error loading settings", e);
    }
    
    const isSimEnabled = state.settings.simulator_enabled === "1";
    
    viewport.innerHTML = `
        <div class="settings-layout">
            <div class="settings-grid">
                <!-- Simulator Toggles -->
                <div class="settings-card glass-panel">
                    <div class="settings-card-header">
                        <div class="settings-icon-wrapper simulator">
                            <i data-lucide="play-circle"></i>
                        </div>
                        <div class="settings-title-desc">
                            <h3>${t('sim_engine_title')}</h3>
                            <p>${t('sim_engine_desc')}</p>
                        </div>
                    </div>
                    
                    <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid var(--border-glass); padding-bottom:16px;">
                        <label class="switch-control">
                            <span class="switch">
                                <input type="checkbox" id="sim-toggle" ${isSimEnabled ? 'checked' : ''}>
                                <span class="slider"></span>
                            </span>
                            <span style="font-size:14px; font-weight:600;">${t('sim_auto_label')}</span>
                        </label>
                        <span style="font-size:12px; color:var(--text-muted);">${t('sim_freq_desc')}</span>
                    </div>
                    
                    <div>
                        <h4 style="font-size:13px; font-weight:700; text-transform:uppercase; color:var(--text-dark); margin-bottom:12px;">${t('sim_trigger_title')}</h4>
                        <div class="simulator-actions">
                            <button class="btn btn-secondary" onclick="triggerSimulatedEvent('gmail', this)">
                                <i data-lucide="mail" style="color:var(--color-gmail);"></i> Gmail
                            </button>
                            <button class="btn btn-secondary" onclick="triggerSimulatedEvent('whatsapp', this)">
                                <i data-lucide="message-square" style="color:var(--color-whatsapp);"></i> WhatsApp
                            </button>
                            <button class="btn btn-secondary" onclick="triggerSimulatedEvent('messenger', this)">
                                <i data-lucide="facebook" style="color:var(--color-messenger);"></i> Messenger
                            </button>
                            <button class="btn btn-secondary" onclick="triggerSimulatedEvent('instagram', this)">
                                <i data-lucide="instagram" style="color:var(--color-instagram);"></i> Instagram
                            </button>
                        </div>
                    </div>
                </div>
            
                <!-- Gmail credentials card -->
                <div class="settings-card glass-panel">
                    <div class="settings-card-header">
                        <div class="settings-icon-wrapper gmail">
                            <i data-lucide="mail"></i>
                        </div>
                        <div class="settings-title-desc">
                            <h3>${t('gmail_title')}</h3>
                            <p>${t('gmail_desc')}</p>
                        </div>
                    </div>
                    <form id="settings-gmail-form" class="settings-form" style="display:flex; flex-direction:column; gap:16px;">
                        <div class="form-group">
                            <label>${t('g_client_id_label')}</label>
                            <input type="text" id="g-client-id" value="${state.settings.google_client_id || ''}" placeholder="Enter client_id...">
                        </div>
                        <div class="form-group">
                            <label>${t('g_client_secret_label')}</label>
                            <input type="password" id="g-client-secret" value="${state.settings.google_client_secret || ''}" placeholder="Enter client_secret...">
                        </div>
                        <div class="form-group">
                            <label>${t('g_redirect_label')}</label>
                            <input type="text" id="g-redirect-uri" value="${state.settings.google_redirect_uri || ''}" readonly>
                        </div>
                        
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:8px;">
                            <button type="submit" class="btn btn-primary">${t('btn_save_g')}</button>
                            <a href="/api/auth/gmail" class="btn btn-secondary" style="text-decoration:none;">
                                <i data-lucide="key"></i> ${t('btn_connect_g')}
                            </a>
                        </div>
                    </form>
                </div>

                <!-- Gemini API Card -->
                <div class="settings-card glass-panel">
                    <div class="settings-card-header">
                        <div class="settings-icon-wrapper simulator" style="background: linear-gradient(135deg, #a5b4fc 0%, #6366f1 100%);">
                            <i data-lucide="sparkles"></i>
                        </div>
                        <div class="settings-title-desc">
                            <h3>${t('gemini_title')}</h3>
                            <p>${t('gemini_desc')}</p>
                        </div>
                    </div>
                    <form id="settings-gemini-form" class="settings-form" style="display:flex; flex-direction:column; gap:16px;">
                        <div class="form-group">
                            <label>${t('gemini_key_label')}</label>
                            <input type="password" id="gemini-key" value="${state.settings.gemini_api_key || ''}" placeholder="AIzaSy...">
                        </div>
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:8px;">
                            <button type="submit" class="btn btn-primary">${t('btn_save_gemini')}</button>
                            <a href="https://aistudio.google.com/" target="_blank" class="btn btn-secondary" style="text-decoration:none;">
                                <i data-lucide="external-link"></i> ${t('link_get_gemini_key')}
                            </a>
                        </div>
                    </form>
                </div>
                
                <!-- Meta integrations card -->
                <div class="settings-card glass-panel">
                    <div class="settings-card-header">
                        <div class="settings-icon-wrapper meta">
                            <i data-lucide="message-square"></i>
                        </div>
                        <div class="settings-title-desc">
                            <h3>${t('meta_title')}</h3>
                            <p>${t('meta_desc')}</p>
                        </div>
                    </div>
                    <form id="settings-meta-form" class="settings-form" style="display:flex; flex-direction:column; gap:16px;">
                        <div class="form-group">
                            <label>${t('m_verify_label')}</label>
                            <input type="text" id="m-verify-token" value="${state.settings.meta_verify_token || ''}" placeholder="e.g. my_verify_token">
                        </div>
                        <div class="form-group">
                            <label>${t('m_page_token_label')}</label>
                            <input type="password" id="m-page-token" value="${state.settings.meta_page_access_token || ''}" placeholder="Enter Access Token...">
                        </div>
                        <div class="form-group">
                            <label>${t('m_wa_phone_label')}</label>
                            <input type="text" id="m-wa-phone-id" value="${state.settings.meta_whatsapp_phone_number_id || ''}" placeholder="Enter Phone Number ID...">
                        </div>
                        <div class="form-group">
                            <label>${t('m_wa_token_label')}</label>
                            <input type="password" id="m-wa-token" value="${state.settings.meta_whatsapp_access_token || ''}" placeholder="Enter Cloud Token...">
                        </div>
                        
                        <div style="display:flex; gap:12px; align-items:center; margin-top:8px; flex-wrap:wrap;">
                            <button type="submit" class="btn btn-primary">${t('btn_save_meta')}</button>
                            <a href="https://developers.facebook.com/" target="_blank" class="btn btn-secondary" style="text-decoration:none;">
                                <i data-lucide="external-link"></i> ${t('link_meta_portal')}
                            </a>
                            <a href="https://developers.facebook.com/docs/whatsapp/cloud-api/get-started" target="_blank" class="btn btn-secondary" style="text-decoration:none;">
                                <i data-lucide="external-link"></i> ${t('link_wa_setup')}
                            </a>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    `;
    
    // Bind form events
    document.getElementById('settings-gmail-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const data = {
            google_client_id: document.getElementById('g-client-id').value,
            google_client_secret: document.getElementById('g-client-secret').value
        };
        try {
            await API.saveSettings(data);
            alert("Google settings saved.");
            state.settings = await API.getSettings();
        } catch (err) {
            alert("Error: " + err.message);
        }
    });
    
    document.getElementById('settings-meta-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const data = {
            meta_verify_token: document.getElementById('m-verify-token').value,
            meta_page_access_token: document.getElementById('m-page-token').value,
            meta_whatsapp_phone_number_id: document.getElementById('m-wa-phone-id').value,
            meta_whatsapp_access_token: document.getElementById('m-wa-token').value
        };
        try {
            await API.saveSettings(data);
            alert("Meta settings saved.");
            state.settings = await API.getSettings();
        } catch (err) {
            alert("Error: " + err.message);
        }
    });

    document.getElementById('settings-gemini-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const data = {
            gemini_api_key: document.getElementById('gemini-key').value
        };
        try {
            await API.saveSettings(data);
            alert(state.language === 'ar' ? "تم حفظ مفتاح Gemini بنجاح." : "Gemini API key saved.");
            state.settings = await API.getSettings();
        } catch (err) {
            alert("Error: " + err.message);
        }
    });
    
    const toggle = document.getElementById('sim-toggle');
    if (toggle) {
        toggle.addEventListener('change', async (e) => {
            try {
                const res = await API.toggleSimulator(e.target.checked);
                state.settings.simulator_enabled = res.simulator_enabled ? "1" : "0";
                // Refresh sidebar text
                const simStatusText = document.querySelector('.status-text');
                if (simStatusText) {
                    simStatusText.innerText = res.simulator_enabled ? t('status_sim') : t('status_sim_off');
                }
            } catch (err) {
                alert("Toggle Error: " + err.message);
                e.target.checked = !e.target.checked;
            }
        });
    }
    
    lucide.createIcons();
}

window.triggerSimulatedEvent = async function(channel, btn) {
    if (!btn) return;
    const originalContent = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = `<i data-lucide="loader" class="loading"></i> ${state.language === 'ar' ? 'جاري المحاكاة...' : 'Simulating...'}`;
    lucide.createIcons();
    
    try {
        await API.triggerSimulatedMessage(channel);
        btn.innerHTML = `<i data-lucide="check" style="color:var(--accent-emerald);"></i> ${state.language === 'ar' ? 'تم الإرسال!' : 'Triggered!'}`;
        btn.style.borderColor = 'var(--accent-emerald)';
        lucide.createIcons();
        
        setTimeout(() => {
            btn.disabled = false;
            btn.innerHTML = originalContent;
            btn.style.borderColor = '';
            lucide.createIcons();
        }, 1500);
    } catch (e) {
        console.error("Failed to trigger message", e);
        btn.innerHTML = `<i data-lucide="alert-circle" style="color:var(--accent-rose);"></i> ${state.language === 'ar' ? 'فشل!' : 'Failed!'}`;
        btn.style.borderColor = 'var(--accent-rose)';
        lucide.createIcons();
        
        setTimeout(() => {
            btn.disabled = false;
            btn.innerHTML = originalContent;
            btn.style.borderColor = '';
            lucide.createIcons();
        }, 1500);
    }
};

// ==========================================
// STRING & DATE FORMATTERS
// ==========================================

function formatRelativeTime(dateStr) {
    if (!dateStr) return '';
    let cleanStr = dateStr;
    if (!dateStr.includes('T') && !dateStr.includes('Z')) {
        cleanStr = dateStr.replace(' ', 'T') + 'Z';
    }
    
    const date = new Date(cleanStr);
    const now = new Date();
    const diffMs = now - date;
    const diffSec = Math.floor(diffMs / 1000);
    const diffMin = Math.floor(diffSec / 60);
    const diffHrs = Math.floor(diffMin / 60);
    const diffDays = Math.floor(diffHrs / 24);
    
    // Arabic relative time handles
    const isAr = state.language === 'ar';
    
    if (diffSec < 60) return isAr ? 'الآن' : 'Just now';
    if (diffMin < 60) return isAr ? `منذ ${diffMin} د` : `${diffMin}m ago`;
    if (diffHrs < 24) return isAr ? `منذ ${diffHrs} س` : `${diffHrs}h ago`;
    if (diffDays === 1) return isAr ? 'أمس' : 'Yesterday';
    return date.toLocaleDateString(isAr ? 'ar-EG' : undefined, {month: 'short', day: 'numeric'});
}

function formatClockTime(dateStr) {
    if (!dateStr) return '';
    let cleanStr = dateStr;
    if (!dateStr.includes('T') && !dateStr.includes('Z')) {
        cleanStr = dateStr.replace(' ', 'T') + 'Z';
    }
    const date = new Date(cleanStr);
    return date.toLocaleTimeString(state.language === 'ar' ? 'ar-EG' : undefined, {hour: '2-digit', minute:'2-digit'});
}

function formatDate(dateStr) {
    if (!dateStr) return '';
    let cleanStr = dateStr;
    if (!dateStr.includes('T') && !dateStr.includes('Z')) {
        cleanStr = dateStr.replace(' ', 'T') + 'Z';
    }
    const date = new Date(cleanStr);
    return date.toLocaleDateString(state.language === 'ar' ? 'ar-EG' : undefined, {year: 'numeric', month: 'short', day: 'numeric'});
}

function detectChannelFromMessagePreview(conv) {
    if (conv.last_message_preview && conv.last_message_preview.includes("Subject:")) {
        return 'gmail';
    }
    if (conv.contact_phone && conv.contact_phone.startsWith("+1415")) {
        if (conv.contact_name.includes("Rivera")) return 'whatsapp';
        if (conv.contact_name.includes("Chen")) return 'instagram';
    }
    if (conv.contact_name.includes("Sarah")) return 'gmail';
    if (conv.contact_name.includes("Alex")) return 'whatsapp';
    if (conv.contact_name.includes("Liam")) return 'instagram';
    
    return 'messenger';
}

function getChannelIconName(channel) {
    if (channel === 'gmail') return 'mail';
    if (channel === 'whatsapp') return 'message-square';
    if (channel === 'messenger') return 'facebook';
    if (channel === 'instagram') return 'instagram';
    return 'message-square';
}

window.requestAiDraft = async function(convId) {
    const btn = document.getElementById('ai-assist-btn');
    const input = document.getElementById('chat-reply-input');
    if (!btn || !input) return;
    
    btn.classList.add('loading');
    input.disabled = true;
    const originalPlaceholder = input.placeholder;
    input.placeholder = state.language === 'ar' ? 'جاري توليد الرد الذكي...' : 'AI is drafting reply...';
    
    try {
        const res = await API.getAiDraft(convId);
        input.value = res.draft;
        
        // Auto grow textarea height to fit content
        input.style.height = 'auto';
        input.style.height = input.scrollHeight + 'px';
    } catch (err) {
        console.error("AI Draft error:", err);
        alert(state.language === 'ar' ? "فشل توليد الرد الذكي" : "Failed to generate AI draft");
    } finally {
        btn.classList.remove('loading');
        input.disabled = false;
        input.placeholder = originalPlaceholder;
        input.focus();
    }
};
