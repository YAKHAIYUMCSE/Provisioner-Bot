import yaml

with open("policy.yaml", "r") as file:
    policy = yaml.safe_load(file)

def validate_request(env, infra_type):
    if env not in policy["allowed_envs"]:
        return False, "Environment not allowed"

    if infra_type not in policy["allowed_types"]:
        return False, "Infrastructure type not allowed"

    return True, "Request approved"