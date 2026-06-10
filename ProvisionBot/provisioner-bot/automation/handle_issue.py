import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from parser import parse_request

def handle_issue(issue_body: str):
    print(f"[Handle Issue] Parsing: {issue_body}")
    result = parse_request(issue_body)
    print(f"[Handle Issue] Parsed: {result}")
    return result

if __name__ == "__main__":
    text = sys.argv[1] if len(sys.argv) > 1 else "Create Docker environment with postgres and redis"
    print(handle_issue(text))
