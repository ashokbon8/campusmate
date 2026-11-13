"""Upload the release with the user's local Git sign-in, excluding private files."""
from pathlib import Path, PurePosixPath
import json
import shutil
import subprocess
import tempfile

REPOSITORY = "https://github.com/ashokbon8/campusmate.git"
WEBSITE = "https://github.com/ashokbon8/campusmate"


def release_paths(root: Path) -> list[str]:
    paths = json.loads((root / "scripts/release_files.json").read_text(encoding="utf-8"))
    if not isinstance(paths, list) or not paths:
        raise ValueError("The release file list is missing. Extract the complete ZIP again.")
    result = []
    forbidden = {".git", ".venv", "node_modules", "__pycache__", ".pytest_cache", "storage"}
    for name in paths:
        if not isinstance(name, str) or not name or "\\" in name or ":" in name:
            raise ValueError("The release file list contains an invalid path.")
        path = PurePosixPath(name)
        private_env = path.name == ".env" or (path.name.startswith(".env.") and path.name != ".env.example")
        if path.is_absolute() or ".." in path.parts or any(p in forbidden for p in path.parts) or private_env:
            raise ValueError("Private files cannot be included in a release.")
        if path.suffix.lower() in {".db", ".sqlite", ".sqlite3", ".zip", ".log"}:
            raise ValueError("Local databases and archives cannot be included in a release.")
        source = root / name
        if source.is_symlink() or not source.is_file() or not source.resolve().is_relative_to(root.resolve()):
            raise ValueError(f"Release file missing or unsafe: {name}")
        if path.name == ".env.example":
            for line in source.read_text(encoding="utf-8").splitlines():
                if line.startswith(("SEED_ADMIN_PASSWORD=", "LLM_API_KEY=", "EMBEDDING_API_KEY=")):
                    if line.split("=", 1)[1].strip().strip("\"'"):
                        raise ValueError("Remove private passwords/API keys from .env.example before uploading.")
        result.append(name)
    if len(set(result)) != len(result):
        raise ValueError("The release file list contains duplicate paths.")
    return result


def git(*args, cwd=None, capture=False):
    return subprocess.run(["git", *map(str, args)], cwd=cwd, check=True,
                          text=True, stdout=subprocess.PIPE if capture else None)


def publish(root: Path, remote: str = REPOSITORY) -> str:
    paths = release_paths(root)
    if shutil.which("git") is None:
        raise ValueError("Git is required. Install Git for Windows from https://git-scm.com/downloads/win, then reopen VS Code.")
    with tempfile.TemporaryDirectory(prefix="campusmate-github-", ignore_cleanup_errors=True) as temporary:
        checkout = Path(temporary) / "release"
        git("clone", "--single-branch", "--branch", "main", "--", remote, checkout)
        git("config", "user.name", "ashokbon8", cwd=checkout)
        git("config", "user.email", "309409354+ashokbon8@users.noreply.github.com", cwd=checkout)
        for name in paths:
            destination = checkout / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(root / name, destination)
        git("add", "--", *paths, cwd=checkout)
        diff = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=checkout)
        if diff.returncode == 1:
            git("commit", "-m", "Publish complete CampusMate hackathon project", cwd=checkout)
        elif diff.returncode != 0:
            raise RuntimeError("Git could not check the release changes.")
        git("push", "origin", "HEAD:main", cwd=checkout)
        local = git("rev-parse", "HEAD", cwd=checkout, capture=True).stdout.strip()
        heads = git("ls-remote", "origin", "refs/heads/main", cwd=checkout, capture=True).stdout.split()
        if not heads or heads[0] != local:
            raise RuntimeError("The remote branch changed before upload could be verified. Inspect the repository's latest commit.")
        return local


def main() -> int:
    print("CampusMate - upload the complete project to GitHub")
    print(WEBSITE)
    print("Git may open your browser to sign in. Choose your ashokbon8 account.")
    print("Private .env, databases, uploads and installed packages are excluded.")
    try:
        sha = publish(Path(__file__).resolve().parents[1])
    except (ValueError, RuntimeError, OSError, subprocess.CalledProcessError) as error:
        print(f"Upload stopped: {error}")
        print("Your local project is unchanged. Correct the Git error above, then run again.")
        return 1
    print("Upload verified: " + WEBSITE)
    print("Commit: " + sha)
    print("Send the repository link back to continue the Render deployment.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
