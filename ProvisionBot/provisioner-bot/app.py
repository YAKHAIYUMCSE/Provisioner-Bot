from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from dotenv import load_dotenv
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

from policy_engine.engine import validate_policy
from terraform_generator.generator import generate_infra
from automation.create_issue import create_github_issue
from automation.create_pr import create_github_pr
from parser import parse_request

app = FastAPI(title="Self-Service Provisioner Bot")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

DATABASE_URL = "sqlite+aiosqlite:///./provisioner.db"
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

class ProvisionRequest(Base):
    __tablename__ = "requests"
    id = Column(Integer, primary_key=True, index=True)
    requester = Column(String)
    requester_email = Column(String, default="")
    env_type = Column(String)
    env_name = Column(String)
    details = Column(String)
    status = Column(String, default="pending")
    pr_link = Column(String, default="")
    issue_link = Column(String, default="")
    generated_path = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("startup")
async def startup():
    await init_db()

# Email sending utility
def send_email(to_email: str, subject: str, body: str):
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = os.getenv("SMTP_PORT")
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASSWORD")
    from_email = os.getenv("SMTP_FROM", "noreply@provisionerbot.com")

    if not all([smtp_host, smtp_port, smtp_user, smtp_pass]):
        print(f"[MOCK EMAIL] To: {to_email} | Subject: {subject} | Body:\n{body}")
        return

    try:
        msg = MIMEMultipart()
        msg["From"] = from_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(smtp_host, int(smtp_port)) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        print(f"[EMAIL SENT] Successfully sent email to {to_email}")
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send email to {to_email}: {e}")

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(request, "index.html")

@app.get("/requests", response_class=HTMLResponse)
async def tracker(request: Request):
    return templates.TemplateResponse(request, "requests.html")

@app.get("/api/requests")
async def get_requests():
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        result = await session.execute(select(ProvisionRequest))
        rows = result.scalars().all()
        return [
            {
                "id": r.id,
                "requester": r.requester,
                "env_type": r.env_type,
                "env_name": r.env_name,
                "status": r.status,
                "pr_link": r.pr_link,
                "issue_link": r.issue_link,
                "created_at": str(r.created_at)
            } for r in rows
        ]

@app.post("/api/validate")
async def validate(data: dict):
    return validate_policy(
        data.get("env_type", ""),
        data.get("env_name", ""),
        data.get("services", [])
    )

@app.post("/api/parse")
async def parse(data: dict):
    return parse_request(data.get("text", ""))

@app.post("/api/chat")
async def chat(data: dict):
    message = data.get("message", "").lower()
    history = data.get("history", [])

    api_key = os.getenv("HF_API_KEY")
    if api_key:
        try:
            import requests as req
            headers = {"Authorization": f"Bearer {api_key}"}
            messages = [{"role": "system", "content": "You are Provisioner AI, expert in Docker, AWS, Terraform, GitHub workflows."}]
            for h in history:
                messages.append(h)
            messages.append({"role": "user", "content": message})
            model = os.getenv("HF_MODEL", "mistralai/Mistral-7B-Instruct-v0.3")
            res = req.post(
                f"https://api-inference.huggingface.co/models/{model}",
                headers=headers,
                json={"inputs": message, "parameters": {"max_new_tokens": 300}},
                timeout=15
            )
            result = res.json()
            if isinstance(result, list):
                return {"reply": result[0].get("generated_text", "Sorry, I could not generate a response.")}
        except Exception:
            pass

    # Mock fallback
    replies = {
        "docker": "🐳 To create a Docker environment, fill the form and select Docker as type. I'll generate a docker-compose.yml automatically!",
        "aws": "☁️ For AWS environments, select AWS type in the form. I'll generate Terraform main.tf with VPC and EC2 resources.",
        "terraform": "🏗️ Terraform environments include provider.tf, variables.tf, and main.tf. Select Terraform in the form to get started.",
        "workflow": "📋 Workflow: Submit request → Policy check → Infra generation → GitHub Issue → PR created → DevOps approves.",
        "status": "📊 Check the Request Tracker at /requests to see all your provisioning requests and their statuses.",
        "github": "🔗 GitHub integration creates Issues labeled auto-provision and opens PRs with generated infrastructure files.",
        "help": "💡 I can help with Docker, AWS, Terraform, GitHub workflows, and request status. What do you need?"
    }

    for keyword, reply in replies.items():
        if keyword in message:
            return {"reply": reply}

    return {"reply": "👋 I am Provisioner AI! Ask me about Docker, AWS, Terraform, GitHub workflows, or request status."}

