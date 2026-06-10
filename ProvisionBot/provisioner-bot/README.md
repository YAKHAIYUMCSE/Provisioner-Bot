# Self-Service Provisioner Bot

## Overview
AI-powered infrastructure provisioning portal.

## Features
- Modern dark theme dashboard
- AI Assistant with mock fallback
- Policy engine validation
- Docker + Terraform infrastructure generation
- GitHub Issue + PR automation
- Request tracker with search and filters
- Full mock mode when API keys are absent

## Setup

```bash
git clone <repo>
cd provisioner-bot
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your keys (optional)
uvicorn app:app --reload --port 8000
```

## API Endpoints

| Method | Endpoint       | Description              |
|--------|---------------|--------------------------|
| GET    | /             | Dashboard                |
| GET    | /requests     | Request tracker          |
| GET    | /api/requests | List all requests (JSON) |
| POST   | /api/validate | Validate policy          |
| POST   | /api/parse    | Parse natural language   |
| POST   | /api/chat     | AI assistant             |
| POST   | /api/submit   | Submit request           |
| GET    | /api/status   | Mock mode status         |

## Mock Mode
App works fully without any API keys.
Add keys to .env to enable live GitHub and HuggingFace features.
