#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GPT‑powered asynchronous code‑review helper with local diff generation.
Version: 2.0  (2025‑07‑31)
Implements the highest‑impact improvements requested:
  • resilient exponential back‑off + jitter for any OpenAI transient error
  • token‑by‑token streaming to minimise latency & memory
  • adaptive CPU‑aware concurrency (up to 16)
  • auto‑adjusted max_tokens per chunk (system+user framing deducted)
  • asyncio.TaskGroup (Python ≥ 3.11) for clearer parallelism
  • single compiled regexes for hot‑paths
  • secret‑pattern guard to avoid leaking credentials to the LLM
  • extended ignore patterns & safe LF line endings everywhere
  • small UX tweaks (colourful Rich progress, improved SUMMARY.md hints)
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
from dataclasses import dataclass, asdict
from hashlib import md5
from typing import Iterable, List, Dict, Set, Final

import pathspec  # type: ignore
from openai import AsyncOpenAI, APIError, APITimeoutError, RateLimitError, APIConnectionError  # type: ignore
import tiktoken  # type: ignore
from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TimeElapsedColumn,
    TextColumn,
)

# ──────────────────────────────────────────────────────────────────────────────
#                              DEFAULTS & CONSTS
# ──────────────────────────────────────────────────────────────────────────────
DEFAULT_REPO_PATH: Final[pathlib.Path] = pathlib.Path.cwd()
DEFAULT_SCAN_PATH: Final[pathlib.Path] = pathlib.Path.cwd()
DEFAULT_OUT_DIR: Final[pathlib.Path] = pathlib.Path("code_review")
DEFAULT_MODEL: Final[str] = "gpt-4o-mini"
DEFAULT_MAXTOK: Final[int] = 12_000   # hard ceiling per request
MAX_CONCURRENCY: Final[int] = min((os.cpu_count() or 2) * 2, 16)
OPENAI_RETRY_ATTEMPTS: Final[int] = 6
OPENAI_BASE_DELAY: Final[float] = 2.0   # seconds
OPENAI_MAX_DELAY: Final[float] = 30.0   # seconds

EXTS: Final[Set[str]] = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css", ".scss", ".json", ".yaml", ".yml", ".sh", ".sql",
}
IGNORE_EXTS: Final[Set[str]] = {
    ".zip", ".tar", ".gz", ".rar", ".7z", ".tgz", ".bz2", ".db", ".sqlite", ".sqlite3", ".pyc", ".pyd", ".so",
    ".o", ".lock", ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".jpg", ".jpeg", ".png", ".gif",
    ".bmp", ".svg", ".pem", ".log", ".DS_Store",
}
IGNORE_PATTERNS: Final[Set[str]] = {
    "/node_modules/", "/__pycache__", "/.git/", "/build/", "/dist/", "/.cache/", "/env/", "/archived/",
    "/keys/", "id_rsa", "_rsa", ".aws/", "secrets/",
}
CACHE_FILE_NAME: Final[str] = ".review_cache.json"

SYSTEM_MSG: Final[str] = (
    "You are a senior full‑stack engineer. Review the provided code snippet "
    "for bugs, anti‑patterns, and security vulnerabilities. "
    "If you find issues that can be fixed, return a code block with the complete, corrected code. "
    "If no fixes are needed or the fixes are too complex, return a markdown list of the issues you found. "
    "IMPORTANT: Your response must contain ONLY the full code block (including ```language) or ONLY the markdown list, with absolutely no extra commentary."
)

SECRET_PATTERNS: Final[List[re.Pattern[str]]] = [
    re.compile(r"AKIA[0-9A-Z]{16}"),              # AWS key
    re.compile(r"(?:ghp|gho|ghs|ghu)_[0-9A-Za-z]{36}"),  # GitHub token
    re.compile(r"-----BEGIN (?:RSA|EC) PRIVATE KEY-----"),
]

# pre‑compiled regex for code block extraction
_CODE_BLOCK_RE: Final[re.Pattern[str]] = re.compile(r"```(?:\w+)?\s*\n([\s\S]*?)```", re.MULTILINE)

# ──────────────────────────────────────────────────────────────────────────────
#                             GLOBALS (init later)
# ──────────────────────────────────────────────────────────────────────────────
console: Final[Console] = Console()
client: AsyncOpenAI | None = None
enc: tiktoken.Encoding | None = None

