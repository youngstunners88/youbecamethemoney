import express from 'express';
import { v4 as uuidv4 } from 'uuid';
import { pool } from '../index.js';
import { initiateMultiChannelOutreach } from '../handlers/communicationFallback.js';

const router = express.Router();

// GET all leads
router.get('/', async (req, res) => {
  try {
    const { status, temperature, limit = 50, offset = 0 } = req.query;

    let query = 'SELECT * FROM leads WHERE 1=1';
    const params = [];

    if (status) {
      query += ' AND status = $' + (params.length + 1);
      params.push(status);
    }

    if (temperature) {
      query += ' AND lead_temperature = $' + (params.length + 1);
      params.push(temperature);
    }

    query += ' ORDER BY created_at DESC LIMIT $' + (params.length + 1) + ' OFFSET $' + (params.length + 2);
    params.push(limit, offset);

    const result = await pool.query(query, params);
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET single lead
router.get('/:id', async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM leads WHERE id = $1', [req.params.id]);
    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Lead not found' });
    }
    res.json(result.rows[0]);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// CREATE lead
router.post('/', async (req, res) => {
  try {
    const { source, name, phone, email, serviceType, message } = req.body;

    const leadId = uuidv4();
    const result = await pool.query(
      `INSERT INTO leads (id, source, name, phone, email, service_type, status, message)
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
       RETURNING *`,
      [leadId, source, name, phone, email, serviceType, 'new', message]
    );

    res.status(201).json(result.rows[0]);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// UPDATE lead status
router.put('/:id/status', async (req, res) => {
  try {
    const { status } = req.body;
    const result = await pool.query(
      'UPDATE leads SET status = $1, updated_at = NOW() WHERE id = $2 RETURNING *',
      [status, req.params.id]
    );
    res.json(result.rows[0]);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// UPDATE lead temperature
router.put('/:id/temperature', async (req, res) => {
  try {
    const { temperature } = req.body;
    if (!['cold', 'luke', 'warm', 'hot'].includes(temperature)) {
      return res.status(400).json({ error: 'Invalid temperature' });
    }

    const result = await pool.query(
      'UPDATE leads SET lead_temperature = $1, updated_at = NOW() WHERE id = $2 RETURNING *',
      [temperature, req.params.id]
    );

    res.json(result.rows[0]);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// INITIATE OUTREACH (phone → SMS → email)
router.post('/:id/initiate-outreach', async (req, res) => {
  try {
    const { voiceAgentId } = req.body;

    if (!voiceAgentId) {
      return res.status(400).json({ error: 'voiceAgentId required' });
    }

    const leadResult = await pool.query('SELECT * FROM leads WHERE id = $1', [req.params.id]);
    if (leadResult.rows.length === 0) {
      return res.status(404).json({ error: 'Lead not found' });
    }

    const lead = leadResult.rows[0];
    const outreachResult = await initiateMultiChannelOutreach(lead, voiceAgentId);

    res.json(outreachResult);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET calls for a lead
router.get('/:id/calls', async (req, res) => {
  try {
    const result = await pool.query(
      'SELECT * FROM calls WHERE lead_id = $1 ORDER BY created_at DESC',
      [req.params.id]
    );
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET interactions for a lead
router.get('/:id/interactions', async (req, res) => {
  try {
    const result = await pool.query(
      'SELECT * FROM interaction_logs WHERE lead_id = $1 ORDER BY timestamp DESC',
      [req.params.id]
    );
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

export default router;
