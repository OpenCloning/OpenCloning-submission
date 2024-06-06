from jinja2 import Environment, PackageLoader
from github import Github, Auth
from github.InputGitTreeElement import InputGitTreeElement
from models import Submission
import os
import base64

# TODO: add tag
# TODO: add action that does the post-processing directly in github


def submit_to_github(submission: Submission, submission_folder: str):
    auth = Auth.Token(os.environ.get("GITHUB_TOKEN"))
    g = Github(auth=auth)

    repo = g.get_repo("genestorian/ShareYourCloning-submission")

    kit_url = submission.kit.addgene_url
    kit_name = kit_url.replace("https://www.addgene.org/", "")
    # Remove trailing slash if it exists
    if kit_name.endswith("/"):
        kit_name = kit_name[:-1]
    base_branch_name = f"{kit_name.replace('/', '-')}"
    new_branch_name = base_branch_name

    branches = repo.get_branches()
    existing_branches = [b.name for b in branches]
    i = 1
    while new_branch_name in existing_branches:
        new_branch_name = f"{base_branch_name}-{i}"
        i += 1

    elements = []
    for entry in os.scandir(submission_folder):
        if entry.is_file():
            with open(entry.path, "rb") as f:
                content = f.read()
                is_binary = not content.isascii()  # Determine if the content is binary
                if is_binary:
                    content_base64 = base64.b64encode(content).decode("utf-8")
                    blob = repo.create_git_blob(content_base64, "base64")
                else:
                    blob = repo.create_git_blob(content.decode("utf-8"), "utf-8")
                if entry.name.endswith(".xlsx"):
                    output_file_name = "submission.xlsx"
                else:
                    output_file_name = entry.name
                elements.append(
                    InputGitTreeElement(
                        path=f"submissions/{base_branch_name}/{output_file_name}",
                        mode="100644",
                        type="blob",
                        sha=blob.sha,
                    )
                )

    sb = repo.get_branch(repo.default_branch)
    ref = repo.create_git_ref(ref=f"refs/heads/{new_branch_name}", sha=sb.commit.sha)
    base_tree = repo.get_git_tree(sha=sb.commit.sha)
    tree = repo.create_git_tree(elements, base_tree)
    parent_commit = repo.get_git_commit(sb.commit.sha)

    commit_message = f"submission of kit {kit_name}"
    commit = repo.create_git_commit(commit_message, tree, [parent_commit])
    ref.edit(commit.sha)

    submission_dict = submission.model_dump()
    submission_dict["kit"]["name"] = kit_name
    jinja_env = Environment(loader=PackageLoader(__name__, "templates"))
    template = jinja_env.get_template("submission_pr_template.md.jinja")
    body = template.render(**submission_dict)

    pr = repo.create_pull(
        base=repo.default_branch,
        head=new_branch_name,
        title=f"Submission of kit {kit_name}",
        body=body,
    )

    # Assign the PR to manulera and other users
    github_users = set(
        s.github_username for s in submission.submitters if s.github_username
    )
    github_users.add("manulera")
    pr.add_to_assignees(*github_users)

    return pr.html_url
