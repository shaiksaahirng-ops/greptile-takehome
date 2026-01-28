"""
Changelog CLI - AI-powered changelog generator for developers.

Usage:
    changelog generate [OPTIONS]   Generate a changelog from recent commits
    changelog publish              Publish the last generated changelog
    changelog list                 Show recent changelogs
"""
import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich import print as rprint
from dotenv import load_dotenv
import os
import json

from .git_parser import find_git_repo, get_commits, format_commits_for_ai
from .ai_generator import configure_gemini, generate_changelog, generate_version_suggestion
from .api_client import publish_changelog, get_changelogs

# Load environment variables from .env file
load_dotenv()

console = Console()

# Store the last generated changelog for the publish command
_last_changelog = None
_last_commit_range = None


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """🚀 AI-powered changelog generator using Gemini"""
    pass


@cli.command()
@click.option("--days", "-d", default=7, help="Number of days to look back for commits")
@click.option("--since", "-s", help="Start date (YYYY-MM-DD)")
@click.option("--until", "-u", help="End date (YYYY-MM-DD)")
@click.option("--branch", "-b", help="Branch to analyze (default: current)")
@click.option("--version", "-v", "version_str", help="Version for this changelog")
@click.option("--project", "-p", default="default", help="Project name")
@click.option("--api-key", envvar="GEMINI_API_KEY", help="Gemini API key")
@click.option("--publish", is_flag=True, help="Publish immediately after generating")
@click.option("--dry-run", is_flag=True, help="Show what would be generated without calling AI")
@click.option("--output", "-o", type=click.Path(), help="Save changelog to file (JSON)")
def generate(days, since, until, branch, version_str, project, api_key, publish, dry_run, output):
    """Generate a changelog from recent git commits using AI."""
    global _last_changelog, _last_commit_range
    
    # Find git repository
    with console.status("[bold blue]Finding git repository..."):
        repo = find_git_repo()
    
    if not repo:
        console.print("[red]❌ Not a git repository. Run this command from within a git project.[/red]")
        raise SystemExit(1)
    
    repo_name = os.path.basename(repo.working_dir)
    console.print(f"[green]✓[/green] Found repository: [bold]{repo_name}[/bold]")
    
    # Get commits
    with console.status("[bold blue]Fetching commits..."):
        commits, commit_range = get_commits(repo, days=days, since=since, until=until, branch=branch)
    
    if not commits:
        console.print("[yellow]⚠ No commits found in the specified range.[/yellow]")
        raise SystemExit(0)
    
    console.print(f"[green]✓[/green] Found [bold]{len(commits)}[/bold] commits")
    _last_commit_range = commit_range
    
    # Show commits in dry-run mode
    if dry_run:
        console.print("\n[bold]Commits that would be analyzed:[/bold]")
        for commit in commits[:10]:
            console.print(f"  • {commit['sha']} - {commit['message'][:60]}...")
        if len(commits) > 10:
            console.print(f"  ... and {len(commits) - 10} more")
        return
    
    # Generate version if not provided
    if not version_str:
        version_str = generate_version_suggestion(commits)
        console.print(f"[dim]Auto-generated version: {version_str}[/dim]")
    
    # Format commits and generate changelog
    commits_text = format_commits_for_ai(commits)
    
    with console.status("[bold blue]🤖 Generating changelog with AI..."):
        try:
            configure_gemini(api_key)
            changelog_data = generate_changelog(commits_text, project_name=repo_name, version=version_str)
        except ValueError as e:
            console.print(f"[red]❌ {e}[/red]")
            raise SystemExit(1)
    
    _last_changelog = changelog_data
    
    # Display the generated changelog
    display_changelog(changelog_data, version_str)
    
    # Save to file if requested
    if output:
        with open(output, "w") as f:
            json.dump({"version": version_str, **changelog_data}, f, indent=2)
        console.print(f"\n[green]✓[/green] Saved to [bold]{output}[/bold]")
    
    # Publish if requested
    if publish:
        do_publish(changelog_data, version_str, commit_range, project)


@cli.command()
@click.option("--version", "-v", "version_str", help="Override version")
@click.option("--project", "-p", default="default", help="Project name")
@click.option("--api-url", envvar="CHANGELOG_API_URL", help="Backend API URL")
def publish(version_str, project, api_url):
    """Publish the last generated changelog to the web."""
    global _last_changelog, _last_commit_range
    
    if not _last_changelog:
        console.print("[yellow]⚠ No changelog to publish. Run 'changelog generate' first.[/yellow]")
        raise SystemExit(1)
    
    version = version_str or generate_version_suggestion([])
    do_publish(_last_changelog, version, _last_commit_range, project, api_url)


def do_publish(changelog_data, version, commit_range, project, api_url=None):
    """Helper to publish a changelog."""
    with console.status("[bold blue]📤 Publishing changelog..."):
        try:
            result = publish_changelog(
                changelog_data,
                version=version,
                commit_range=commit_range,
                project_name=project,
                api_url=api_url,
            )
            console.print(f"\n[green]✓ Published![/green] Changelog ID: [bold]{result['id']}[/bold]")
            console.print(f"[dim]View at: http://localhost:5173[/dim]")
        except ConnectionError as e:
            console.print(f"\n[red]❌ {e}[/red]")
            raise SystemExit(1)
        except RuntimeError as e:
            console.print(f"\n[red]❌ {e}[/red]")
            raise SystemExit(1)


@cli.command("list")
@click.option("--project", "-p", help="Filter by project name")
@click.option("--limit", "-n", default=5, help="Number of changelogs to show")
@click.option("--api-url", envvar="CHANGELOG_API_URL", help="Backend API URL")
def list_changelogs(project, limit, api_url):
    """List recent changelogs from the server."""
    with console.status("[bold blue]Fetching changelogs..."):
        try:
            changelogs = get_changelogs(project_name=project, limit=limit, api_url=api_url)
        except ConnectionError as e:
            console.print(f"[red]❌ {e}[/red]")
            raise SystemExit(1)
    
    if not changelogs:
        console.print("[yellow]No changelogs found.[/yellow]")
        return
    
    table = Table(title="Recent Changelogs")
    table.add_column("ID", style="dim")
    table.add_column("Version", style="cyan")
    table.add_column("Title", style="bold")
    table.add_column("Date", style="green")
    
    for cl in changelogs:
        date = cl["created_at"][:10]
        table.add_row(str(cl["id"]), cl["version"], cl["title"][:40], date)
    
    console.print(table)


def display_changelog(data: dict, version: str):
    """Display a beautifully formatted changelog in the terminal."""
    console.print()
    
    # Title panel
    title = f"📋 {data.get('title', 'Changelog')}"
    console.print(Panel(title, style="bold cyan", expand=False))
    
    # Summary
    if data.get("summary"):
        console.print(f"\n[italic]{data['summary']}[/italic]\n")
    
    # Changes by category
    changes = data.get("changes", {})
    
    categories = [
        ("features", "✨ New Features", "green"),
        ("improvements", "📈 Improvements", "blue"),
        ("bugfixes", "🐛 Bug Fixes", "yellow"),
        ("breaking", "⚠️  Breaking Changes", "red"),
    ]
    
    for key, label, color in categories:
        items = changes.get(key, [])
        if items:
            console.print(f"\n[bold {color}]{label}[/bold {color}]")
            for item in items:
                console.print(f"  • {item}")
    
    console.print()


if __name__ == "__main__":
    cli()
