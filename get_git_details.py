#!/usr/bin/env python3
import subprocess

def get_git_remote_url():
    try:
        result = subprocess.run(["git", "remote", "-v"], capture_output=True, text=True, check=True)
        remote_url = result.stdout.split()[1]  # The first URL in the output
        return remote_url
    except subprocess.CalledProcessError as e:
        print("Error: Not a git repository or no remote configured.")
        return None

def extract_repo_name(url):
    if url:
        if url.startswith("git@"):
            repo_name = url.split(":")[1].split(".git")[0]
            protocol = "SSH"
        elif url.startswith("https://"):
            repo_name = url.split("/")[4].split(".git")[0]
            protocol = "HTTPS"
        else:
            print("Unknown URL format")
            return None, None, None
        return repo_name, protocol, url
    return None, None, None

def get_git_branch():
    try:
        result = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True, check=True)
        branch = result.stdout.strip()
        return branch
    except subprocess.CalledProcessError as e:
        print("Error: Not a git repository or no branch configured.")
        return None

remote_url = get_git_remote_url()
if remote_url:
    repo_name, protocol, full_url = extract_repo_name(remote_url)
    branch = get_git_branch()
    if repo_name and protocol and full_url and branch:
        print(f"Repository Name: {repo_name}")
        print(f"Protocol: {protocol}")
        print(f"Full URL: {full_url}")
        print(f"Current Branch: {branch}")
