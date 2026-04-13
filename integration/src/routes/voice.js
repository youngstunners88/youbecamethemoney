import express from 'express';
import retellClient from '../clients/retell.js';
import { VOICE_AGENT_CONFIG, VOICE_AGENT_SYSTEM_PROMPT } from '../prompts/voiceAgent.js';
import { handleCallWebhook } from '../handlers/communicationFallback.js';

const router = express.Router();

// CREATE voice agent
router.post('/agent/create', async (req, res) => {
  try {
    const config = req.body || VOICE_AGENT_CONFIG;
    const agent = await retellClient.createAgent(config);

    res.status(201).json({
      success: true,
      agent,
      message: 'Voice agent created successfully',
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET default voice agent config
router.get('/agent/config', (req, res) => {
  res.json({
    name: VOICE_AGENT_CONFIG.name,
    department: VOICE_AGENT_CONFIG.department,
    language: VOICE_AGENT_CONFIG.language,
    maxDurationSeconds: VOICE_AGENT_CONFIG.maxDurationSeconds,
    systemPromptPreview: VOICE_AGENT_SYSTEM_PROMPT.substring(0, 200) + '...',
  });
});

// GET call details
router.get('/calls/:callId', async (req, res) => {
  try {
    const call = await retellClient.getCall(req.params.callId);
    res.json(call);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET call transcript
router.get('/calls/:callId/transcript', async (req, res) => {
  try {
    const transcript = await retellClient.getTranscript(req.params.callId);
    res.json(transcript);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// WEBHOOK: Handle Retell call completed
// Retell will POST to this endpoint when call ends
router.post('/webhook/call-ended', async (req, res) => {
  try {
    console.log('📞 Received call webhook:', req.body);

    const result = await handleCallWebhook(req.body);

    res.json({
      success: true,
      message: 'Call processed',
      result,
    });
  } catch (err) {
    console.error('Error processing call webhook:', err);
    res.status(500).json({ error: err.message });
  }
});

// END a call (admin use)
router.post('/calls/:callId/end', async (req, res) => {
  try {
    const result = await retellClient.endCall(req.params.callId);
    res.json(result);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// LIST recent calls
router.get('/', async (req, res) => {
  try {
    const { limit = 50 } = req.query;
    const calls = await retellClient.listCalls({ limit });
    res.json(calls);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

export default router;