# ──────────────────────────────────────────────────────────────────────────────
#                               LOW‑LEVEL UTILS
# ──────────────────────────────────────────────────────────────────────────────

def get_tokenizer_for_model(model: str) -> None:
    global enc
    try:
        enc = tiktoken.encoding_for_model(model)
    except KeyError:  # fallback for unknown model
        console.print(f"[yellow]⚠️  Нет токенизатора для {model}. Использую cl100k_base.[/yellow]")
        enc = tiktoken.get_encoding("cl100k_base")


def get_gitignore_spec(repo_path: pathlib.Path) -> pathspec.PathSpec:
    gitignore_file = repo_path / ".gitignore"
    lines: List[str] = gitignore_file.read_text("utf-8").splitlines() if gitignore_file.is_file() else []
    return pathspec.PathSpec.from_lines("gitwildmatch", lines)


def iter_source_files(scan_path: pathlib.Path, repo_path: pathlib.Path) -> Iterable[pathlib.Path]:
    gitignore_spec = get_gitignore_spec(repo_path)
    out_dir_name = DEFAULT_OUT_DIR.name
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
    """Return (kind, payload): kind∈{"code", "markdown"}."""
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


# ──────────────────────────────────────────────────────────────────────────────
#                          TOKEN & CHUNK MANAGEMENT
# ──────────────────────────────────────────────────────────────────────────────

def _token_len(text: str) -> int:
    if enc is None:
        raise RuntimeError("Tokenizer not initialised; call get_tokenizer_for_model() first.")
    return len(enc.encode(text))


def chunkify(text: str, max_tokens: int, framing_tokens: int = 64) -> List[str]:
    """Splits *text* so that each chunk fits within max_tokens‑framing_tokens."""
    budget = max_tokens - framing_tokens
    if budget <= 0:
        return [text]

    lines = text.splitlines()
    chunks: List[str] = []
    current: List[str] = []
    current_tokens = 0
    for line in lines:
        line_tokens = _token_len(line) + 1  # newline
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
#                           LLM CALL WITH RETRIES
# ──────────────────────────────────────────────────────────────────────────────

async def _call_llm(messages: list[dict[str, str]], model: str) -> str:
    """Send messages to OpenAI chat API with streaming and retries."""

    async def _one_call() -> str:
        assert client is not None  # safety
        stream = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0,
            stream=True,
        )
        parts: List[str] = []
        async for chunk in stream:
            parts.append(chunk.choices[0].delta.content or "")
        return "".join(parts).strip()

    for attempt in range(1, OPENAI_RETRY_ATTEMPTS + 1):
        try:
            return await _one_call()
        except (
            RateLimitError,
            APITimeoutError,
            APIConnectionError,
            APIError,
        ) as exc:
            if attempt == OPENAI_RETRY_ATTEMPTS:
                raise
            delay = min(OPENAI_BASE_DELAY * 2 ** (attempt - 1), OPENAI_MAX_DELAY)
            delay *= random.uniform(0.75, 1.25)  # jitter
            console.log(f"[yellow]LLM transient error ({exc}); retry {attempt}/{OPENAI_RETRY_ATTEMPTS} in {delay:.1f}s…[/yellow]")
            await asyncio.sleep(delay)
    # Should never reach here
    raise RuntimeError("Unreachable retry logic")


async def review_chunk(code: str, rel_path: str, model: str, sem: asyncio.Semaphore) -> str:
    async with sem:
        messages = [
            {"role": "system", "content": SYSTEM_MSG},
            {"role": "user", "content": f"File: {rel_path}\n```\n{code}\n```"},
        ]
        try:
            return await _call_llm(messages, model)
        except Exception as exc:  # already logged in _call_llm
            return f"/* REVIEW FAILED: {exc} */"


# ──────────────────────────────────────────────────────────────────────────────
#                       ARTIFACT WRITING & HASHING UTILS
# ──────────────────────────────────────────────────────────────────────────────

def _write_artifact(out_dir: pathlib.Path, rel_repo_path: pathlib.Path, ext: str, content: str) -> str:
    sanitized = str(rel_repo_path).replace("/", "_").replace("\\", "_")
    name = f"{sanitized}.{md5(str(rel_repo_path).encode()).hexdigest()[:8]}{ext}"
    path = out_dir / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, "utf-8", newline="\n")  # force LF endings
    return name


