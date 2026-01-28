"""
AI-powered changelog generation using Gemini API.
"""
import json
import os
from typing import Dict, List, Optional

# Try new package first, fall back to deprecated one
try:
    from google import genai
    from google.genai import types
    USING_NEW_API = True
except ImportError:
    import google.generativeai as genai
    USING_NEW_API = False


def configure_gemini(api_key: Optional[str] = None):
    """Configure the Gemini API with the provided key."""
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        raise ValueError(
            "Gemini API key not found. Set GEMINI_API_KEY environment variable "
            "or pass it via --api-key option."
        )
    
    if USING_NEW_API:
        # New API uses client-based configuration
        return genai.Client(api_key=key)
    else:
        genai.configure(api_key=key)
        return None


def generate_changelog(
    commits_text: str,
    project_name: str = "this project",
    version: Optional[str] = None,
    client=None,
) -> Dict:
    """
    Generate a changelog from commit text using Gemini AI.
    
    Args:
        commits_text: Formatted string of commits
        project_name: Name of the project for context
        version: Optional version number for this release
        client: Gemini client (for new API)
    
    Returns:
        Dictionary with structured changelog data
    """
    prompt = f"""You are a technical writer creating a changelog for end-users of a developer tool.

Analyze the following git commits and create a user-friendly changelog. Focus on what matters to END USERS, not internal implementation details.

PROJECT: {project_name}
VERSION: {version or "Latest"}

COMMITS:
{commits_text}

Create a changelog with the following JSON structure:
{{
    "title": "A brief, catchy title summarizing this release (e.g., 'Performance Improvements & Bug Fixes')",
    "summary": "A 1-2 sentence high-level summary of what changed",
    "changes": {{
        "features": ["List of new features or capabilities (user-facing)"],
        "bugfixes": ["List of bug fixes (describe the fix, not the bug)"],
        "improvements": ["List of improvements or enhancements"],
        "breaking": ["List of breaking changes that users need to know about"]
    }}
}}

RULES:
1. Write for END USERS, not developers. Translate technical commits into user benefits.
2. Group related commits into single changelog items.
3. Skip internal refactoring, test updates, or documentation changes unless they affect users.
4. Be concise - each item should be one clear sentence.
5. If a category has no items, use an empty array.
6. Use action verbs: "Added", "Fixed", "Improved", "Removed", etc.

Return ONLY valid JSON, no markdown or explanation."""

    try:
        if USING_NEW_API and client:
            response = client.models.generate_content(
                model="gemini-flash-latest",
                contents=prompt,
            )
            text = response.text.strip()
        else:
            model = genai.GenerativeModel("gemini-flash-latest")
            response = model.generate_content(prompt)
            text = response.text.strip()
        
        # Remove markdown code blocks if present
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            text = text.rsplit("```", 1)[0]
        
        changelog_data = json.loads(text)
        return changelog_data
    except json.JSONDecodeError as e:
        # If parsing fails, return a structured error
        return {
            "title": "Changelog Generation Error",
            "summary": "Failed to parse AI response",
            "changes": {
                "features": [],
                "bugfixes": [],
                "improvements": [f"Raw response: {text[:500] if 'text' in dir() else 'No response'}"],
                "breaking": []
            },
            "error": str(e)
        }
    except Exception as e:
        return {
            "title": "Changelog Generation Error",
            "summary": f"AI generation failed: {str(e)}",
            "changes": {
                "features": [],
                "bugfixes": [],
                "improvements": [],
                "breaking": []
            },
            "error": str(e)
        }


def generate_version_suggestion(commits: List[Dict], current_version: Optional[str] = None) -> str:
    """
    Suggest a version number based on commit content.
    Uses simple semver heuristics.
    """
    has_breaking = False
    has_features = False
    
    for commit in commits:
        msg = commit["message"].lower()
        if "breaking" in msg or "!:" in msg:
            has_breaking = True
        if "feat" in msg or "feature" in msg or "add" in msg:
            has_features = True
    
    if current_version:
        parts = current_version.lstrip("v").split(".")
        if len(parts) == 3:
            major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
            if has_breaking:
                return f"v{major + 1}.0.0"
            elif has_features:
                return f"v{major}.{minor + 1}.0"
            else:
                return f"v{major}.{minor}.{patch + 1}"
    
    # Default to date-based version
    from datetime import datetime
    return datetime.now().strftime("v%Y.%m.%d")
