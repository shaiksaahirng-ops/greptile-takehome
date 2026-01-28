"""
Git repository parser for extracting commit information.
"""
from git import Repo, InvalidGitRepositoryError
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os


def find_git_repo(path: str = ".") -> Optional[Repo]:
    """Find a git repository starting from the given path."""
    try:
        return Repo(path, search_parent_directories=True)
    except InvalidGitRepositoryError:
        return None


def get_commits(
    repo: Repo,
    days: int = 7,
    since: Optional[str] = None,
    until: Optional[str] = None,
    branch: Optional[str] = None,
) -> List[Dict]:
    """
    Extract commits from the repository within the specified time range.
    
    Args:
        repo: GitPython Repo object
        days: Number of days to look back (default 7)
        since: Start date in YYYY-MM-DD format (overrides days)
        until: End date in YYYY-MM-DD format (default: now)
        branch: Branch to analyze (default: current branch)
    
    Returns:
        List of commit dictionaries with message, author, date, files changed
    """
    # Calculate date range
    if since:
        since_date = datetime.strptime(since, "%Y-%m-%d")
    else:
        since_date = datetime.now() - timedelta(days=days)
    
    if until:
        until_date = datetime.strptime(until, "%Y-%m-%d")
    else:
        until_date = datetime.now()
    
    # Get the branch reference
    if branch:
        try:
            ref = repo.refs[branch]
        except IndexError:
            ref = repo.active_branch
    else:
        ref = repo.active_branch
    
    commits = []
    first_sha = None
    last_sha = None
    
    for commit in repo.iter_commits(ref):
        commit_date = datetime.fromtimestamp(commit.committed_date)
        
        # Skip commits outside the date range
        if commit_date < since_date:
            break
        if commit_date > until_date:
            continue
        
        # Track commit range
        if first_sha is None:
            first_sha = commit.hexsha[:7]
        last_sha = commit.hexsha[:7]
        
        # Get files changed
        files_changed = []
        if commit.parents:
            diff = commit.parents[0].diff(commit)
            files_changed = [d.a_path or d.b_path for d in diff]
        
        commits.append({
            "sha": commit.hexsha[:7],
            "message": commit.message.strip(),
            "author": commit.author.name,
            "email": commit.author.email,
            "date": commit_date.isoformat(),
            "files_changed": files_changed,
        })
    
    # Add commit range info
    commit_range = None
    if first_sha and last_sha:
        commit_range = f"{last_sha}..{first_sha}"
    
    return commits, commit_range


def format_commits_for_ai(commits: List[Dict]) -> str:
    """
    Format commits into a string suitable for AI analysis.
    """
    if not commits:
        return "No commits found in the specified range."
    
    formatted = []
    for commit in commits:
        files = ", ".join(commit["files_changed"][:5])
        if len(commit["files_changed"]) > 5:
            files += f" (+{len(commit['files_changed']) - 5} more)"
        
        formatted.append(
            f"- [{commit['sha']}] {commit['message']}\n"
            f"  Author: {commit['author']}\n"
            f"  Files: {files or 'N/A'}"
        )
    
    return "\n\n".join(formatted)
