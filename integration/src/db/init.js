export async function initializeDatabase(pool) {
  const client = await pool.connect();

  try {
    // Create tables
    await client.query(`
      CREATE TABLE IF NOT EXISTS leads (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        source VARCHAR(20) NOT NULL,
        name VARCHAR(100) NOT NULL,
        phone VARCHAR(20),
        email VARCHAR(100),
        service_type VARCHAR(50) NOT NULL,
        lead_temperature VARCHAR(10) CHECK (lead_temperature IN ('cold', 'luke', 'warm', 'hot')),
        status VARCHAR(20) DEFAULT 'new',
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW(),
        message TEXT
      );

      CREATE TABLE IF NOT EXISTS calls (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
        retell_call_id VARCHAR(100) UNIQUE,
        call_started_at TIMESTAMP,
        call_ended_at TIMESTAMP,
        duration_seconds INTEGER,
        call_status VARCHAR(20),
        temperature_detected VARCHAR(10) CHECK (temperature_detected IN ('cold', 'luke', 'warm', 'hot')),
        engagement_method VARCHAR(20),
        created_at TIMESTAMP DEFAULT NOW()
      );

      CREATE TABLE IF NOT EXISTS interaction_logs (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
        timestamp TIMESTAMP DEFAULT NOW(),
        platform VARCHAR(20) NOT NULL,
        message_type VARCHAR(20),
        message TEXT NOT NULL,
        response TEXT,
        status VARCHAR(20)
      );

      CREATE TABLE IF NOT EXISTS cases (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
        service_type VARCHAR(50) NOT NULL,
        value INTEGER,
        intake_date TIMESTAMP,
        close_date TIMESTAMP,
        outcome VARCHAR(10) CHECK (outcome IN ('won', 'lost', 'pending'))
      );

      CREATE INDEX IF NOT EXISTS idx_leads_source ON leads(source);
      CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
      CREATE INDEX IF NOT EXISTS idx_leads_temperature ON leads(lead_temperature);
      CREATE INDEX IF NOT EXISTS idx_calls_lead_id ON calls(lead_id);
      CREATE INDEX IF NOT EXISTS idx_calls_retell_id ON calls(retell_call_id);
      CREATE INDEX IF NOT EXISTS idx_interaction_logs_lead_id ON interaction_logs(lead_id);
    `);

    console.log('✅ Database initialized');
  } finally {
    client.release();
  }
}

// Add indexes for performance
export async function addIndexes() {
  await pool.query(`
    CREATE INDEX IF NOT EXISTS idx_leads_created_at ON leads(created_at DESC);
    CREATE INDEX IF NOT EXISTS idx_calls_created_at ON calls(created_at DESC);
  `);
}
