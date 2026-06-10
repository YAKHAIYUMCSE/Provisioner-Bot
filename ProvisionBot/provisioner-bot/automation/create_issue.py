import os
from github import Github

def create_github_issue(env_type, env_name, requester, summary):
    token = os.getenv("GITHUB_TOKEN")
    repo_name = os.getenv("GITHUB_REPOSITORY") or os.getenv("GITHUB_REPO")
    if not token or not repo_name:
        print("[MOCK] GitHub issue created")
        return "https://github.com/mock/repo/issues/1"
    try:
        g = Github(token)
        repo = g.get_repo(repo_name)
        issue = repo.create_issue(
            title=f"Provision {env_type} {env_name} - {requester}",
            body=f"**Type:** {env_type}\n**Env:** {env_name}\n**Requester:** {requester}\n**Summary:** {summary}",
            labels=["auto-provision"]
        )
        return issue.html_url
    except Exception as e:
        print(f"[GitHub Error] {e}")
        return "https://github.com/mock/repo/issues/1"
