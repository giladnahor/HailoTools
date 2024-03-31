#!/usr/bin/env python3
import os
import subprocess
import urllib.parse

def download_github_directory(github_url):
    # Parse the URL to separate the different components
    parsed_url = urllib.parse.urlparse(github_url)
    path_parts = parsed_url.path.strip('/').split('/')
    
    # Validate URL
    if len(path_parts) < 5 or parsed_url.netloc != 'github.com':
        print("Invalid GitHub URL")
        return
    
    owner, repo, _, branch, *directory = path_parts
    
    # Create the URL for the ZIP file
    zip_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip"
    
    # Create a temporary directory to store the ZIP file
    temp_dir = 'temp_folder'
    os.makedirs(temp_dir, exist_ok=True)
    
    # Download the ZIP file
    subprocess.run(['wget', zip_url, '-O', f"{temp_dir}/{branch}.zip"])
    
    # Unzip only the relevant directory to a temporary target folder
    unzip_target = os.path.join(temp_dir, 'target_folder')
    directory_path = f"{repo}-{branch}/{'/'.join(directory)}/*"
    subprocess.run(['unzip', f"{temp_dir}/{branch}.zip", directory_path, '-d', unzip_target])
    
    # Move the unzipped directory to the current path
    os.rename(os.path.join(unzip_target, repo+'-'+branch, *directory), os.path.join('.', directory[-1]))
    
    # Remove the temporary folder and ZIP file
    subprocess.run(['rm', '-r', temp_dir])

if __name__ == '__main__':
    github_url = input("Enter the GitHub URL of the directory you want to download: ")
    download_github_directory(github_url)
