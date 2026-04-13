import { pool } from '../index.js';
import retellClient from '../clients/retell.js';
import smsClient from '../clients/sms.js';
import emailClient from '../clients/email.js';

/**
 * Communication Fallback Handler
 * Strategy: Phone (3s) → SMS → Email
 *
 * This ensures maximum reachability for hot leads
 */
export async function initiateMultiChannelOutreach(lead, voiceAgentId) {
  const leadId = lead.id;
  const phone = lead.phone;
  const email = lead.email;
  const name = lead.name;

  try {
    // 1. TRY PHONE CALL (3 second timeout)
    console.log(`📞 Initiating phone call to ${name} (${phone})...`);

    const phonePromise = retellClient.initiateCall(phone, voiceAgentId, {
      leadId,
      name,
      source: 'phone_first_fallback',
    });

    // Wait up to 3 seconds for call to be initiated
    const callStartTimeout = new Promise((_, reject) => {
      setTimeout(() => reject(new Error('Phone call timeout')), 3000);
    });

    let callResult;
    try {
      callResult = await Promise.race([phonePromise, callStartTimeout]);

      // Log successful call initiation
      await pool.query(
        `INSERT INTO interaction_logs (lead_id, platform, message_type, message, status)
         VALUES ($1, $2, $3, $4, $5)`,
        [leadId, 'phone', 'call_initiated', `Outbound call initiated to ${phone}`, 'success']
      );

      // Update lead engagement method
      await pool.query(
        `UPDATE leads SET updated_at = NOW() WHERE id = $1`,
        [leadId]
      );

      return {
        success: true,
        method: 'phone',
        callId: callResult.call_id,
        message: `Call initiated to ${phone}`,
      };
    } catch (phoneErr) {
      console.warn(`⏱️  Phone call timeout or error: ${phoneErr.message}`);

      // Log failed call attempt
      await pool.query(
        `INSERT INTO interaction_logs (lead_id, platform, message_type, message, status)
         VALUES ($1, $2, $3, $4, $5)`,
        [leadId, 'phone', 'call_failed', `Phone call failed: ${phoneErr.message}`, 'failed']
      );

      // 2. FALLBACK TO SMS
      return await fallbackToSMS(lead);
    }
  } catch (err) {
    console.error('Error in communication fallback:', err);
    throw err;
  }
}

async function fallbackToSMS(lead) {
  const { id: leadId, name, phone, email } = lead;

  console.log(`💬 Falling back to SMS for ${name}...`);

  const smsContent = `Hi ${name.split(' ')[0]}! Daniel Garcia from You Became The Money here. 🚀 We have an exclusive opportunity to discuss your commercial law needs. Reply STOP to opt out, or tell us more about your situation.`;

  const smsResult = await smsClient.sendSMS(phone, smsContent);

  if (smsResult.success) {
    await pool.query(
      `INSERT INTO interaction_logs (lead_id, platform, message_type, message, status)
       VALUES ($1, $2, $3, $4, $5)`,
      [leadId, 'sms', 'message_sent', smsContent, 'success']
    );

    return {
      success: true,
      method: 'sms',
      messageId: smsResult.messageId,
      message: `SMS sent to ${phone}`,
    };
  } else {
    console.warn(`SMS failed for ${name}. Falling back to email...`);
    return await fallbackToEmail(lead);
  }
}

async function fallbackToEmail(lead) {
  const { id: leadId, name, phone, email } = lead;

  console.log(`📧 Falling back to email for ${name}...`);

  const emailSubject = 'Your Commercial Law Breakthrough - From You Became The Money';
  const emailContent = `
    <h2>Hello ${name},</h2>
    <p>Daniel Garcia from <strong>You Became The Money</strong> here.</p>
    <p>We noticed you're interested in commercial law and financial sovereignty. We have some powerful insights to share about UCC Articles, securitization strategies, and how to transition from debtor to creditor.</p>
    <p><strong>Your Next Step:</strong> Reply to this email or call us at 954-260-9327 for a brief consultation.</p>
    <p>From goods to <strong>GODS</strong> - let's get you started on your journey.</p>
    <p>Best regards,<br>Daniel Garcia<br>You Became The Money</p>
  `;

  const emailResult = await emailClient.sendEmail(email, emailSubject, emailContent);

  if (emailResult.success) {
    await pool.query(
      `INSERT INTO interaction_logs (lead_id, platform, message_type, message, status)
       VALUES ($1, $2, $3, $4, $5)`,
      [leadId, 'email', 'message_sent', emailSubject, 'success']
    );

    return {
      success: true,
      method: 'email',
      messageId: emailResult.messageId,
      message: `Email sent to ${email}`,
    };
  } else {
    console.error(`All communication methods failed for ${name}`);

    await pool.query(
      `INSERT INTO interaction_logs (lead_id, platform, message_type, message, status)
       VALUES ($1, $2, $3, $4, $5)`,
      [leadId, 'all', 'communication_failed', 'All channels exhausted', 'failed']
    );

    return {
      success: false,
      method: 'none',
      message: 'Unable to reach prospect through any channel',
    };
  }
}

/**
 * Handle incoming Retell call webhook
 * Update call status and lead temperature in database
 */
export async function handleCallWebhook(webhookData) {
  const { call_id, user_id, call_status, end_timestamp, transcript, duration_seconds } = webhookData;

  try {
    const leadId = user_id;

    // Get call details from Retell
    const callDetails = await retellClient.getCall(call_id);

    // Insert call record
    await pool.query(
      `INSERT INTO calls (lead_id, retell_call_id, call_status, duration_seconds, call_started_at, call_ended_at)
       VALUES ($1, $2, $3, $4, NOW(), NOW())`,
      [leadId, call_id, call_status, duration_seconds]
    );

    // If call completed, analyze transcript for lead temperature
    if (call_status === 'completed' && transcript) {
      const temperature = analyzeTranscriptForTemperature(transcript);

      // Update call with detected temperature
      await pool.query(
        `UPDATE calls SET temperature_detected = $1 WHERE retell_call_id = $2`,
        [temperature, call_id]
      );

      // Update lead temperature
      await pool.query(
        `UPDATE leads SET lead_temperature = $1 WHERE id = $2`,
        [temperature, leadId]
      );

      console.log(`✅ Call completed. Lead temperature: ${temperature}`);
    }

    return { success: true, leadId, temperature: callDetails.temperature };
  } catch (err) {
    console.error('Error handling call webhook:', err);
    throw err;
  }
}

/**
 * Simple heuristic to detect lead temperature from transcript
 * This can be enhanced with Claude API analysis
 */
function analyzeTranscriptForTemperature(transcript) {
  const text = transcript.toLowerCase();

  const hotKeywords = ['ready to hire', 'ready to start', 'sign up', 'how much', 'next steps', 'when can we', 'absolutely', 'yes please'];
  const warmKeywords = ['interested', 'tell me more', 'seems helpful', 'makes sense', 'can you explain', 'how does it work'];
  const lukeKeywords = ['maybe', 'possibly', 'might be', 'i guess', 'not sure yet', 'need to think'];
  const coldKeywords = ['not interested', 'no thanks', 'wrong number', 'unsubscribe', 'stop calling'];

  let temperature = 'luke'; // Default

  if (coldKeywords.some(kw => text.includes(kw))) {
    temperature = 'cold';
  } else if (hotKeywords.some(kw => text.includes(kw))) {
    temperature = 'hot';
  } else if (warmKeywords.some(kw => text.includes(kw))) {
    temperature = 'warm';
  }

  return temperature;
}
