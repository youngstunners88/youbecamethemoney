import axios from 'axios';

const RETELL_API_BASE = 'https://api.retellai.com/v2';

class RetellClient {
  constructor(apiKey) {
    this.apiKey = apiKey;
    this.client = axios.create({
      baseURL: RETELL_API_BASE,
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
    });
  }

  /**
   * Create an agent for lead qualification
   */
  async createAgent(config) {
    try {
      const response = await this.client.post('/agent/create', {
        agent_name: config.name || 'YBTM Garcia Qualifier',
        agent_role: config.role || 'intake_specialist',
        agent_department: 'lead_qualification',
        language: 'en-US',
        max_duration_seconds: 900, // 15 min max call
        prompt: config.systemPrompt,
        llm_websocket_url: config.llmWebsocketUrl || null,
        voice_id: config.voiceId || 'default',
        ambient_sound: 'office',
        enable_voicemail: true,
        voicemail_message: 'We\'re currently unavailable. Please leave your name and contact info.',
        temperature: 0.7, // Balanced between creative and consistent
      });
      return response.data;
    } catch (err) {
      console.error('Error creating Retell agent:', err.response?.data || err.message);
      throw err;
    }
  }

  /**
   * Initiate an outbound call
   */
  async initiateCall(phoneNumber, agentId, metadata = {}) {
    try {
      const response = await this.client.post('/call/begin', {
        agent_id: agentId,
        phone_number: phoneNumber,
        from_number: process.env.RETELL_PHONE_NUMBER,
        language: 'en-US',
        user_id: metadata.leadId || null,
        custom_metadata: metadata,
        retries: 2,
      });
      return response.data;
    } catch (err) {
      console.error('Error initiating Retell call:', err.response?.data || err.message);
      throw err;
    }
  }

  /**
   * Get call details
   */
  async getCall(callId) {
    try {
      const response = await this.client.get(`/call/${callId}`);
      return response.data;
    } catch (err) {
      console.error('Error fetching call:', err.response?.data || err.message);
      throw err;
    }
  }

  /**
   * Get call transcript
   */
  async getTranscript(callId) {
    try {
      const response = await this.client.get(`/call/${callId}/transcript`);
      return response.data;
    } catch (err) {
      console.error('Error fetching transcript:', err.response?.data || err.message);
      throw err;
    }
  }

  /**
   * End a call
   */
  async endCall(callId) {
    try {
      const response = await this.client.post(`/call/${callId}/end`);
      return response.data;
    } catch (err) {
      console.error('Error ending call:', err.response?.data || err.message);
      throw err;
    }
  }

  /**
   * List calls
   */
  async listCalls(filters = {}) {
    try {
      const response = await this.client.get('/calls', { params: filters });
      return response.data;
    } catch (err) {
      console.error('Error listing calls:', err.response?.data || err.message);
      throw err;
    }
  }
}

export default new RetellClient(process.env.RETELL_API_KEY);
