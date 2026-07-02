/**
 * QariCrm API Client Wrapper
 * Encapsulates fetch logic for simple usage across views
 */
const API = {
    async request(url, options = {}) {
        const defaultHeaders = {
            'Content-Type': 'application/json',
        };
        
        const response = await fetch(url, {
            ...options,
            headers: {
                ...defaultHeaders,
                ...options.headers,
            },
        });
        
        if (!response.ok) {
            let errorText = '';
            try {
                const errData = await response.json();
                errorText = errData.error || response.statusText;
            } catch (e) {
                errorText = await response.text() || response.statusText;
            }
            throw new Error(errorText);
        }
        
        if (response.status === 204) {
            return null;
        }
        
        return await response.json();
    },

    // Contacts API
    getContacts() {
        return this.request('/api/contacts');
    },
    
    createContact(contactData) {
        return this.request('/api/contacts', {
            method: 'POST',
            body: JSON.stringify(contactData),
        });
    },

    // Conversations & Messages API
    getConversations() {
        return this.request('/api/conversations');
    },
    
    getMessages(conversationId) {
        return this.request(`/api/conversations/${conversationId}/messages`);
    },
    
    sendMessage(conversationId, content) {
        return this.request(`/api/conversations/${conversationId}/messages`, {
            method: 'POST',
            body: JSON.stringify({ content }),
        });
    },
    
    getAiDraft(conversationId) {
        return this.request(`/api/conversations/${conversationId}/ai-draft`, {
            method: 'POST',
        });
    },

    // Sales Deals API
    getDeals() {
        return this.request('/api/deals');
    },
    
    createDeal(dealData) {
        return this.request('/api/deals', {
            method: 'POST',
            body: JSON.stringify(dealData),
        });
    },
    
    updateDealStage(dealId, stage) {
        return this.request(`/api/deals/${dealId}/stage`, {
            method: 'PUT',
            body: JSON.stringify({ stage }),
        });
    },

    // Settings & Credentials API
    getSettings() {
        return this.request('/api/settings');
    },
    
    saveSettings(settingsData) {
        return this.request('/api/settings', {
            method: 'POST',
            body: JSON.stringify(settingsData),
        });
    },

    // Simulator API
    toggleSimulator(enabled) {
        return this.request('/api/simulator/toggle', {
            method: 'POST',
            body: JSON.stringify({ enabled }),
        });
    },
    
    triggerSimulatedMessage(channel = null) {
        const body = channel ? { channel } : {};
        return this.request('/api/simulator/trigger', {
            method: 'POST',
            body: JSON.stringify(body),
        });
    }
};
