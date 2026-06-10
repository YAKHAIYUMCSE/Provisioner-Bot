from policy_engine import validate_request

env = input("Enter environment: ")
infra_type = input("Enter infrastructure type: ")

result, message = validate_request(env, infra_type)

print(result)
print(message)