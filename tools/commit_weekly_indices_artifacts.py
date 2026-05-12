from __future__ import annotations

import glob
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ARTIFACT_PATTERNS = [
    "output_indices/weekly_indices_review_*.md",
    "output_indices/run_manifests/*.json",
    "output_indices/research/*.json",
    "output_indices/macro/*.json",
    "output_indices/runtime/*.json",
    "output_indices/index_candidate_ranking_*.json",
    "output_indices/index_discovery_coverage_*.json",
    "output_indices/index_portfolio_state.json",
    "output_indices/index_valuation_history.csv",
    "output_indices/index_recommendation_scorecard.csv",
    "output_indices/pricing/*.json",
]


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    print("+ " + " ".join(cmd))
    result = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if result.stdout:
        print(result.stdout.rstrip())
    if check and result.returncode != 0:
        raise RuntimeError(f"Command failed with exit code {result.returncode}: {' '.join(cmd)}")
    return result


def existing_artifact_files() -> list[Path]:
    files: list[Path] = []
    for pattern in ARTIFACT_PATTERNS:
        for match in glob.glob(pattern):
            path = Path(match)
            if path.is_file() and path not in files:
                files.append(path)
    return sorted(files)


def status_for_artifacts() -> str:
    return run(["git", "status", "--porcelain", "--", *ARTIFACT_PATTERNS], check=False).stdout.strip()


def snapshot_artifacts(files: list[Path], temp_root: Path) -> None:
    for path in files:
        target = temp_root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)


def restore_artifacts(temp_root: Path) -> None:
    for source in temp_root.rglob("*"):
        if not source.is_file():
            continue
        rel = source.relative_to(temp_root)
        target = Path(rel)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def git_add_artifacts() -> None:
    run(["git", "add", *ARTIFACT_PATTERNS], check=False)


def commit_artifacts() -> bool:
    git_add_artifacts()
    diff = run(["git", "diff", "--cached", "--quiet"], check=False)
    if diff.returncode == 0:
        print("No composed report, manifest, research, macro, runtime, pricing, scorecard, or candidate artifact changes to commit.")
        return False
    run(["git", "commit", "-m", "Persist Weekly Indices run manifest and artifacts [skip ci]"])
    return True


def push_with_retries() -> None:
    for attempt in range(1, 4):
        print(f"PUSH_ATTEMPT | attempt={attempt}")
        run(["git", "fetch", "origin", "main"])
        run(["git", "pull", "--rebase", "--autostash", "origin", "main"])
        push = run(["git", "push", "origin", "HEAD:main"], check=False)
        if push.returncode == 0:
            print("ARTIFACT_PUSH_OK")
            return
        print("ARTIFACT_PUSH_RETRY | non-fast-forward or transient push failure")
    raise RuntimeError("Failed to push Weekly Indices artifacts after 3 attempts.")


def main() -> None:
    run(["git", "config", "user.name", "github-actions[bot]"])
    run(["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"])

    files = existing_artifact_files()
    if not files and not status_for_artifacts():
        print("No artifact files found to commit.")
        return

    with tempfile.TemporaryDirectory(prefix="weekly-index-artifacts-") as temp_dir:
        temp_root = Path(temp_dir)
        snapshot_artifacts(files, temp_root)

        # Reruns and concurrent ChatGPT commits can advance main while this job is
        # running. Reset to the current remote first, then restore generated
        # artifacts, so commit-back is not rejected as non-fast-forward.
        run(["git", "fetch", "origin", "main"])
        run(["git", "checkout", "main"])
        run(["git", "reset", "--hard", "origin/main"])
        restore_artifacts(temp_root)

    if not commit_artifacts():
        return
    push_with_retries()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ARTIFACT_COMMIT_FAILED | {exc}")
        sys.exit(1)