# ──────────────────────────────────────────────────────────────────────────────
#                            PER‑FILE REVIEW LOGIC
# ──────────────────────────────────────────────────────────────────────────────

async def _contains_secret(text: str) -> bool:
    return any(p.search(text) for p in SECRET_PATTERNS)


async def review_file(
    p: pathlib.Path,
    repo_path: pathlib.Path,
    scan_path: pathlib.Path,
    out_dir: pathlib.Path,
    model: str,
    max_tokens: int,
    sem: asyncio.Semaphore,
) -> ReviewResult:
    rel_repo_path = p.relative_to(repo_path)
    content_bytes = p.read_bytes()
    content_hash = md5(content_bytes).hexdigest()

    try:
        original_text = content_bytes.decode("utf-8", errors="ignore")
    except UnicodeDecodeError as exc:
        console.print(f"[red]Не читаю {p}: {exc}[/red]")
        return ReviewResult(src=rel_repo_path, content_hash=content_hash, status="read_error")

    if not original_text.strip():
        return ReviewResult(src=rel_repo_path, content_hash=content_hash, status="skipped_empty")

    if await _contains_secret(original_text):
        console.print(f"[red]⚠️  Пропущено {p}: подозрение на секреты.[/red]")
        return ReviewResult(src=rel_repo_path, content_hash=content_hash, status="skipped_secrets")

    framing_tokens = 64  # rough overhead for system+user messages
    chunks = (
        chunkify(original_text, max_tokens, framing_tokens)
        if _token_len(original_text) > max_tokens - framing_tokens
        else [original_text]
    )

    # If file split into chunks, produce only markdown notes
    if len(chunks) > 1:
        notes: List[str] = []
        for chunk in chunks:
            reply = await review_chunk(chunk, str(p.relative_to(scan_path)), model, sem)
            kind, content = parse_llm_reply(reply)
            if content:
                preview = chunk[:200].replace("\n", " ") + ("…" if len(chunk) > 200 else "")
                notes.append(f"### Review for chunk ({preview})\n\n{content}")
        md_file = _write_artifact(out_dir, rel_repo_path, ".md", "\n\n---\n\n".join(notes))
        return ReviewResult(src=rel_repo_path, content_hash=content_hash, md_file=md_file)

    # Whole file fits in one chunk
    reply = await review_chunk(original_text, str(p.relative_to(scan_path)), model, sem)
    kind, content = parse_llm_reply(reply)

    diff_file: str | None = None
    md_file: str | None = None

    if kind == "code" and content and content != original_text.strip():
        diff_text = "".join(
            difflib.unified_diff(
                original_text.splitlines(keepends=True),
                content.splitlines(keepends=True),
                fromfile=f"a/{rel_repo_path}",
                tofile=f"b/{rel_repo_path}",
            )
        )
        if diff_text:
            diff_file = _write_artifact(out_dir, rel_repo_path, ".patch", diff_text)
    elif kind == "markdown" and content:
        md_file = _write_artifact(out_dir, rel_repo_path, ".md", content)

    return ReviewResult(src=rel_repo_path, content_hash=content_hash, diff_file=diff_file, md_file=md_file)


# ──────────────────────────────────────────────────────────────────────────────
#                                   MAIN LOGIC
# ──────────────────────────────────────────────────────────────────────────────

