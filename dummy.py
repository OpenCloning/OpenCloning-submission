from github import Github, Auth
import os

auth = Auth.Token(os.environ["GITHUB_TOKEN"])
g = Github(auth=auth)

# Create an issue and assign it to manulera

issue_body = """
You can find the file here:

hello.txt
"""
repo = g.get_repo("genestorian/ShareYourCloning-submission")
# issue = repo.create_issue(
#     title="Test issue", body=issue_body, assignee="manulera", labels=["submission"]
# )

branches = repo.get_branches()

new_branch_name = "test-branch-0"
existing_branches = [b.name for b in branches]
i = 1
while new_branch_name in existing_branches:
    new_branch_name = f"test-branch-{i}"
    i += 1

sb = repo.get_branch(repo.default_branch)
repo.create_git_ref(ref=f"refs/heads/{new_branch_name}", sha=sb.commit.sha)

repo.create_file("test.txt", "commit message", "file content", branch=new_branch_name)

body = """
Submission of kit X'

Hello!
"""

pr = repo.create_pull(
    base=repo.default_branch,
    head=new_branch_name,
    title="Submission of kit X'",
    body=body,
)
