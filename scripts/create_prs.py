#!/usr/bin/env python3
"""
Script to programmatically create Pull Requests for all open branches against main.

Usage:
    python scripts/create_prs.py --token <github_token> [--dry-run]

Environment:
    GITHUB_TOKEN: GitHub personal access token (alternative to --token)
"""

import os
import sys
import argparse
import json
from typing import List, Dict, Optional
import subprocess


class GitHubAPI:
    """Simple GitHub REST API client for PR operations."""

    def __init__(self, token: str, owner: str, repo: str):
        self.token = token
        self.owner = owner
        self.repo = repo
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "create-prs-script/1.0",
        }

    def _run_curl(
        self, method: str, endpoint: str, data: Optional[Dict] = None
    ) -> Dict:
        """Execute curl command for GitHub API calls."""
        url = f"{self.base_url}{endpoint}"
        cmd = ["curl", "-s", "-X", method, "-H", f"Authorization: token {self.token}"]

        for key, value in self.headers.items():
            if key != "Authorization":
                cmd.extend(["-H", f"{key}: {value}"])

        if data:
            cmd.extend(["-d", json.dumps(data)])

        cmd.append(url)

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return json.loads(result.stdout) if result.stdout else {}
        except subprocess.CalledProcessError as e:
            print(f"❌ API Error: {e.stderr}")
            return {"error": str(e)}
        except json.JSONDecodeError:
            return {"error": "Invalid JSON response"}

    def get_branches(self) -> List[str]:
        """Fetch all branches except main."""
        endpoint = f"/repos/{self.owner}/{self.repo}/branches?per_page=100"
        response = self._run_curl("GET", endpoint)

        if isinstance(response, list):
            branches = [b["name"] for b in response if b["name"] != "main"]
            return branches
        return []

    def get_existing_prs(self, head_branch: str) -> bool:
        """Check if a PR already exists for this branch."""
        endpoint = f"/repos/{self.owner}/{self.repo}/pulls?state=all&head={self.owner}:{head_branch}"
        response = self._run_curl("GET", endpoint)

        return isinstance(response, list) and len(response) > 0

    def create_pr(self, head_branch: str, title: str, description: str) -> Dict:
        """Create a new PR."""
        endpoint = f"/repos/{self.owner}/{self.repo}/pulls"
        data = {
            "title": title,
            "body": description,
            "head": head_branch,
            "base": "main",
        }
        return self._run_curl("POST", endpoint, data)


def generate_pr_title(branch_name: str) -> str:
    """Generate PR title from branch name."""
    # Remove timestamp suffix and format nicely
    clean_name = (
        branch_name.rsplit("-", 1)[0] if branch_name[-10:].isdigit() else branch_name
    )
    # Replace slashes and hyphens with spaces, title case
    title = clean_name.replace("/", ": ").replace("-", " ").title()
    return f"[Auto] {title}"


def generate_pr_description(branch_name: str) -> str:
    """Generate PR description template."""
    return f"""## Automated PR from branch: `{branch_name}`

### Description
Please review the changes in this branch.

### Checklist
- [ ] Code reviewed
- [ ] Tests pass
- [ ] No breaking changes
- [ ] Documentation updated (if needed)

---
*This PR was automatically created by create_prs.py*
"""


def main():
    parser = argparse.ArgumentParser(
        description="Create PRs for all open branches against main"
    )
    parser.add_argument(
        "--token", help="GitHub personal access token (or use GITHUB_TOKEN env var)"
    )
    parser.add_argument(
        "--owner",
        default="simpleprogrammer2",
        help="Repository owner (default: simpleprogrammer2)",
    )
    parser.add_argument(
        "--repo", default="easy-jarvis", help="Repository name (default: easy-jarvis)"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview PRs without creating them"
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        default=True,
        help="Skip branches that already have open PRs (default: True)",
    )

    args = parser.parse_args()

    # Get token from args or environment
    token = args.token or os.getenv("GITHUB_TOKEN")
    if not token:
        print(
            "❌ Error: GitHub token required. Use --token or set GITHUB_TOKEN env var"
        )
        sys.exit(1)

    # Initialize API client
    api = GitHubAPI(token, args.owner, args.repo)

    print(f"🔍 Fetching branches from {args.owner}/{args.repo}...")
    branches = api.get_branches()

    if not branches:
        print("⚠️  No open branches found (excluding main)")
        return

    print(f"✅ Found {len(branches)} open branches\n")

    # Summary stats
    created = 0
    skipped = 0
    errors = 0
    pr_summary = []

    for i, branch in enumerate(branches, 1):
        print(f"[{i}/{len(branches)}] Processing: {branch}")

        # Check for existing PRs
        if args.skip_existing and api.get_existing_prs(branch):
            print("  ⏭️  Skipping (PR already exists)")
            skipped += 1
            continue

        # Generate PR details
        title = generate_pr_title(branch)
        description = generate_pr_description(branch)

        if args.dry_run:
            print(f"  📋 Title: {title}")
            print(f"  📝 Description: {description[:100]}...")
            pr_summary.append(
                {"branch": branch, "title": title, "status": "PREVIEW (dry-run)"}
            )
        else:
            response = api.create_pr(branch, title, description)

            if "id" in response:
                pr_number = response.get("number", "?")
                pr_url = response.get("html_url", "#")
                print(f"  ✅ Created PR #{pr_number}: {pr_url}")
                created += 1
                pr_summary.append(
                    {
                        "branch": branch,
                        "title": title,
                        "status": f"✅ Created (#{pr_number})",
                    }
                )
            elif "error" in response:
                print(f"  ❌ Error: {response['error']}")
                errors += 1
                pr_summary.append(
                    {"branch": branch, "title": title, "status": "❌ Error"}
                )
            else:
                message = response.get("message", "Unknown error")
                print(f"  ❌ Error: {message}")
                errors += 1
                pr_summary.append(
                    {"branch": branch, "title": title, "status": "❌ Error"}
                )

    # Print summary
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    print(f"Total branches: {len(branches)}")
    if not args.dry_run:
        print(f"✅ Created: {created}")
    print(f"⏭️  Skipped: {skipped}")
    print(f"❌ Errors: {errors}")
    print("=" * 70)

    # Print PR details table
    if pr_summary and (args.dry_run or created > 0 or errors > 0):
        print("\n📋 PR Details:")
        print("-" * 70)
        for item in pr_summary:
            print(f"  {item['branch']}")
            print(f"    Status: {item['status']}")
        print("-" * 70)

    sys.exit(0 if errors == 0 else 1)


if __name__ == "__main__":
    main()
