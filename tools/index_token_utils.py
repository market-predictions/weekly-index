from __future__ import annotations

from pathlib import Path


def token_from_close_date(close_date: str) -> str:
    yyyy, mm, dd = close_date.split('-')
    return f'{yyyy[2:]}{mm}{dd}'


def report_path_for_token(token: str, output_dir: str | Path = 'output_indices') -> Path:
    return Path(output_dir) / f'weekly_indices_review_{token}.md'


def report_path_for_close_date(close_date: str, output_dir: str | Path = 'output_indices') -> Path:
    return report_path_for_token(token_from_close_date(close_date), output_dir)
