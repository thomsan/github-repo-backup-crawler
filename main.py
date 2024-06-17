import argparse
import logging
import os
import shutil
import zipfile
from subprocess import CalledProcessError, check_call

import requests

logging.basicConfig(
    filename="backup.log", filemode="w", format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)


def get_github_token(file_path):
    with open(file_path, "r") as file:
        return file.read().strip()


def get_user_repositories(username, token):
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/user/repos"
        headers = {"Authorization": f"token {token}"}
        params = {
            "visibility": "all",  # Can be 'all', 'public', or 'private'
            "affiliation": "owner",
            "per_page": 100,
            "page": page,
        }
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        page_repos = response.json()
        if not page_repos:
            break
        repos.extend(page_repos)
        page += 1
    return repos


def get_org_repositories(org_name, token):
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/orgs/{org_name}/repos"
        headers = {"Authorization": f"token {token}"}
        params = {"per_page": 100, "page": page}
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        page_repos = response.json()
        if not page_repos:
            break
        repos.extend(page_repos)
        page += 1
    return repos


def get_user_orgs(username, token):
    url = f"https://api.github.com/user/orgs"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    orgs = response.json()
    return [org["login"] for org in orgs]


def clone_or_pull_repo(repo_url, repo_dir):
    if os.path.exists(repo_dir):
        logging.info(f"Updating repository: {repo_dir}")
        try:
            check_call(["git", "-C", repo_dir, "reset", "--hard"])
            check_call(["git", "-C", repo_dir, "pull"])
        except CalledProcessError as e:
            logging.error(f"Error updating repository {repo_dir}: {e}")
            return False
    else:
        logging.info(f"Cloning repository: {repo_url}")
        try:
            check_call(["git", "clone", repo_url, repo_dir])
        except CalledProcessError as e:
            logging.error(f"Error cloning repository {repo_url}: {e}")
            return False
    return True


def zip_directory(directory_path):
    zip_path = f"{directory_path}.zip"
    logging.info(f"Zipping directory: {directory_path}")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, directory_path))
    logging.info(f"Zipped directory to: {zip_path}")


def unzip_directory(zip_path, extract_to):
    logging.info(f"Unzipping file: {zip_path}")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)
    logging.info(f"Unzipped to: {extract_to}")


def backup_repositories(repos, backup_dir, summary, entity_name):
    success_count = 0
    for repo in repos:
        repo_name = repo["name"]
        repo_dir = os.path.join(backup_dir, repo_name)
        zip_path = f"{repo_dir}.zip"

        if os.path.exists(zip_path):
            unzip_directory(zip_path, repo_dir)

        if os.path.exists(zip_path):
            os.remove(zip_path)

        if clone_or_pull_repo(repo["clone_url"], repo_dir):
            success_count += 1

        if os.path.exists(repo_dir):
            zip_directory(repo_dir)

        if os.path.exists(repo_dir):
            shutil.rmtree(repo_dir)

    summary[entity_name] = {"success": success_count, "failed": len(repos) - success_count}


def main(username, backup_dir, include_orgs):
    token_file = "github_token.txt"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    token = get_github_token(token_file)
    summary = {}

    user_backup_dir = os.path.join(backup_dir, username)
    os.makedirs(user_backup_dir, exist_ok=True)
    user_repos = get_user_repositories(username, token)
    logging.info(f"Found {len(user_repos)} personal repositories.")
    backup_repositories(user_repos, user_backup_dir, summary, username)

    if include_orgs:
        org_names = get_user_orgs(username, token)
        for org_name in org_names:
            org_backup_dir = os.path.join(backup_dir, org_name)
            os.makedirs(org_backup_dir, exist_ok=True)
            org_repos = get_org_repositories(org_name, token)
            logging.info(f"Found {len(org_repos)} organization repositories in {org_name}.")
            backup_repositories(org_repos, org_backup_dir, summary, org_name)

    print("\nBackup Summary:")
    for entity_name, counts in summary.items():
        print(f"Backed up {counts['success']} repos for {entity_name} with {counts['failed']} errors")
    print("Check backup.log for details.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backup GitHub repositories.")
    parser.add_argument("username", help="GitHub username")
    parser.add_argument("backup_dir", help="Directory to backup repositories to")
    parser.add_argument("--include-orgs", action="store_true", help="Include organization repositories")

    args = parser.parse_args()
    main(args.username, args.backup_dir, args.include_orgs)
