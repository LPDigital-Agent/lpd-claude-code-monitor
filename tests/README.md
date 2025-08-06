# Tests Directory

This directory contains all test suites for the LPD Claude Code Monitor project.

## Structure

### `/unit/`
Unit tests for individual components and functions.

### `/integration/`
Integration tests that verify the interaction between different components.
- `test_adk_system.py` - Full ADK multi-agent system integration test

### `/validation/`
Validation tests for configuration and environment setup.
- `test_adk_simple.py` - Simplified validation test for ADK components

## Running Tests

### Run all tests
```bash
make test
```

### Run specific test suites
```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# Validation tests
python tests/validation/test_adk_simple.py
```

### ADK System Validation
```bash
# From project root with environment loaded
source .env
export GITHUB_TOKEN=$(gh auth token 2>/dev/null)
python tests/validation/test_adk_simple.py
```

## Test Requirements

- Python 3.11+
- All dependencies from `requirements-test.txt`
- Environment variables set (GEMINI_API_KEY, GITHUB_TOKEN, etc.)
- AWS credentials configured for FABIO-PROD profile