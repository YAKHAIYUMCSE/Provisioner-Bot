# 🤖 Self-Service Provisioner Bot

> **AI-powered self-service infrastructure provisioning portal** — Developers submit environment requests through a web interface; the system validates against policy rules, auto-generates Terraform/Docker infrastructure files, and raises GitHub Issues and Pull Requests automatically.

---

## 🧩 Problem Statement

In most organizations, developers file tickets to request new environments (Docker, AWS, etc.) and wait **days** for DevOps teams to manually provision them. This project eliminates that wait by automating the entire provisioning pipeline — from request to PR — using an AI-powered web portal.

---

## 💡 Solution Overview

Instead of a Discord bot, we built a **full-stack web-based provisioner portal** that provides a richer, more accessible interface for developers to:

- Submit infrastructure requests in plain English
- Get instant policy validation feedback
- Receive auto-generated Terraform/Docker configuration files
- Track request status in real time
- Trigger GitHub Issue + PR creation automatically

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🧠 AI Assistant | Chat interface powered by HuggingFace Mistral-7B with smart mock fallback |
| ✅ Policy Engine | Validates requests against YAML-defined rules before any action |
| 🏗️ IaC Generator | Auto-generates `docker-compose.yml` or Terraform (`main.tf`, `provider.tf`, `variables.tf`) |
| 🔗 GitHub Automation | Creates GitHub Issues (labeled `auto-provision`) and opens PRs with generated files |
| 📊 Request Tracker | Real-time dashboard showing all requests, statuses, PR and issue links |
| 📧 Email Notifications | Notifies dev team on new requests; notifies requester when environment is ready |
| 🔒 Mock Mode | Fully functional without any API keys — ideal for demos and local development |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI (Python) |
| Database | SQLite + SQLAlchemy (async) |
| Frontend | HTML, CSS, JavaScript (Jinja2 templates) |
| AI Model | HuggingFace Mistral-7B-Instruct |
| IaC | Terraform + Docker Compose |
| GitHub Automation | PyGitHub |
| CI/CD | GitHub Actions |

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.10+
- Git

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/Veeraabinaya/self-service-provisioner-bot.git
cd self-service-provisioner-bot/Project/ProvisionBot/provisioner-bot

# 2. Create and activate virtual environment
python -m venv venv

# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env and add your API keys (optional — works without them)

# 5. Run the app
uvicorn app:app --reload --port 8000
```

Open your browser at: `http://localhost:8000`

---

## 🔑 Environment Variables

```env
GITHUB_TOKEN=your_github_token
GITHUB_REPO=owner/repo-name
HF_API_KEY=your_huggingface_api_key
HF_MODEL=mistralai/Mistral-7B-Instruct-v0.3
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email
SMTP_PASSWORD=your_password
DEV_TEAM_EMAIL=devteam@company.com
```

> All keys are **optional**. The app runs in full **mock mode** without them.

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Main dashboard |
| GET | `/requests` | Request tracker page |
| GET | `/api/requests` | List all requests (JSON) |
| POST | `/api/submit` | Submit a new provision request |
| POST | `/api/validate` | Validate against policy engine |
| POST | `/api/parse` | Parse natural language request |
| POST | `/api/chat` | AI assistant chat |
| GET | `/api/status` | Check mock mode / API key status |
| POST | `/api/complete/{id}` | Mark a request as completed |

---

## 🔄 Provisioning Workflow

```
Developer submits request via web portal
            ↓
Policy Engine validates (env type, name, service count)
            ↓
Infrastructure files auto-generated
   → Docker: docker-compose.yml
   → AWS:    main.tf + provider.tf + variables.tf
            ↓
GitHub Issue created (labeled: auto-provision)
            ↓
GitHub PR opened with generated infra files
            ↓
Dev Team notified via email
            ↓
DevOps reviews & merges PR
            ↓
Requester notified — environment is ready!
```

---

## 📁 Project Structure

```
provisioner-bot/
├── app.py                      # Main FastAPI application
├── parser.py                   # Natural language request parser
├── requirements.txt
├── policy_engine/
│   ├── engine.py               # Policy validation logic
│   └── policy.yaml             # Policy rules (allowed envs, types, max services)
├── terraform_generator/
│   └── generator.py            # Terraform & Docker Compose file generator
├── automation/
│   ├── create_issue.py         # GitHub Issue automation
│   ├── create_pr.py            # GitHub PR automation
│   └── handle_issue.py
├── templates/
│   ├── index.html              # Dashboard UI
│   └── requests.html           # Request tracker UI
├── static/
│   ├── script.js
│   └── style.css
├── generated/                  # Auto-generated infra files (per request ID)
└── .github/workflows/          # CI/CD pipelines
```

---

## 👥 Team

| Name |
|------|
| Janani Sandhiya T |
| Jeshintha X |
| Veera Abinaya M |
| Ya Khaiyum A |
