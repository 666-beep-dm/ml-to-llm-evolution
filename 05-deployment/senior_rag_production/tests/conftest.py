"""Shared pytest configuration."""
import pytest

# Allow asyncio tests without marking every single one
pytest_plugins = ["pytest_asyncio"]