@app.get("/api/status")
async def status_endpoint():
    return {
        "mock_mode": not bool(os.getenv("GITHUB_TOKEN") and os.getenv("HF_API_KEY")),
        "github": bool(os.getenv("GITHUB_TOKEN")),
        "huggingface": bool(os.getenv("HF_API_KEY"))
    }

@app.post("/api/submit")
async def submit(data: dict):
    requester = data.get("requester", "Unknown")
    requester_email = data.get("requester_email", "")
    env_type = data.get("env_type", "docker")
    env_name = data.get("env_name", "dev")
    details = data.get("details", "")

    policy_result = validate_policy(env_type, env_name)
    if policy_result["status"] == "rejected":
        return JSONResponse(status_code=400, content=policy_result)

    parsed = parse_request(details)
    services = parsed.get("services", [])

    async with AsyncSessionLocal() as session:
        req_obj = ProvisionRequest(
            requester=requester,
            requester_email=requester_email,
            env_type=env_type,
            env_name=env_name,
            details=details,
            status="pending"
        )
        session.add(req_obj)
        await session.commit()
        await session.refresh(req_obj)
        request_id = req_obj.id

    generated_path = generate_infra(request_id, env_type, env_name, services)
    issue_url = create_github_issue(env_type, env_name, requester, details)
    pr_url = create_github_pr(request_id, env_type, env_name, generated_path)

    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        result = await session.execute(
            select(ProvisionRequest).where(ProvisionRequest.id == request_id)
        )
        req_obj = result.scalar_one()
        req_obj.status = "approved"
        req_obj.pr_link = pr_url
        req_obj.issue_link = issue_url
        req_obj.generated_path = generated_path
        await session.commit()

    # Notify developer team
    dev_email = os.getenv("DEV_TEAM_EMAIL", "devteam@company.com")
    dev_subject = f"[New Request] Provision {env_type} {env_name} - {requester}"
    dev_body = f"""Hi Team,

A new infrastructure request has been submitted and auto-generated.

- Requester: {requester} ({requester_email})
- Environment Type: {env_type}
- Environment Name: {env_name}
- Services Detected: {', '.join(services) if services else 'Default'}
- Details: {details}

Links:
- GitHub Issue: {issue_url}
- GitHub PR: {pr_url}

Best regards,
Provisioner Bot
"""
    send_email(dev_email, dev_subject, dev_body)

    return {
        "request_id": request_id,
        "status": "approved",
        "pr_link": pr_url,
        "issue_link": issue_url,
        "generated_path": generated_path
    }

@app.post("/api/complete/{request_id}")
async def complete_request(request_id: int):
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        result = await session.execute(
            select(ProvisionRequest).where(ProvisionRequest.id == request_id)
        )
        req_obj = result.scalar_one_or_none()
        if not req_obj:
            return JSONResponse(status_code=404, content={"reason": "Request not found"})
        
        req_obj.status = "completed"
        await session.commit()
        
        # Notify requester
        requester_subject = f"Your environment request #{request_id} is completed!"
        requester_body = f"""Hi {req_obj.requester},

Great news! The infrastructure request #{request_id} you raised has been successfully approved, merged, and deployed.

- Environment: {req_obj.env_type} ({req_obj.env_name})
- PR Link: {req_obj.pr_link}
- Issue Link: {req_obj.issue_link}

Your environment is now ready for use.

Best regards,
Provisioner Bot Team
"""
        send_email(req_obj.requester_email, requester_subject, requester_body)
        
    return {"status": "completed"}
