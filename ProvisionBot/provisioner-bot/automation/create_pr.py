import os
from github import Github

def create_github_pr(request_id, env_type, env_name, generated_path):
    token = os.getenv("GITHUB_TOKEN")
    repo_name = os.getenv("GITHUB_REPOSITORY") or os.getenv("GITHUB_REPO")
    if not token or not repo_name:
        print("[MOCK] GitHub PR created")
        return f"https://github.com/mock/repo/pull/{request_id}"
    try:
        g = Github(token)
        repo = g.get_repo(repo_name)
        branch = f"provision/{request_id}"
        sb = repo.get_branch("main")
        repo.create_git_ref(f"refs/heads/{branch}", sb.commit.sha)

        for fname in os.listdir(generated_path):
            fpath = os.path.join(generated_path, fname)
            with open(fpath) as f:
                content = f.read()
            repo.create_file(
                f"generated/{request_id}/{fname}",
                f"Add {fname} for request {request_id}",
                content,
                branch=branch
            )

        pr = repo.create_pull(
            title=f"Provision {env_type} {env_name} Environment",
            body=f"Auto-generated infrastructure for request #{request_id}",
            head=branch,
            base="main"
        )
        return pr.html_url
    except Exception as e:
        print(f"[GitHub Error] {e}")
        return f"https://github.com/mock/repo/pull/{request_id}"
