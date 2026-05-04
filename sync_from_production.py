import argparse
import datetime as dt
import os
import shutil
import subprocess
import sys
from pathlib import Path

DEFAULT_HOST = "192.168.15.51"
DEFAULT_USER = "vm-ssh"
DEFAULT_REMOTE = "/home/vm-ssh/gartner"


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    proc = subprocess.run(cmd)
    if proc.returncode != 0:
        raise SystemExit(proc.returncode)


def make_snapshot(workspace: Path) -> Path:
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    snap = workspace / f"prod_snapshot_{stamp}"
    snap.mkdir(parents=True, exist_ok=True)
    return snap


def copy_from_snapshot_to_workspace(snapshot: Path, workspace: Path, exclude: set[str]) -> tuple[int, int]:
    copied_files = 0
    copied_dirs = 0

    for src in snapshot.rglob("*"):
        rel = src.relative_to(snapshot)
        parts = rel.parts
        if parts and parts[0] in exclude:
            continue

        dest = workspace / rel
        if src.is_dir():
            dest.mkdir(parents=True, exist_ok=True)
            copied_dirs += 1
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            copied_files += 1

    return copied_dirs, copied_files


def main() -> None:
    parser = argparse.ArgumentParser(description="Pull latest production files into workspace snapshot.")
    parser.add_argument("--workspace", default=str(Path.cwd()), help="Workspace folder")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--user", default=DEFAULT_USER)
    parser.add_argument("--remote", default=DEFAULT_REMOTE)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Also mirror pulled snapshot into workspace root (excluding local env/cache folders).",
    )
    args = parser.parse_args()

    workspace = Path(args.workspace).resolve()
    if not workspace.exists():
        raise SystemExit(f"Workspace not found: {workspace}")

    snapshot = make_snapshot(workspace)
    print(f"Workspace: {workspace}")
    print(f"Snapshot:  {snapshot}")

    source = f"{args.user}@{args.host}:{args.remote}/."
    run(["scp", "-r", source, str(snapshot)])

    print("✅ Production snapshot pull complete.")

    if args.apply:
        exclude = {
            ".venv",
            "__pycache__",
            ".git",
            ".vscode",
            "node_modules",
            "prod_snapshot_current",
        }
        dirs, files = copy_from_snapshot_to_workspace(snapshot, workspace, exclude)
        print(f"✅ Applied snapshot into workspace. Dirs touched: {dirs}, files copied: {files}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(130)
