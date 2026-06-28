import subprocess
import shutil
import os
import sys
import signal
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.resolve()
PID_FILE = PROJECT_ROOT / "bot.pid"

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"


def log(color, icon, msg):
    print(f"{color}{icon} {msg}{RESET}")


def run_cmd(cmd, cwd=None, timeout=60):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd or PROJECT_ROOT, timeout=timeout)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except FileNotFoundError:
        return -1, "", f"Command not found: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return -2, "", "Timed out"


def git_pull(dry_run=False):
    log(CYAN, "📦", "Pulling latest changes from git...")
    if dry_run:
        code, out, err = run_cmd(["git", "status", "--short"])
        if out:
            log(YELLOW, "📋", "Changed files:")
            for line in out.splitlines():
                print(f"   {line}")
        else:
            log(GREEN, "✅", "Working tree clean")
        return True

    code, out, err = run_cmd(["git", "pull"])
    if code == 0:
        if "Already up to date" in out:
            log(GREEN, "✅", "Already up to date")
        else:
            log(GREEN, "✅", f"Pulled:\n{out}")
        return True
    else:
        log(RED, "❌", f"Git pull failed: {err or out}")
        return False


def install_deps(dry_run=False):
    log(CYAN, "📥", "Installing dependencies...")
    req = PROJECT_ROOT / "requirements.txt"
    if not req.exists():
        log(YELLOW, "⏭️", "No requirements.txt found, skipping")
        return True
    if dry_run:
        log(YELLOW, "📋", f"Would run: pip install -r {req}")
        return True

    code, out, err = run_cmd([sys.executable, "-m", "pip", "install", "-r", str(req), "-q"], timeout=120)
    if code == 0:
        log(GREEN, "✅", "Dependencies installed")
        return True
    else:
        log(RED, "❌", f"pip install failed: {err or out}")
        return False


def install_features(source_dir, dry_run=False):
    source = Path(source_dir).resolve()
    if not source.exists():
        log(RED, "❌", f"Source directory not found: {source}")
        return False

    log(CYAN, "📂", f"Installing features from: {source}")

    copied = 0

    # Copy cog files
    src_cogs = source / "cogs"
    if src_cogs.is_dir():
        dest_cogs = PROJECT_ROOT / "cogs"
        dest_cogs.mkdir(exist_ok=True)
        for f in src_cogs.glob("*.py"):
            dest = dest_cogs / f.name
            if dry_run:
                log(YELLOW, "📋", f"Would copy: {f.name} -> cogs/")
            else:
                shutil.copy2(f, dest)
                log(GREEN, "✅", f"Copied: cogs/{f.name}")
            copied += 1

    # Copy root-level Python files
    for f in source.glob("*.py"):
        if f.name == "update.py":
            continue
        dest = PROJECT_ROOT / f.name
        if dry_run:
            log(YELLOW, "📋", f"Would copy: {f.name}")
        else:
            shutil.copy2(f, dest)
            log(GREEN, "✅", f"Copied: {f.name}")
        copied += 1

    # Copy requirements.txt if exists
    src_req = source / "requirements.txt"
    if src_req.exists():
        dest_req = PROJECT_ROOT / "requirements.txt"
        if dry_run:
            log(YELLOW, "📋", "Would update: requirements.txt")
        else:
            shutil.copy2(src_req, dest_req)
            log(GREEN, "✅", "Updated: requirements.txt")
        copied += 1

    if copied == 0:
        log(YELLOW, "⏭️", "No files to copy")
    else:
        log(GREEN, "✅", f"{'Would copy' if dry_run else 'Copied'} {copied} file(s)")

    return True


def stop_bot():
    if not PID_FILE.exists():
        log(YELLOW, "⏭️", "No bot.pid found, checking processes...")
        code, out, _ = run_cmd(["tasklist", "/FI", "IMAGENAME eq python.exe", "/FO", "CSV"])
        if code == 0 and "python.exe" in out.lower():
            log(YELLOW, "⚠️", "Python processes running but no PID file. Bot may need manual restart.")
        return False

    pid = int(PID_FILE.read_text().strip())
    log(CYAN, "🔄", f"Stopping bot (PID: {pid})...")
    try:
        os.kill(pid, signal.SIGTERM)
        log(GREEN, "✅", "Bot stopped")
        return True
    except ProcessLookupError:
        log(YELLOW, "⏭️", "Bot process not running (stale PID)")
        return False
    except PermissionError:
        log(RED, "❌", "Permission denied to stop bot")
        return False


def start_bot():
    log(CYAN, "🚀", "Starting bot...")
    bot_py = PROJECT_ROOT / "bot.py"
    if not bot_py.exists():
        log(RED, "❌", "bot.py not found")
        return False

    # Start bot in background and save PID
    if sys.platform == "win32":
        proc = subprocess.Popen(
            [sys.executable, str(bot_py)],
            cwd=str(PROJECT_ROOT),
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    else:
        proc = subprocess.Popen(
            [sys.executable, str(bot_py)],
            cwd=str(PROJECT_ROOT),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )

    PID_FILE.write_text(str(proc.pid))
    log(GREEN, "✅", f"Bot started (PID: {proc.pid})")
    return True


def main():
    parser = argparse.ArgumentParser(description="Cipher Labs Bot Updater")
    parser.add_argument("--install", metavar="DIR", help="Install features from a source directory")
    parser.add_argument("--dry-run", action="store_true", help="Show what would change without doing it")
    parser.add_argument("--no-restart", action="store_true", help="Skip bot restart")
    args = parser.parse_args()

    print(f"\n{CYAN}{'='*50}")
    print(f"  Cipher Labs Bot Updater")
    print(f"{'='*50}{RESET}\n")

    dry = args.dry_run

    # Step 1: Install features from source if provided
    if args.install:
        install_features(args.install, dry)
        print()

    # Step 2: Git pull
    git_ok = git_pull(dry)
    print()

    # Step 3: Install dependencies
    deps_ok = install_deps(dry)
    print()

    if dry:
        log(CYAN, "📋", "Dry run complete — no changes were made")
        return

    # Step 4: Restart bot
    if not args.no_restart:
        stop_bot()
        import time
        time.sleep(2)
        start_bot()
    else:
        log(GREEN, "✅", "Update complete. Bot not restarted (--no-restart)")

    print(f"\n{GREEN}{'='*50}")
    print(f"  Done!")
    print(f"{'='*50}{RESET}\n")


if __name__ == "__main__":
    main()