async def main(cfg) -> None:
    global client
    client = AsyncOpenAI()

    repo_path = pathlib.Path(cfg.repo_path).resolve()
    scan_path = pathlib.Path(cfg.scan_path).resolve()
    out_dir = repo_path / pathlib.Path(cfg.out_dir)
    out_dir.mkdir(exist_ok=True)
    cache_path = out_dir / CACHE_FILE_NAME

    get_tokenizer_for_model(cfg.model)

    if repo_path not in scan_path.parents and repo_path != scan_path:
        console.print(f"[red]scan-path '{scan_path}' не лежит внутри repo-path '{repo_path}'.[/red]")
        return

    # --- collect files
    all_files = list(iter_source_files(scan_path, repo_path))

    # --- load cache
    cache: Dict[str, Dict] = {}
    if not cfg.no_cache and cache_path.is_file():
        try:
            cache = json.loads(cache_path.read_text("utf-8"))
        except (json.JSONDecodeError, FileNotFoundError):
            cache = {}

    files_to_review: List[pathlib.Path] = []
    cached_results: List[ReviewResult] = []

    for p in all_files:
        rel_path_str = str(p.relative_to(repo_path))
        content_hash = md5(p.read_bytes()).hexdigest()
        if rel_path_str in cache and cache[rel_path_str].get("content_hash") == content_hash:
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

    # Option: only list files and exit
    if cfg.list_files:
        (repo_path / "file_list_for_review.txt").write_text(
            "\n".join(str(p.relative_to(repo_path)) for p in all_files),
            "utf-8",
        )
        console.print("[green]Список всех найденных файлов сохранён.[/green]")
        return

    if not files_to_review and not cached_results:
        console.print("[yellow]Файлы не найдены – проверьте фильтры.[/yellow]")
        return

    # --- review new/changed files
    sem = asyncio.Semaphore(MAX_CONCURRENCY)

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
            task_id = progress.add_task("[green]Анализ…", total=len(files_to_review))
            async with asyncio.TaskGroup() as tg:
                results_fut: List[asyncio.Task[ReviewResult]] = []
                for p in files_to_review:
                    results_fut.append(
                        tg.create_task(
                            review_file(p, repo_path, scan_path, out_dir, cfg.model, cfg.maxtok, sem)
                        )
                    )
                for fut in results_fut:
                    res = await fut
                    cached_results.append(res)
                    progress.advance(task_id)
    else:
        console.print("[green]✔ Все файлы актуальны в кэше. Новых изменений для ревью нет.[/green]")

    final_results = cached_results

    # --- write cache back
    new_cache: Dict[str, Dict] = {}
    for res in final_results:
        serializable = asdict(res)
        serializable["src"] = str(res.src)
        new_cache[str(res.src)] = serializable
    for res in final_results:
        serializable = res.__dict__.copy()
        serializable["src"] = str(res.src)
        new_cache[str(res.src)] = serializable
    cache_path.write_text(json.dumps(new_cache, indent=2, ensure_ascii=False), "utf-8")

    # --- summary generation
    summary_lines: List[str] = []
    cached_lines: List[str] = []
    patches_present = False

    for res in sorted(final_results, key=lambda r: str(r.src)):
        src_str = str(res.src)
        if res.diff_file:
            patches_present = True
            line = f"* PATCH: `{src_str}` → [{res.diff_file}]({cfg.out_dir}/{res.diff_file})"
        elif res.md_file:
            line = f"* ISSUES: `{src_str}` → [{res.md_file}]({cfg.out_dir}/{res.md_file})"
        else:
            continue
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
            f"""
            ## Как применить патчи

            ```bash
            cd {repo_path}
            git checkout -b gpt-review-patches
            find {cfg.out_dir} -type f -name '*.patch' -exec git am {{}} \;
            ```
            ---
            """
        )

    summary_content = header + apply_instr
    if summary_lines:
        summary_content += "### Новые/изменённые файлы\n\n" + "\n".join(summary_lines) + "\n\n"
    if cached_lines:
        summary_content += "### Без изменений (из кэша)\n\n" + "\n".join(cached_lines) + "\n\n"

    summary_path.write_text(summary_content, "utf-8")
    console.print(f"\n[green]✔ Отчёт сохранён:[/] {summary_path}")


# ──────────────────────────────────────────────────────────────────────────────
#                                      CLI
# ──────────────────────────────────────────────────────────────────────────────

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Асинхронный GPT код‑ревью с кэшированием.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--repo-path", default=str(DEFAULT_REPO_PATH), help="Путь к корню Git репозитория.")
    parser.add_argument("--scan-path", default=str(DEFAULT_SCAN_PATH), help="Путь к директории для сканирования.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR), help="Папка для сохранения отчётов (относительно repo-path).")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Модель OpenAI.")
    parser.add_argument("--maxtok", type=int, default=DEFAULT_MAXTOK, help="Макс. токенов в запросе ( ceiling ).")
    parser.add_argument("--list-files", action="store_true", help="Показать список файлов и выйти.")
    parser.add_argument("--no-cache", action="store_true", help="Отключить кэширование и проверить все файлы заново.")
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
