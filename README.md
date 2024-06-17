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

1. Go to [GitHub Personal Access Tokens](https://github.com/settings/tokens).
2. Click on **Generate new token**.
3. Give your token a descriptive name.
4. Select the scopes or permissions you'd like to grant this token. For backing up repositories, you typically need the following scopes:
   - `repo` (Full control of private repositories)
5. Click **Generate token**.
6. Copy the token and save it to `github_token.txt`.

## Usage

Run the script with your GitHub username and the path to your backup directory as arguments.

### Basic Usage

```sh
python main.py <your_github_username> <path_to_backup_directory>
```

### Example

```sh
python main.py johndoe /mnt/nas/github_backups
```

### Script Explanation

The script performs the following steps:

1. Reads the GitHub Token: Reads the GitHub token from the specified file.
2. Fetches Repositories: Uses the GitHub API to fetch all repositories for the specified user.
3. Unzips Repositories: If a repository zip file exists, it unzips the repository before updating.
4. Clones or Updates Repositories: Checks if each repository exists in the backup directory. If it does, the script performs a git pull to update it. If it does not, the script performs a git clone to clone the repository.
5. Zips Repositories: After updating or cloning, the script zips the repository directory.

### Notes

1. Ensure the backup directory exists and is writable.
2. The token file should have read permissions for the user running the script.
3. Ensure git is installed and accessible from the command line.

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.
