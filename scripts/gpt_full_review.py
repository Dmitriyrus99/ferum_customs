#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GPT-powered asynchronous code-review helper.

This script automates code reviews using the OpenAI API. It scans a source code
repository, identifies new or modified files, sends them for review, and
generates reports and patch files based on the AI's feedback.

Key Features:
- Asynchronous processing for high performance.
- Caching of results to avoid re-reviewing unchanged files.
- Automatic chunking of large files to fit model context limits.
- Robust error handling with exponential backoff for API calls.
- Generation of .patch files for direct application of suggestions.
- Generation of .md reports for issue lists.
- Respects .gitignore rules.
- Scans for hardcoded secrets to prevent leaks.

Version: 2.2 (Refactored for clarity and robustness, 2025-07-31)
"""

# Часть 1: Импорты и константы

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
from dataclasses import asdict, dataclass
from hashlib import md5
from typing import Dict, Final, Iterable, List, Set

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
# Константы и настройки (Constants and Configuration)
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

EXTS: Final[Set[str]] = {
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
IGNORE_EXTS: Final[Set[str]] = {
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
IGNORE_PATTERNS: Final[Set[str]] = {
    "/node_modules/",
    "/__pycache__",
    "/.git/",
    "/env/",
    "secrets/",
}
CACHE_FILE_NAME: Final[str] = ".review_cache.json"

SYSTEM_MSG: Final[str] = (
    "You are a senior full-stack engineer. Review the provided code snippet "
    "for bugs, anti-patterns, and security vulnerabilities. "
    "Return a code block with the corrected code or a markdown list of issues."
    "No extra commentary allowed."
)

SECRET_PATTERNS: Final[List[re.Pattern[str]]] = [
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"(?:ghp|gho|ghs|ghu)_[0-9A-Za-z]{36}"),
    re.compile(r"-----BEGIN (?:RSA|EC) PRIVATE KEY-----"),
]

_CODE_BLOCK_RE: Final[re.Pattern[str]] = re.compile(
    r"```(?:\w+)?\s*\n([\s\S]*?)```", re.MULTILINE
)

# Глобальные объекты (Global objects)
console: Final[Console] = Console()
enc: tiktoken.Encoding | None = None

# ──────────────────────────────────────────────────────────────────────────────
# Классы и типы данных (Data Classes and Types)
# ──────────────────────────────────────────────────────────────────────────────

@dataclass(slots=True)
class ReviewResult:
    """Stores the result of a single file review."""
    src: pathlib.Path
    content_hash: str
    diff_file: str | None = None
    md_file: str | None = None
    status: str = "reviewed"

# ──────────────────────────────────────────────────────────────────────────────
# Утилиты (Utility Functions)
# ──────────────────────────────────────────────────────────────────────────────


def get_tokenizer_for_model(model: str) -> None:
    """Initializes the global tokenizer based on the model name."""
    global enc
    try:
        enc = tiktoken.encoding_for_model(model)
    except KeyError:
        console.print(
            f"[yellow]⚠️  Нет токенизатора для {model}. Использую cl100k_base.[/yellow]"
        )
        enc = tiktoken.get_encoding("cl100k_base")

def _token_len(text: str) -> int:
    """Calculates the number of tokens in a string."""
    if enc is None:
        raise RuntimeError("Tokenizer not initialised; call get_tokenizer_for_model() first.")
    return len(enc.encode(text))

def get_gitignore_spec(repo_path: pathlib.Path) -> pathspec.PathSpec:
    """Loads and parses the .gitignore file from the repository root."""
    gitignore_file = repo_path / ".gitignore"
    lines = (
        gitignore_file.read_text("utf-8").splitlines()
        if gitignore_file.is_file()
        else []
    )
    return pathspec.PathSpec.from_lines("gitwildmatch", lines)


def iter_source_files(
    scan_path: pathlib.Path, repo_path: pathlib.Path
) -> Iterable[pathlib.Path]:
    gitignore_spec = get_gitignore_spec(repo_path)
    for p in scan_path.rglob("*"):
        if not p.is_file():
            continue

        relative_path = p.relative_to(repo_path)
        if gitignore_spec.match_file(str(relative_path)):
            continue

        p_low_suffix = p.suffix.lower()
        path_str = p.as_posix()
        if (
            p_low_suffix in EXTS
            and p_low_suffix not in IGNORE_EXTS
            and not any(pattern in path_str for pattern in IGNORE_PATTERNS)
            and f"/{out_dir_name}/" not in path_str
        ):
            yield p

def parse_llm_reply(reply: str) -> tuple[str, str]:
    """Parses the LLM reply to extract code blocks or return markdown."""
    match = _CODE_BLOCK_RE.search(reply)
    if match:
        return "code", match.group(1).strip()
    return "markdown", reply.strip()


@dataclass(slots=True)
class ReviewResult:
    src: pathlib.Path
    content_hash: str
    diff_file: str | None = None
    md_file: str | None = None
    status: str = "reviewed"


def _token_len(text: str) -> int:
    if enc is None:
        raise RuntimeError(
            "Tokenizer not initialised; call get_tokenizer_for_model() first."
        )
    return len(enc.encode(text))


def chunkify(text: str, max_tokens: int, framing_tokens: int = 64) -> list[str]:
    budget = max_tokens - framing_tokens
    if budget <= 0:
        return [text]

    lines = text.splitlines()
    chunks: list[str] = []
    current: list[str] = []
    current_tokens = 0
    for line in lines:
        line_tokens = _token_len(line) + 1
        if current_tokens + line_tokens > budget and current:
            chunks.append("\n".join(current))
            current, current_tokens = [line], line_tokens
        else:
            current.append(line)
            current_tokens += line_tokens

    if current:
        chunks.append("\n".join(current))
    return chunks

# ──────────────────────────────────────────────────────────────────────────────
# Взаимодействие с API (API Interaction)
# ──────────────────────────────────────────────────────────────────────────────

async def _call_llm(
    client: AsyncOpenAI, messages: list[dict[str, str]], model: str
) -> str:
    async def _one_call() -> str:
        stream = await client.chat.completions.create(
            model=model, messages=messages, temperature=0, stream=True
        )
        parts = [chunk.choices[0].delta.content or "" async for chunk in stream]
        return "".join(parts).strip()

    for attempt in range(1, OPENAI_RETRY_ATTEMPTS + 1):
        try:
            return await _one_call()
        except (RateLimitError, APITimeoutError, APIConnectionError, APIError) as exc:
            if attempt == OPENAI_RETRY_ATTEMPTS:
                raise
            delay = min(OPENAI_BASE_DELAY * 2 ** (attempt - 1), OPENAI_MAX_DELAY)
            delay *= random.uniform(0.75, 1.25)
            console.log(
                f"[yellow]LLM transient error ({exc}); retry {attempt}/{OPENAI_RETRY_ATTEMPTS} in {delay:.1f}s…[/yellow]"
            )
            await asyncio.sleep(delay)
    raise RuntimeError("Unreachable retry logic") # Should not be reached

async def review_chunk(
    client: AsyncOpenAI, code: str, rel_path: str, model: str, sem: asyncio.Semaphore
) -> str:
    """Sends a single code chunk to the LLM for review."""
    async with sem:
        messages = [
            {"role": "system", "content": SYSTEM_MSG},
            {"role": "user", "content": f"File: {rel_path}\n```\n{code}\n```"},
        ]
        try:
            return await _call_llm(client, messages, model)
        except Exception as exc:
            console.print(f"[red]Не удалось обработать чанк для {rel_path}: {exc}[/red]")
            return f"/* REVIEW FAILED: {exc} */"

# ──────────────────────────────────────────────────────────────────────────────
# Обработка файлов и артефактов (File and Artifact Handling)
# ──────────────────────────────────────────────────────────────────────────────


def _write_artifact(
    out_dir: pathlib.Path, rel_repo_path: pathlib.Path, ext: str, content: str
) -> str:
    sanitized = str(rel_repo_path).replace("/", "_").replace("\\", "_")
    # Add a short hash of the full path to prevent filename collisions
    name = f"{sanitized}.{md5(str(rel_repo_path).encode()).hexdigest()[:8]}{ext}"
    path = out_dir / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, "utf-8", newline="\n")
    return name

def _contains_secret(text: str) -> bool:
    """Checks if the given text contains any patterns that look like secrets."""
    return any(p.search(text) for p in SECRET_PATTERNS)


async def review_file(
    client: AsyncOpenAI,
    p: pathlib.Path,
    repo_path: pathlib.Path,
    scan_path: pathlib.Path,
    out_dir: pathlib.Path,
    model: str,
    max_tokens: int,
    sem: asyncio.Semaphore,
) -> ReviewResult:
    """
    Manages the full review process for a single file.
    This includes reading, checking for secrets, chunking, and saving results.
    """
    rel_repo_path = p.relative_to(repo_path)
    content_bytes = p.read_bytes()
    content_hash = md5(content_bytes).hexdigest()

    try:
        original_text = content_bytes.decode("utf-8", errors="ignore")
    except UnicodeDecodeError as exc:
        console.print(f"[red]Не читаю {p}: {exc}[/red]")
        return ReviewResult(
            src=rel_repo_path, content_hash=content_hash, status="read_error"
        )

    if not original_text.strip():
        return ReviewResult(
            src=rel_repo_path, content_hash=content_hash, status="skipped_empty"
        )

    if _contains_secret(original_text):
        console.print(f"[red]⚠️  Пропущено {p}: подозрение на секреты.[/red]")
        return ReviewResult(
            src=rel_repo_path, content_hash=content_hash, status="skipped_secrets"
        )

    framing_tokens = _token_len(SYSTEM_MSG) + 128  # Reserve tokens for system prompt and formatting
    chunks = chunkify(original_text, max_tokens, framing_tokens)

    # Handle multi-chunk files by creating a single report.
    if len(chunks) > 1:
        notes = []
        for chunk in chunks:
            reply = await review_chunk(
                client, chunk, str(p.relative_to(scan_path)), model, sem
            )
            kind, content = parse_llm_reply(reply)
            if content.strip():
                preview = chunk[:200].replace("\n", " ") + (
                    "…" if len(chunk) > 200 else ""
                )
                notes.append(f"### Review for chunk ({preview})\n\n{content}")
        notes_file = _write_artifact(
            out_dir / "reports", rel_repo_path, ".md", "\n\n---\n\n".join(notes)
        )
        return ReviewResult(
            src=rel_repo_path, content_hash=content_hash, md_file=notes_file
        )

    reply = await review_chunk(
        client, original_text, str(p.relative_to(scan_path)), model, sem
    )
    kind, content = parse_llm_reply(reply)

    diff_file: str | None = None
    md_file: str | None = None

    if kind == "code" and content and content != original_text.strip():
        diff_text = "".join(difflib.unified_diff(
            original_text.splitlines(keepends=True),
            content.splitlines(keepends=True),
            fromfile=f"a/{rel_repo_path}",
            tofile=f"b/{rel_repo_path}",
        ))
        if diff_text.strip():
            diff_file = _write_artifact(
                out_dir / "patches", rel_repo_path, ".patch", diff_text
            )
    elif kind == "markdown" and content.strip():
        md_file = _write_artifact(out_dir / "reports", rel_repo_path, ".md", content)

    return ReviewResult(
        src=rel_repo_path,
        content_hash=content_hash,
        diff_file=diff_file,
        md_file=md_file,
    )


async def main(cfg: argparse.Namespace) -> None:
    repo_path = pathlib.Path(cfg.repo_path).resolve()
    scan_path = pathlib.Path(cfg.scan_path).resolve()
    out_dir = repo_path / pathlib.Path(cfg.out_dir)
    out_dir.mkdir(exist_ok=True)
    cache_path = out_dir / CACHE_FILE_NAME

    get_tokenizer_for_model(cfg.model)

    if repo_path not in scan_path.parents and repo_path != scan_path:
        console.print(
            f"[red]scan-path '{scan_path}' не лежит внутри repo-path '{repo_path}'.[/red]"
        )
        return

    all_files = list(iter_source_files(scan_path, repo_path))

    cache = {}
    if not no_cache and cache_path.is_file():
        try:
            cache = json.loads(cache_path.read_text("utf-8"))
        except (json.JSONDecodeError, FileNotFoundError):
            cache = {}

    files_to_review, cached_results = [], []
    console.print("[cyan]Планирование ревью: проверка кэша...[/cyan]")
    for p in all_files:
        content_hash = md5(p.read_bytes()).hexdigest()
        rel_path_str = str(p.relative_to(repo_path))
        if (
            rel_path_str in cache
            and cache[rel_path_str].get("content_hash") == content_hash
        ):
            cached_item = cache[rel_path_str]
            cached_results.append(
                ReviewResult(
                    src=pathlib.Path(cached_item["src"]),
                    content_hash=cached_item["content_hash"],
                    diff_file=cached_item.get("diff_file"),
                    md_file=cached_item.get("md_file"),
                    status="cached",
                )
            )
        else:
            files_to_review.append(p)
    return files_to_review, cached_results

async def _run_reviews(
    files_to_review: List[pathlib.Path], client: AsyncOpenAI, repo_path: pathlib.Path,
    scan_path: pathlib.Path, out_dir: pathlib.Path, cfg: argparse.Namespace
) -> List[ReviewResult]:
    """Executes the review process for the given files concurrently."""
    if not files_to_review:
        return []

    console.print(f"[cyan]Начинаю GPT-ревью {len(files_to_review)} новых/изменённых файлов...[/cyan]")
    sem = asyncio.Semaphore(cfg.max_concurrency)
    results = []

    async with AsyncOpenAI() as client:
        if files_to_review:
            console.print(
                f"[cyan]▶ {len(cached_results)} файлов из кэша. Начинаю GPT‑ревью {len(files_to_review)} новых/изменённых файлов…[/cyan]"
            )
            progress = Progress(
                SpinnerColumn(),
                TextColumn("{task.description}"),
                BarColumn(),
                "[progress.percentage]{task.percentage:>3.0f}%",
                TimeElapsedColumn(),
                console=console,
            )
            with progress:
                task_id = progress.add_task(
                    "[green]Анализ…", total=len(files_to_review)
                )
                async with asyncio.TaskGroup() as tg:  # type: ignore[attr-defined]
                    results_fut = [
                        tg.create_task(
                            review_file(
                                client,
                                p,
                                repo_path,
                                scan_path,
                                out_dir,
                                cfg.model,
                                cfg.maxtok,
                                sem,
                            )
                        )
                        for p in files_to_review
                    ]
                    for fut in results_fut:
                        cached_results.append(await fut)
                        progress.advance(task_id)
        else:
            console.print(
                "[green]✔ Все файлы актуальны в кэше. Новых изменений для ревью нет.[/green]"
            )

    new_cache = {str(res.src): asdict(res) for res in cached_results}
    cache_path.write_text(json.dumps(new_cache, indent=2, ensure_ascii=False), "utf-8")

    summary_lines, cached_lines, patches_present = [], [], False
    for res in sorted(all_results, key=lambda r: str(r.src)):
        src_str = str(res.src)
        line = None
        if res.diff_file:
            patches_present = True
            line = f"* PATCH: `{src_str}` → [{res.diff_file}]({out_dir_str}/patches/{res.diff_file})"
        elif res.md_file:
            line = f"* ISSUES: `{src_str}` → [{res.md_file}]({out_dir_str}/reports/{res.md_file})"

        if line:
            if res.status == "cached":
                cached_lines.append(f"{line} (из кэша)")
            else:
                summary_lines.append(line)

    if not summary_lines and not cached_lines:
        console.print("\n[bold green]✔ Замечаний не найдено![/]")
        return

    summary_path = repo_path / "SUMMARY.md"
    header = f"# GPT Code Review Report\n\n**Date:** {_dt.datetime.now():%Y-%m-%d %H:%M:%S}\n\n"
    apply_instr = ""
    if patches_present:
        apply_instr = textwrap.dedent(
            rf"""
            ## Как применить патчи

        Чтобы применить предложенные исправления, выполните следующие команды в корне репозитория:
        ```bash
        # Создайте новую ветку для ревью
        git checkout -b gpt-review-patches

        # Примените все патчи
        find {out_dir_str}/patches -type f -name '*.patch' -exec git apply {{}} \\;

        # Проверьте изменения и сделайте коммит
        git status
        git add .
        git commit -m "Apply GPT-review patches"
        ```
        ---
        """)

    summary_content = header + apply_instr
    if summary_lines:
        summary_content += (
            "### Новые/изменённые файлы\n\n" + "\n".join(summary_lines) + "\n\n"
        )
    if cached_lines:
        summary_content += (
            "### Без изменений (из кэша)\n\n" + "\n".join(cached_lines) + "\n\n"
        )

    summary_path.write_text(summary_content, "utf-8")
    console.print(f"\n[green]✔ Отчёт сохранён:[/] {summary_path}")


# ─────────────────────────────────────────────────────────────────────────────
#                                      CLI
# ─────────────────────────────────────────────────────────────────────────────


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Асинхронный GPT код‑ревью с кэшированием.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--repo-path",
        default=str(DEFAULT_REPO_PATH),
        help="Путь к корню Git репозитория.",
    )
    parser.add_argument(
        "--scan-path",
        default=str(DEFAULT_SCAN_PATH),
        help="Путь к директории для сканирования.",
    )
    parser.add_argument(
        "--out-dir",
        default=str(DEFAULT_OUT_DIR),
        help="Папка для сохранения отчётов (относительно repo-path).",
    )
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Модель OpenAI.")
    parser.add_argument(
        "--maxtok",
        type=int,
        default=DEFAULT_MAXTOK,
        help="Макс. токенов в запросе (ceiling).",
    )
    parser.add_argument(
        "--list-files", action="store_true", help="Показать список файлов и выйти."
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Отключить кэширование и проверить все файлы заново.",
    )
    parser.add_argument(
        "--max-concurrency",
        type=int,
        default=MAX_CONCURRENCY,
        help="Параллельность запросов к LLM.",
    )
    return parser.parse_args()


def _check_env() -> None:
    if not os.environ.get("OPENAI_API_KEY"):
        console.print("[red]OPENAI_API_KEY не установлен![/red]")
        raise SystemExit(1)


if __name__ == "__main__":
    args = _parse_args()
    if not args.list_files:
        _check_env()
    try:
        asyncio.run(main(args))
    except (KeyboardInterrupt, asyncio.CancelledError):
        console.print("\n[yellow]Прервано пользователем.[/yellow]")
