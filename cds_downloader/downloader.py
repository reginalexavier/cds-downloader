"""Execute CDS download tasks."""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import cdsapi

from .requests import DownloadTask


def print_dry_run(tasks: list[DownloadTask]) -> None:
    for task in tasks:
        payload = {
            "dataset": task.dataset,
            "request": task.request,
            "target": str(task.target),
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))


def _client_kwargs(*, timeout: int | None, retry_max: int, quiet: bool) -> dict[str, Any]:
    kwargs: dict[str, Any] = {
        "retry_max": retry_max,
        "quiet": quiet,
    }
    if timeout is not None:
        kwargs["timeout"] = timeout
    return kwargs


def download_task(task: DownloadTask, *, timeout: int | None, retry_max: int, quiet: bool) -> Path:
    task.target.parent.mkdir(parents=True, exist_ok=True)
    client = cdsapi.Client(**_client_kwargs(timeout=timeout, retry_max=retry_max, quiet=quiet))
    print(f"Downloading {task.dataset} -> {task.target}")
    client.retrieve(task.dataset, task.request, str(task.target))
    return task.target


def run_downloads(
    tasks: list[DownloadTask],
    *,
    max_workers: int,
    timeout: int | None,
    retry_max: int,
    quiet: bool,
) -> list[Path]:
    if max_workers < 1:
        raise ValueError("--max-workers must be at least 1.")

    if max_workers == 1:
        return [download_task(task, timeout=timeout, retry_max=retry_max, quiet=quiet) for task in tasks]

    completed = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(download_task, task, timeout=timeout, retry_max=retry_max, quiet=quiet) for task in tasks
        ]
        for future in as_completed(futures):
            completed.append(future.result())
    return completed
