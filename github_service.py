import json
import base64
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional


class GitHubService:
    def __init__(self, token: str, repo_owner: str, repo_name: str):
        self.token = token
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.base_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github+json"
        }

    # ---------------------------
    def _make_request(self, method: str, url: str, data: Optional[dict] = None):
        if method == "GET":
            r = requests.get(url, headers=self.headers)
        elif method == "PUT":
            r = requests.put(url, headers=self.headers, json=data)
        else:
            raise ValueError("Invalid HTTP method")

        if r.status_code == 404:
            return None

        if not r.ok:
            raise Exception(f"GitHub Error {r.status_code}: {r.text}")

        return r

    # ---------------------------
    # WAITLIST
    # ---------------------------
    def load_waitlist(self) -> List[dict]:
        """
        Load waitlist/waitlist.json from GitHub.
        Returns [] if file does not exist.
        """
        url = f"{self.base_url}/waitlist/waitlist.json"
        response = self._make_request("GET", url)

        if response is None:
            return []

        content = response.json()["content"]
        decoded = base64.b64decode(content).decode()
        return json.loads(decoded)

    # ---------------------------
    def save_waitlist(self, entries: List[dict]):
        """
        Save full waitlist to GitHub.
        Automatically handles sha (required for update).
        """
        url = f"{self.base_url}/waitlist/waitlist.json"

        existing = self._make_request("GET", url)
        sha = existing.json().get("sha") if existing else None

        encoded = base64.b64encode(json.dumps(entries, indent=2).encode()).decode()

        data = {
            "message": "Update waitlist.json",
            "content": encoded
        }

        if sha:
            data["sha"] = sha

        self._make_request("PUT", url, data)

    # ---------------------------
    def add_waitlist_entry(self, entry: dict):
        """
        Append a new entry into waitlist.json
        """
        entries = self.load_waitlist()
        entry["submitted_at"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        entries.append(entry)
        self.save_waitlist(entries)
