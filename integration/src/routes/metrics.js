import express from 'express';
import { pool } from '../index.js';

const router = express.Router();

// GET dashboard metrics
router.get('/', async (req, res) => {
  try {
    const metrics = await calculateMetrics();
    res.json(metrics);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET leads by temperature
router.get('/temperature', async (req, res) => {
  try {
    const result = await pool.query(
      `SELECT lead_temperature, COUNT(*) as count
       FROM leads
       GROUP BY lead_temperature
       ORDER BY COUNT(*) DESC`
    );

    res.json(
      Object.fromEntries(
        result.rows.map(row => [row.lead_temperature || 'unknown', row.count])
      )
    );
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET leads by status
router.get('/status', async (req, res) => {
  try {
    const result = await pool.query(
      `SELECT status, COUNT(*) as count
       FROM leads
       GROUP BY status
       ORDER BY COUNT(*) DESC`
    );

    res.json(
      Object.fromEntries(
        result.rows.map(row => [row.status, row.count])
      )
    );
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET leads by service type
router.get('/service-type', async (req, res) => {
  try {
    const result = await pool.query(
      `SELECT service_type, COUNT(*) as count
       FROM leads
       GROUP BY service_type
       ORDER BY COUNT(*) DESC`
    );

    res.json(
      Object.fromEntries(
        result.rows.map(row => [row.service_type, row.count])
      )
    );
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET call performance metrics
router.get('/calls', async (req, res) => {
  try {
    const result = await pool.query(
      `SELECT
        COUNT(*) as total_calls,
        COUNT(CASE WHEN call_status = 'completed' THEN 1 END) as completed,
        COUNT(CASE WHEN call_status = 'failed' THEN 1 END) as failed,
        AVG(duration_seconds) as avg_duration,
        COUNT(CASE WHEN temperature_detected = 'hot' THEN 1 END) as hot_leads,
        COUNT(CASE WHEN temperature_detected = 'warm' THEN 1 END) as warm_leads,
        COUNT(CASE WHEN temperature_detected = 'luke' THEN 1 END) as luke_leads,
        COUNT(CASE WHEN temperature_detected = 'cold' THEN 1 END) as cold_leads
       FROM calls`
    );

    res.json(result.rows[0]);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Helper function
async function calculateMetrics() {
  const [leadsResult, casesResult, statusResult, tempResult] = await Promise.all([
    pool.query('SELECT COUNT(*) as count FROM leads'),
    pool.query('SELECT COUNT(*) as count, AVG(value) as avg_value FROM cases WHERE outcome = \'won\''),
    pool.query('SELECT status, COUNT(*) as count FROM leads GROUP BY status'),
    pool.query('SELECT lead_temperature, COUNT(*) as count FROM leads GROUP BY lead_temperature'),
  ]);

  const totalLeads = parseInt(leadsResult.rows[0].count);
  const wonCases = casesResult.rows[0].count;
  const avgCaseValue = casesResult.rows[0].avg_value || 0;

  const statusMap = Object.fromEntries(
    statusResult.rows.map(row => [row.status, parseInt(row.count)])
  );

  const temperatureMap = Object.fromEntries(
    tempResult.rows.map(row => [row.lead_temperature || 'unknown', parseInt(row.count)])
  );

  const conversionRate = totalLeads > 0 ? ((wonCases / totalLeads) * 100).toFixed(2) : 0;

  return {
    totalLeads,
    wonCases,
    conversionRate: parseFloat(conversionRate),
    avgCaseValue: parseFloat(avgCaseValue),
    pipelineValue: wonCases * avgCaseValue,
    leadsByStatus: statusMap,
    leadsByTemperature: temperatureMap,
    hotLeads: temperatureMap['hot'] || 0,
    warmLeads: temperatureMap['warm'] || 0,
    lukeLeads: temperatureMap['luke'] || 0,
    coldLeads: temperatureMap['cold'] || 0,
  };
}

export default router;
