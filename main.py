import argparse
import os
import shutil
import zipfile
from subprocess import CalledProcessError, check_call

import requests


# Function to read GitHub token from a file
def get_github_token(file_path):
    with open(file_path, "r") as file:
        return file.read().strip()


# Function to get repositories from GitHub
def get_repositories(username, token):
    url = f"https://api.github.com/user/repos"
    headers = {"Authorization": f"token {token}"}
    params = {
        "visibility": "all",  # Can be 'all', 'public', or 'private'
        "affiliation": "owner",  # Repositories that the authenticated user owns
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


# Function to clone or pull a repository
def clone_or_pull_repo(repo_url, repo_dir):
    if os.path.exists(repo_dir):
        # If the directory exists, pull the latest changes
        print(f"Updating repository: {repo_dir}")
        try:
            check_call(["git", "-C", repo_dir, "reset", "--hard"])
            check_call(["git", "-C", repo_dir, "pull"])
        except CalledProcessError as e:
            print(f"Error updating repository {repo_dir}: {e}")
    else:
        # If the directory doesn't exist, clone the repository
        print(f"Cloning repository: {repo_url}")
        try:
            check_call(["git", "clone", repo_url, repo_dir])
        except CalledProcessError as e:
            print(f"Error cloning repository {repo_url}: {e}")


# Function to zip a directory
def zip_directory(directory_path):
    zip_path = f"{directory_path}.zip"
    print(f"Zipping directory: {directory_path}")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, directory_path))
    print(f"Zipped directory to: {zip_path}")


# Function to unzip a directory
def unzip_directory(zip_path, extract_to):
    print(f"Unzipping file: {zip_path}")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)
    print(f"Unzipped to: {extract_to}")


# Main function
def main(username, backup_dir):
    token_file = "github_token.txt"
    # Ensure the backup directory exists
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    token = get_github_token(token_file)
    repos = get_repositories(username, token)
    for repo in repos:
        repo_name = repo["name"]
        repo_dir = os.path.join(backup_dir, repo_name)
        zip_path = f"{repo_dir}.zip"

        # Unzip if zip file exists
        if os.path.exists(zip_path):
            unzip_directory(zip_path, repo_dir)

        # Remove the zip file
        if os.path.exists(zip_path):
            os.remove(zip_path)

        # Clone or pull the repository
        clone_or_pull_repo(repo["clone_url"], repo_dir)

        # Zip the repository directory
        if os.path.exists(repo_dir):
            zip_directory(repo_dir)

        # Remove the repository directory
        if os.path.exists(repo_dir):
            shutil.rmtree(repo_dir)


if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Backup GitHub repositories.")
    parser.add_argument("username", help="GitHub username")
    parser.add_argument("backup_dir", help="Directory to backup repositories to")

    args = parser.parse_args()
    main(args.username, args.backup_dir)
