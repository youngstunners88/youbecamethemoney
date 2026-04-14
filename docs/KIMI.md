# Daniel Garcia Website Strategy

## User Context (REMEMBER)
- **User OS:** Windows 8 (cannot run modern apps locally)
- **Workflow:** SSH into Google VM for all development
- **Constraint:** Token-sensitive (keep responses minimal)
- **Tools:** Free, open-source only

## Overview
Client pre-screening system for credit structuring specialist. Tiered service pathways filter bad-fit prospects before consultations. Goal: eliminate 50%+ of unsuitable leads.

## Tech Stack (Free-First)
React/Next.js + TypeScript | n8n (self-hosted) | Resend | Calendly | Vercel | GA4

## Commands
`npm run dev` | `npm run build` | `n8n start` | `vercel --prod`

## Conventions
- **Pages:** kebab-case (`tier-1.tsx`, `intake-tier1.tsx`)
- **Components:** PascalCase (`TierCard.tsx`, `IntakeForm.tsx`)
- **Messaging:** "Sovereignty" framing, honest timelines (6-18 months), "Investment" not "Cost"
- **Forms:** Tier-specific questions + red flag scoring (0-10)
- **Routing:** 0-1 = schedule | 2-3 = gatekeeper call | 4+ = redirect
- **No generic contact forms** - every form captures qualification data

## n8n Automation Flow
```
Form Submit → n8n Webhook → Red Flag Score → IF/ELSE Logic
  → Score 0-1: Create Calendly invite + SendGrid/Resend confirmation
  → Score 2-3: Queue for gatekeeper call + Send "next steps" email
  → Score 4+: Redirect to resources page + Send "not ready" email
```

## Status
- Next.js app: `youbecamethemoney/next-app/`
- Dev server: http://your-vm-ip:3000 (running)
- n8n: Install pending (docker issues, use npm n8n or manual webhook)
- Old HTML: `youbecamethemoney/index-old.html`

## Avoid
- ❌ Generic contact forms
- ❌ Exact pricing (use ranges: "Starting at $500")
- ❌ Guarantees (use "typically," "supports")
- ❌ Fast timeline promises
- ❌ "Credit repair" (use "credit structuring")
- ❌ Missing CROA disclaimers
- ❌ Verbose responses (token-sensitive user)
