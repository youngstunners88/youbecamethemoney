import axios from 'axios';

/**
 * Email Gateway wrapper (using SendGrid)
 * Can be swapped for other email providers
 */
class EmailClient {
  constructor() {
    this.apiKey = process.env.SENDGRID_API_KEY;
    this.fromEmail = process.env.SENDGRID_FROM_EMAIL || 'noreply@youbecamethemoney.com';
  }

  async sendEmail(to, subject, htmlContent) {
    if (!this.apiKey) {
      console.warn('Email not configured. Skipping email fallback.');
      return { success: false, reason: 'Email not configured' };
    }

    try {
      const response = await axios.post(
        'https://api.sendgrid.com/v3/mail/send',
        {
          personalizations: [
            {
              to: [{ email: to }],
              subject: subject,
            },
          ],
          from: { email: this.fromEmail },
          content: [
            {
              type: 'text/html',
              value: htmlContent,
            },
          ],
        },
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json',
          },
        }
      );

      console.log(`✅ Email sent to ${to}`);
      return { success: true, messageId: 'email_sent' };
    } catch (err) {
      console.error(`❌ Email failed for ${to}:`, err.response?.data || err.message);
      return { success: false, error: err.message };
    }
  }
}

export default new EmailClient();
