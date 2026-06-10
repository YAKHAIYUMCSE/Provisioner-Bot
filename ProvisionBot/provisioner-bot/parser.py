import os
import re
import requests

def parse_request(text: str) -> dict:
    api_key = os.getenv("HF_API_KEY")
    if api_key:
        try:
            headers = {"Authorization": f"Bearer {api_key}"}
            payload = {
                "inputs": f"Extract type (docker/aws/terraform), environment (dev/qa/staging/prod), and services from: {text}. Reply in JSON only.",
                "parameters": {"max_new_tokens": 200}
            }
            model = os.getenv("HF_MODEL", "mistralai/Mistral-7B-Instruct-v0.3")
            res = requests.post(
                f"https://api-inference.huggingface.co/models/{model}",
                headers=headers, json=payload, timeout=10
            )
            result = res.json()
            if isinstance(result, list) and result:
                import json
                raw = result[0].get("generated_text", "")
                match = re.search(r'\{.*\}', raw, re.DOTALL)
                if match:
                    return json.loads(match.group())
        except Exception:
            pass
    return keyword_fallback(text)

def keyword_fallback(text: str) -> dict:
    text_lower = text.lower()
    env_type = "docker"
    if "aws" in text_lower:
        env_type = "aws"
    elif "terraform" in text_lower:
        env_type = "terraform"

    env_name = "dev"
    for e in ["qa", "staging", "prod", "production"]:
        if e in text_lower:
            env_name = "prod" if e == "production" else e
            break

    services = []
    for svc in ["postgres", "redis", "nginx", "mongodb", "mysql", "rabbitmq", "elasticsearch"]:
        if svc in text_lower:
            services.append(svc)

    return {"type": env_type, "environment": env_name, "services": services}
