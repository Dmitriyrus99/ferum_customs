#!/usr/bin/env python3
"""
Asynchronous GPT-powered code review helper.
Version: 2.1 (fixes and improvements as of 2025-07-31)
"""

from __future__ import annotations

import argparse
import asyncio
import datetime as _dt
import difflib
import json
import os
import pathlib
import random
import re
import textwrap
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from hashlib import md5
from typing import Final, Optional

import pathspec
import tiktoken
from openai import (
    APIConnectionError,
    APIError,
    APITimeoutError,
    AsyncOpenAI,
    RateLimitError,
)
from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)

# ──────────────────────────────────────────────────────────────────────────────
# Constants and settings
# ──────────────────────────────────────────────────────────────────────────────
DEFAULT_REPO_PATH: Final[pathlib.Path] = pathlib.Path.cwd()
DEFAULT_SCAN_PATH: Final[pathlib.Path] = pathlib.Path.cwd()
DEFAULT_OUT_DIR: Final[pathlib.Path] = pathlib.Path("code_review")
DEFAULT_MODEL: Final[str] = "gpt-4o-mini"
DEFAULT_MAXTOK: Final[int] = 12_000
MAX_CONCURRENCY: Final[int] = min((os.cpu_count() or 2) * 2, 16)
OPENAI_RETRY_ATTEMPTS: Final[int] = 6
OPENAI_BASE_DELAY: Final[float] = 2.0
OPENAI_MAX_DELAY: Final[float] = 30.0

EXTS: Final[set[str]] = {
    ".py",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".html",
    ".css",
    ".scss",
    ".json",
    ".yaml",
    ".yml",
    ".sh",
    ".sql",
}
IGNORE_EXTS: Final[set[str]] = {
    ".zip",
    ".tar",
    ".gz",
    ".rar",
    ".7z",
    ".db",
    ".sqlite",
    ".pyc",
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".jpg",
    ".png",
    ".pem",
    ".log",
}
IGNORE_PATTERNS: Final[set[str]] = {
    "node_modules",
    "__pycache__",
    ".git",
    "env",
    "secrets",
    ".pre-commit-home",
    ".devcontainer",
    "sites",
    ".venv",
    ".venv_dev",
    "testvenv",
    ".mypy_cache",
    "site-packages",
}
CACHE_FILE_NAME: Final[str] = ".review_cache.json"

SYSTEM_MSG: Final[str] = (
    "You are a senior full‑stack engineer and Frappe/ERPNext expert. Review the provided code snippet for any issues or improvements. "
    "Focus on architecture (compliance with Frappe/ERPNext conventions for DocTypes, Hooks, workflows, permissions), "
    "code quality (formatting, linting, type annotations, using environment config for secrets), "
    "testing (adequate unit/E2E test coverage), "
    "security (vulnerabilities or unsafe patterns, proper use of whitelisted API functions), "
    "and documentation/maintainability (Changelog updates, code comments, fixtures). "
    "If any issues are found, return a markdown bullet list of them (grouped by category if applicable). "
    "If the code can be fully corrected, return the revised code in a code block instead. "
    "Provide no commentary outside the list or code block."
)

SECRET_PATTERNS: Final[list[re.Pattern[str]]] = [
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"(?:ghp|gho|ghs|ghu)_[0-9A-Za-z]{36}"),
    re.compile(r"-----BEGIN (?:RSA|EC) PRIVATE KEY-----"),
]

_CODE_BLOCK_RE: Final[re.Pattern[str]] = re.compile(
    r"```(?:[\w.+-]+)?\n(?P<code>[\s\S]+?)\n```",
    re.MULTILINE,
)
