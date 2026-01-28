"""
API client for communicating with the changelog backend.
"""
import requests
from typing import Dict, Optional
import os


DEFAULT_API_URL = "http://localhost:8000"


def get_api_url() -> str:
    """Get the API URL from environment or default."""
    return os.getenv("CHANGELOG_API_URL", DEFAULT_API_URL)


def publish_changelog(
    changelog_data: Dict,
    version: str,
    commit_range: Optional[str] = None,
    project_name: str = "default",
    api_url: Optional[str] = None,
) -> Dict:
    """
    Publish a changelog to the backend API.
    
    Args:
        changelog_data: The generated changelog dictionary
        version: Version string for this changelog
        commit_range: Git commit range (e.g., "abc123..def456")
        project_name: Name of the project
        api_url: Override API URL
    
    Returns:
        Response from the API
    """
    url = api_url or get_api_url()
    
    payload = {
        "version": version,
        "title": changelog_data.get("title", "Changelog Update"),
        "summary": changelog_data.get("summary"),
        "changes": changelog_data.get("changes", {
            "features": [],
            "bugfixes": [],
            "improvements": [],
            "breaking": []
        }),
        "commit_range": commit_range,
        "project_name": project_name,
    }
    
    try:
        response = requests.post(
            f"{url}/api/changelogs",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        raise ConnectionError(
            f"Could not connect to the changelog API at {url}. "
            "Make sure the backend is running."
        )
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"API error: {e.response.text}")


def get_changelogs(
    project_name: Optional[str] = None,
    limit: int = 10,
    api_url: Optional[str] = None,
) -> list:
    """
    Fetch changelogs from the backend API.
    """
    url = api_url or get_api_url()
    params = {"limit": limit}
    if project_name:
        params["project"] = project_name
    
    try:
        response = requests.get(
            f"{url}/api/changelogs",
            params=params,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        raise ConnectionError(
            f"Could not connect to the changelog API at {url}. "
            "Make sure the backend is running."
        )
