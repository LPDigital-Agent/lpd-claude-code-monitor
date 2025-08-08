"""Shared pytest fixtures for DLQ Monitor tests."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from typing import Dict, Any, Generator

import pytest
import boto3
from moto import mock_aws
import yaml


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def mock_config() -> Dict[str, Any]:
    """Provide a mock configuration for testing."""
    return {
        "aws": {"profile": "test-profile", "region": "us-east-1"},
        "dlq_patterns": ["*-dlq", "*-dead-letter*"],
        "notification": {"threshold": 1, "cooldown": 300},
        "investigation": {"enabled": True, "auto_trigger": True, "cooldown": 600},
        "demo_mode": {"enabled": False, "simulate_messages": False},
        "monitoring": {"interval": 30, "max_investigations": 3},
    }


@pytest.fixture
def config_file(temp_dir: Path, mock_config: Dict[str, Any]) -> Path:
    """Create a temporary configuration file."""
    config_path = temp_dir / "config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(mock_config, f)
    return config_path


@pytest.fixture
def mock_env_vars() -> Generator[None, None, None]:
    """Mock environment variables for testing."""
    env_vars = {
        "GITHUB_TOKEN": "test_token_123",
        "GITHUB_USERNAME": "test_user",
        "ELEVENLABS_API_KEY": "test_elevenlabs_key",
        "AWS_PROFILE": "test-profile",
        "AWS_DEFAULT_REGION": "us-east-1",
    }

    with patch.dict(os.environ, env_vars):
        yield


@pytest.fixture
def mock_aws_session():
    """Mock AWS session for testing."""
    with patch("boto3.Session") as mock_session:
        mock_session_instance = Mock()
        mock_session.return_value = mock_session_instance
        yield mock_session_instance


@pytest.fixture
def mock_sqs_client():
    """Mock SQS client for testing."""
    with mock_aws():
        client = boto3.client("sqs", region_name="us-east-1")
        yield client


@pytest.fixture
def mock_sqs_queues(mock_sqs_client):
    """Create mock SQS queues for testing."""
    queues = {}

    # Create test queues
    queue_names = ["test-queue-dlq", "processing-dead-letter-queue", "normal-queue", "another-dlq"]

    for queue_name in queue_names:
        response = mock_sqs_client.create_queue(QueueName=queue_name)
        queues[queue_name] = response["QueueUrl"]

    # Add messages to some DLQ queues
    mock_sqs_client.send_message(QueueUrl=queues["test-queue-dlq"], MessageBody="Test error message 1")
    mock_sqs_client.send_message(QueueUrl=queues["processing-dead-letter-queue"], MessageBody="Test error message 2")

    return queues


@pytest.fixture
def mock_claude_session_data() -> Dict[str, Any]:
    """Mock Claude session data for testing."""
    return {
        "session_123": {
            "queue_name": "test-queue-dlq",
            "started": "2024-01-01T10:00:00Z",
            "status": "active",
            "message_count": 5,
            "pid": 12345,
            "cooldown_until": None,
        },
        "session_456": {
            "queue_name": "processing-dead-letter-queue",
            "started": "2024-01-01T09:30:00Z",
            "status": "completed",
            "message_count": 2,
            "pid": None,
            "cooldown_until": "2024-01-01T11:00:00Z",
        },
    }


@pytest.fixture
def claude_sessions_file(temp_dir: Path, mock_claude_session_data: Dict[str, Any]) -> Path:
    """Create a temporary Claude sessions file."""
    sessions_path = temp_dir / ".claude_sessions.json"
    with open(sessions_path, "w") as f:
        json.dump(mock_claude_session_data, f, indent=2)
    return sessions_path


@pytest.fixture
def mock_github_client():
    """Mock GitHub client for testing."""
    with patch("github.Github") as mock_github:
        mock_client = Mock()
        mock_github.return_value = mock_client

        # Mock repository
        mock_repo = Mock()
        mock_client.get_repo.return_value = mock_repo

        # Mock pull requests
        mock_pr = Mock()
        mock_pr.number = 123
        mock_pr.title = "Fix DLQ Processing Issue"
        mock_pr.state = "open"
        mock_pr.created_at = "2024-01-01T10:00:00Z"
        mock_repo.get_pulls.return_value = [mock_pr]

        yield mock_client


@pytest.fixture
def mock_subprocess():
    """Mock subprocess calls for testing."""
    with patch("subprocess.Popen") as mock_popen:
        mock_process = Mock()
        mock_process.pid = 12345
        mock_process.poll.return_value = None  # Process still running
        mock_process.communicate.return_value = ("Success", "")
        mock_popen.return_value = mock_process
        yield mock_popen


@pytest.fixture
def mock_elevenlabs():
    """Mock ElevenLabs TTS client for testing."""
    with patch("elevenlabs.generate") as mock_generate:
        mock_generate.return_value = b"fake_audio_data"
        yield mock_generate


@pytest.fixture
def mock_macos_notification():
    """Mock macOS notification system for testing."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        yield mock_run


@pytest.fixture
def sample_dlq_messages() -> list:
    """Sample DLQ messages for testing."""
    return [
        {
            "MessageId": "msg-001",
            "Body": json.dumps(
                {"error": "Connection timeout", "service": "payment-processor", "timestamp": "2024-01-01T10:00:00Z"}
            ),
            "Attributes": {"ApproximateReceiveCount": "3", "SentTimestamp": "1704110400000"},
        },
        {
            "MessageId": "msg-002",
            "Body": json.dumps(
                {"error": "Database connection failed", "service": "user-service", "timestamp": "2024-01-01T10:05:00Z"}
            ),
            "Attributes": {"ApproximateReceiveCount": "2", "SentTimestamp": "1704110700000"},
        },
    ]


@pytest.fixture
def mock_curses():
    """Mock curses library for dashboard testing."""
    with (
        patch("curses.initscr") as mock_initscr,
        patch("curses.endwin") as mock_endwin,
        patch("curses.curs_set") as mock_curs_set,
        patch("curses.start_color") as mock_start_color,
        patch("curses.init_pair") as mock_init_pair,
        patch("curses.color_pair") as mock_color_pair,
    ):

        mock_screen = Mock()
        mock_initscr.return_value = mock_screen
        mock_screen.getmaxyx.return_value = (50, 100)
        mock_screen.getch.return_value = ord("q")  # Simulate quit key

        yield {
            "screen": mock_screen,
            "initscr": mock_initscr,
            "endwin": mock_endwin,
            "curs_set": mock_curs_set,
            "start_color": mock_start_color,
            "init_pair": mock_init_pair,
            "color_pair": mock_color_pair,
        }


@pytest.fixture
def mock_yaml_config_loader():
    """Mock YAML configuration loading."""

    def load_config(path: str) -> Dict[str, Any]:
        return {
            "aws": {"profile": "test", "region": "us-east-1"},
            "dlq_patterns": ["*-dlq"],
            "notification": {"threshold": 1},
            "investigation": {"enabled": True},
        }

    with patch("yaml.safe_load", side_effect=lambda f: load_config("")):
        yield load_config


# Test data fixtures stored in files
@pytest.fixture
def fixtures_dir() -> Path:
    """Get the fixtures directory path."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def mocks_dir() -> Path:
    """Get the mocks directory path."""
    return Path(__file__).parent / "mocks"


# Cleanup fixture
@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Automatically cleanup test files after each test."""
    yield
    # Cleanup any temporary files created during tests
    test_files = [".claude_sessions.json", "test_config.yaml", "test_log.log"]

    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
