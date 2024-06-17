# GitHub Repository Backup Script

This script allows you to back up all your GitHub repositories to a specified directory (e.g. a NAS). It clones repositories that do not exist in the backup directory and pulls updates for those that already exist.

## Prerequisites

- Python
- Git
- GitHub Personal Access Token

## Installation

1. Clone this repository or download the script.

2. Install the required Python library:

   ```sh
   pip install requests
   ```

3. Save your GitHub Personal Access Token in `github_token.txt`.

## Creating a GitHub Personal Access Token

1. Go to [New personal access token (classic)](https://github.com/settings/tokens/new).
2. Give your token a descriptive name.
3. Select the scopes or permissions you'd like to grant this token. For backing up repositories, you need the following scopes:
   - `repo` (Full control of private repositories)
   - `read:org` (Read org and team membership)
4. Click **Generate token**.
5. Copy the token and save it to `github_token.txt`.

## Usage

Run the script with your GitHub username and the path to your backup directory as arguments.

### Basic Usage

```sh
python main.py <your_github_username> <path_to_backup_directory>
```

### Usage with Organization Repositories

```sh
python main.py <your_github_username> <path_to_backup_directory> --include-orgs
```

### Example

```sh
python main.py johndoe /mnt/nas/github_backups --include-orgs
```

### Script Explanation

The script performs the following steps:

1. **Reads the GitHub Token**: Reads the GitHub token from the specified file.
2. **Fetches Personal Repositories**: Uses the GitHub API to fetch all personal repositories for the specified user, handling pagination to get all repositories.
3. **Fetches Organization Repositories**: If the --include-orgs flag is set, the script uses the GitHub API to fetch all repositories for each organization the user is part of, handling pagination to get all repositories.
4. **Unzips Repositories**: If a repository zip file exists, it unzips the repository before updating.
5. **Clones or Updates Repositories**: Checks if each repository exists in the backup directory. If it does, the script resets and pulls the latest changes from the remote repository. If it does not, the script performs a git clone to clone the repository.
6. **Zips Repositories**: After updating or cloning, the script zips the repository directory and deletes the original directory.

### Notes

1. Ensure the backup directory exists and is writable.
2. The token file should have read permissions for the user running the script. If you're running the script with --include-orgs, the token should have org:read permissions.
3. Ensure git is installed and accessible from the command line.

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.
