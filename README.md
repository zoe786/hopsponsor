# HOPe Sponsor Assistant

A **Next.js** sponsor relationship management and student support dashboard, deployable to **Vercel**.

## Features

- 👥 **Sponsor Management** — Add, edit, delete, and search sponsors; CSV export
- 🎓 **Student Management** — Track students with grade/sponsor assignments; CSV export
- ✉️ **Messaging** — Send emails (via Resend) and WhatsApp (via Twilio) with built-in message templates
- 📁 **Reports** — Upload student reports with AI-powered file-to-student matching and sent-status tracking
- 🗓️ **Scheduling** — Schedule messages for future delivery with a background worker
- 💳 **Payment Commitments** — Track sponsor commitments, due dates, and received amounts
- 📅 **Calendar Sync** — Manage calendar events and subscribe to an ICS feed from Google Calendar, Apple Calendar, Outlook, and more
- 🧠 **AI Intelligence** — Generate message drafts in your style + an AI chat assistant that can also schedule messages and create tracking records
- 🎨 **Style Library** — Store writing examples to guide the AI
- 📜 **Message History** — Full log of all outbound communications
- 📊 **Analytics Dashboard** — Live stats and 30-day message activity chart

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 15 (App Router), React 19, TypeScript |
| Styling | Custom CSS (HOPe dark purple theme) |
| Database | SQLite via `better-sqlite3` |
| AI | OpenAI GPT-4 |
| Email | Resend |
| WhatsApp | Twilio |
| Charts | Recharts |
| Notifications | react-hot-toast |
| Deployment | Vercel |

## Quick Start

### 1. Install dependencies

```bash
npm install
```

### 2. Configure environment variables

```bash
cp .env.example .env.local
```

Fill in the API keys in `.env.local` only when you are ready to use those features:

```env
OPENAI_API_KEY=sk-...
RESEND_API_KEY=re_...
RESEND_SENDER_EMAIL=noreply@yourdomain.com
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_WHATSAPP_FROM=+14155238886
```

### 3. Run in development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

Without API keys, sponsor/student storage, reports, payment tracking, calendar events, and the ICS calendar feed still work. Add the OpenAI, Resend, and Twilio keys later when you want AI or outbound messaging.

### 4. Build for production

```bash
npm run build
npm start
```

## Deploying to Vercel

### Option A: One-click deploy

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new)

1. Push this repository to GitHub
2. Import it in the [Vercel dashboard](https://vercel.com/new)
3. Add your environment variables in Vercel's settings
4. Deploy!

### Option B: Vercel CLI

```bash
npm install -g vercel
vercel deploy
```

### ⚠️ Database persistence on Vercel

By default, this app uses a local SQLite file at `./data/sponsor_assistant.db`. Vercel's serverless functions have an **ephemeral** filesystem (`/tmp`), so the database will not persist across deployments.

**For production, use [Turso](https://turso.tech/) (free tier available):**

1. Create a Turso database: `turso db create hopsponsor`
2. Get your URL and auth token: `turso db show hopsponsor`
3. Add to Vercel environment variables:
   ```
   TURSO_DATABASE_URL=libsql://hopsponsor-xxx.turso.io
   TURSO_AUTH_TOKEN=...
   ```
4. Update `src/lib/db.ts` to use `@libsql/client` instead of `better-sqlite3`

## Bug Fixes (vs Python/Streamlit original)

1. **`update_sponsor`** — Now correctly uses numeric ID instead of name string
2. **`delete_sponsor`** — Now correctly uses numeric ID instead of name string
3. **Style library "Golden" column** — Fixed key mismatch (`Golden Example` vs `Golden`)
4. **`get_scheduled_messages`** — Now always includes `ORDER BY send_time` in all query paths
5. **File matching** — Returns ordered array of `{fileName, studentName}` objects (safe to iterate in sync with files)
6. **Chat XSS** — User messages are rendered as text, not raw HTML
7. **Student code generation** — Handles non-standard codes gracefully

## Calendar Sync

HOPe exposes an **ICS calendar feed** at `/api/calendar/feed`. Once the app is deployed, copy that URL into Google Calendar (Add calendar → From URL), Apple Calendar, Outlook, or any other app that supports iCalendar subscriptions. The feed includes manual calendar events and pending scheduled messages.

## Environment Variables Reference

| Variable | Required | Description |
|---|---|---|
| `OPENAI_API_KEY` | Yes | OpenAI API key |
| `RESEND_API_KEY` | Yes (email) | Resend API key |
| `RESEND_SENDER_EMAIL` | Yes (email) | Verified sender email |
| `TWILIO_ACCOUNT_SID` | Yes (WhatsApp) | Twilio account SID |
| `TWILIO_AUTH_TOKEN` | Yes (WhatsApp) | Twilio auth token |
| `TWILIO_WHATSAPP_FROM` | No | WhatsApp number (default: +14155238886) |
| `DB_PATH` | No | SQLite DB path (default: `./data/sponsor_assistant.db`) |
