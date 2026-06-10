import yaml
import os

def load_policy():
    base = os.path.dirname(__file__)
    with open(os.path.join(base, "policy.yaml")) as f:
        return yaml.safe_load(f)

def validate_policy(env_type: str, env_name: str, services: list = None) -> dict:
    policy = load_policy()
    if env_name.lower() not in policy["allowed_envs"]:
        return {"status": "rejected", "reason": f"Environment '{env_name}' is not allowed."}
    if env_type.lower() not in policy["allowed_types"]:
        return {"status": "rejected", "reason": f"Type '{env_type}' is not allowed."}
    if services and len(services) > policy["max_services"]:
        return {"status": "rejected", "reason": f"Too many services. Max allowed is {policy['max_services']}."}
    return {"status": "approved"}
