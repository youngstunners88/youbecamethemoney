import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { Pool } from 'pg';
import leadsRouter from './routes/leads.js';
import voiceRouter from './routes/voice.js';
import metricsRouter from './routes/metrics.js';
import { initializeDatabase } from './db/init.js';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

// Database pool
export const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

// Middleware
app.use(cors());
app.use(express.json());

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Routes
app.use('/api/leads', leadsRouter);
app.use('/api/voice', voiceRouter);
app.use('/api/metrics', metricsRouter);

// Error handler
app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).json({ error: err.message });
});

// Start server
const start = async () => {
  try {
    // Test database connection
    await pool.query('SELECT 1');

    // Initialize database
    await initializeDatabase(pool);

    app.listen(PORT, () => {
      console.log(`✅ YBTM API running on port ${PORT}`);
      console.log(`📞 Retell voice integration enabled`);
      console.log(`🔄 Communication fallback: Phone → SMS → Email`);
    });
  } catch (err) {
    console.error('❌ Failed to start server:', err);
    process.exit(1);
  }
};

start();
