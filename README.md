# MedScribe

**MedScribe** is a doctor–patient conversation recorder: it transcribes audio, builds medical reports, suggests possible conditions (reference only), and supports PDF export and WhatsApp sharing.

**Repository:** rename your GitHub repo to `medscribe` if you like (Settings → General → Repository name). Then point your local remote at the new URL:

```bash
git remote set-url origin https://github.com/YOUR_USERNAME/medscribe.git
```

(Replace `YOUR_USERNAME` with your GitHub username.)

## Features

- **Login** – Simple authentication (demo: doctor / doctor123)
- **Record** – Click mic to record voice; speech is transcribed automatically
- **Add manually** – Type doctor/patient messages directly
- **Dashboard** – View full conversation, generate summary
- **Medical report** – AI-generated report with conversation summary
- **Disease suggestions** – Possible conditions based on mentioned symptoms (for reference only)
- **Send to WhatsApp** – Share the report via WhatsApp

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open http://localhost:8501

## Deploy

### Vercel (landing page only)

**Streamlit cannot run on Vercel** — it needs a long-lived server and WebSockets. Vercel is serverless/static-only for this stack.

This repo includes a small **static page** in `public/` that explains where to host the real app.

Deploy that folder to Vercel:

1. [Vercel](https://vercel.com) → Add New → Project → import this repo.
2. **Root Directory**: set to `public` (or run `cd public && npx vercel --prod` from your machine).
3. Deploy. You get a URL for the info page; users still open the Streamlit host for the app.

### Run the full Streamlit app in production

Pick one:

| Host | How |
|------|-----|
| **Streamlit Community Cloud** | [streamlit.io/cloud](https://streamlit.io/cloud) → connect GitHub → Main file `app.py`, Python 3.12. |
| **Render** | New **Web Service** → **Docker** → use this repo’s `Dockerfile` (or import `render.yaml`). |
| **Railway / Fly.io** | New service from repo → build with `Dockerfile`. |

Docker listens on `PORT` (Render sets this automatically).

## Disclaimer

Disease suggestions are for educational/demo purposes only. **Not medical advice.** Always consult a qualified healthcare professional.
