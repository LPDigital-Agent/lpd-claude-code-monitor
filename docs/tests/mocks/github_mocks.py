"""Mock GitHub API objects for testing."""

from typing import List, Dict, Any, Optional
from unittest.mock import Mock
from datetime import datetime


class MockPullRequest:
    """Mock GitHub Pull Request object."""
    
    def __init__(self, number: int, title: str, state: str = "open", 
                 created_at: str = "2024-01-01T10:00:00Z"):
        self.number = number
        self.title = title
        self.state = state
        self.created_at = created_at
        self.html_url = f"https://github.com/test/test-repo/pull/{number}"
        self.body = f"This is a test PR #{number}"
        self.user = Mock()
        self.user.login = "test-user"
        self.head = Mock()
        self.head.ref = "feature-branch"
        self.base = Mock()
        self.base.ref = "main"
        self.mergeable = True
        self.merged = False
        self.draft = False
    
    def get_reviews(self):
        """Mock get_reviews method."""
        review = Mock()
        review.state = "PENDING"
        review.user.login = "reviewer"
        return [review]
    
    def get_files(self):
        """Mock get_files method."""
        file_mock = Mock()
        file_mock.filename = "src/example.py"
        file_mock.status = "modified"
        file_mock.additions = 10
        file_mock.deletions = 5
        return [file_mock]


class MockRepository:
    """Mock GitHub Repository object."""
    
    def __init__(self, name: str = "test-repo", owner: str = "test-user"):
        self.name = name
        self.full_name = f"{owner}/{name}"
        self.owner = Mock()
        self.owner.login = owner
        self.html_url = f"https://github.com/{owner}/{name}"
        self.default_branch = "main"
        self._prs = []
        self._issues = []
    
    def get_pulls(self, state: str = "open", sort: str = "created", 
                  direction: str = "desc") -> List[MockPullRequest]:
        """Mock get_pulls method."""
        filtered_prs = [pr for pr in self._prs if pr.state == state]
        return filtered_prs
    
    def create_pull(self, title: str, body: str, head: str, base: str) -> MockPullRequest:
        """Mock create_pull method."""
        pr_number = len(self._prs) + 1
        pr = MockPullRequest(pr_number, title)
        pr.body = body
        pr.head.ref = head
        pr.base.ref = base
        self._prs.append(pr)
        return pr
    
    def get_pull(self, number: int) -> MockPullRequest:
        """Mock get_pull method."""
        for pr in self._prs:
            if pr.number == number:
                return pr
        raise Exception(f"Pull request #{number} not found")
    
    def get_issues(self, state: str = "open") -> List[Mock]:
        """Mock get_issues method."""
        return [issue for issue in self._issues if issue.state == state]
    
    def create_issue(self, title: str, body: str = "") -> Mock:
        """Mock create_issue method."""
        issue = Mock()
        issue.number = len(self._issues) + 1
        issue.title = title
        issue.body = body
        issue.state = "open"
        issue.html_url = f"https://github.com/{self.full_name}/issues/{issue.number}"
        self._issues.append(issue)
        return issue


class MockGitHub:
    """Mock GitHub API client."""
    
    def __init__(self, auth_token: str = "test_token"):
        self.auth_token = auth_token
        self._repos = {}
        self._user = Mock()
        self._user.login = "test-user"
        self._user.email = "test@example.com"
    
    def get_user(self) -> Mock:
        """Mock get_user method."""
        return self._user
    
    def get_repo(self, full_name: str) -> MockRepository:
        """Mock get_repo method."""
        if full_name not in self._repos:
            owner, name = full_name.split('/')
            self._repos[full_name] = MockRepository(name, owner)
        return self._repos[full_name]
    
    def search_repositories(self, query: str) -> Mock:
        """Mock search_repositories method."""
        result = Mock()
        result.totalCount = 1
        repo = MockRepository()
        result.get_page.return_value = [repo]
        return result
    
    def get_rate_limit(self) -> Mock:
        """Mock get_rate_limit method."""
        rate_limit = Mock()
        rate_limit.core.remaining = 4999
        rate_limit.core.limit = 5000
        rate_limit.core.reset = datetime.now()
        return rate_limit


class MockGitHubWorkflow:
    """Mock GitHub Actions workflow for testing."""
    
    def __init__(self, workflow_id: int = 1, name: str = "CI"):
        self.id = workflow_id
        self.name = name
        self.path = ".github/workflows/ci.yml"
        self.state = "active"
        self.html_url = f"https://github.com/test/test-repo/actions/workflows/{workflow_id}"
    
    def get_runs(self, status: str = None) -> List[Mock]:
        """Mock get_runs method."""
        run = Mock()
        run.id = 123456
        run.status = status or "completed"
        run.conclusion = "success"
        run.html_url = f"{self.html_url}/runs/123456"
        run.created_at = "2024-01-01T10:00:00Z"
        return [run]