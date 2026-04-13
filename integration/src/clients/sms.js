import axios from 'axios';

/**
 * SMS Gateway wrapper (using Twilio)
 * Can be swapped for other SMS providers
 */
class SMSClient {
  constructor() {
    this.accountSid = process.env.TWILIO_ACCOUNT_SID;
    this.authToken = process.env.TWILIO_AUTH_TOKEN;
    this.fromNumber = process.env.TWILIO_PHONE_NUMBER;
  }

  async sendSMS(toNumber, message) {
    if (!this.accountSid || !this.authToken) {
      console.warn('SMS not configured. Skipping SMS fallback.');
      return { success: false, reason: 'SMS not configured' };
    }

    try {
      const response = await axios.post(
        `https://api.twilio.com/2010-04-01/Accounts/${this.accountSid}/Messages.json`,
        new URLSearchParams({
          From: this.fromNumber,
          To: toNumber,
          Body: message,
        }),
        {
          auth: {
            username: this.accountSid,
            password: this.authToken,
          },
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        }
      );

      console.log(`✅ SMS sent to ${toNumber}`);
      return { success: true, messageId: response.data.sid };
    } catch (err) {
      console.error(`❌ SMS failed for ${toNumber}:`, err.message);
      return { success: false, error: err.message };
    }
  }
}

export default new SMSClient();
