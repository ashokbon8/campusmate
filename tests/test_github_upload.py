import json
import subprocess

import pytest

from scripts.upload_to_github import publish, release_paths


def git(*args, cwd=None):
    return subprocess.run(["git", *map(str, args)], cwd=cwd, check=True,
                          capture_output=True, text=True).stdout.strip()


def manifest(root, names):
    (root / "scripts").mkdir(exist_ok=True)
    (root / "scripts/release_files.json").write_text(json.dumps(names))


def test_upload_preserves_remote_history_and_excludes_private_runtime_data(tmp_path):
    remote = tmp_path / "remote.git"
    git("init", "--bare", "--initial-branch=main", remote)
    seed = tmp_path / "seed"
    git("clone", remote, seed)
    git("config", "user.name", "Test", cwd=seed)
    git("config", "user.email", "test@example.com", cwd=seed)
    (seed / "README.md").write_text("Initial repository")
    (seed / "existing.txt").write_text("Keep existing remote work")
    git("add", ".", cwd=seed)
    git("commit", "-m", "Initial commit", cwd=seed)
    git("push", "origin", "main", cwd=seed)
    initial = git("rev-parse", "HEAD", cwd=seed)
    source = tmp_path / "project"
    source.mkdir()
    (source / "README.md").write_text("Complete final project")
    (source / "app.py").write_text("print('CampusMate')")
    (source / ".env").write_text("PRIVATE=must-stay-local")
    (source / "campusmate.db").write_bytes(b"private database")
    manifest(source, ["README.md", "app.py"])
    commit = publish(source, str(remote))
    assert git("rev-parse", "refs/heads/main", cwd=remote) == commit
    assert git("rev-parse", commit + "^", cwd=remote) == initial
    names = git("ls-tree", "-r", "--name-only", "main", cwd=remote).splitlines()
    assert set(names) == {"README.md", "app.py", "existing.txt"}
    assert git("show", "main:README.md", cwd=remote) == "Complete final project"
    assert (source / ".env").read_text() == "PRIVATE=must-stay-local"
    assert not (source / ".git").exists()


@pytest.mark.parametrize("name", [".env", "backend/.env", "../private.txt", "campusmate.db", ".git/config", "node_modules/package.json"])
def test_release_list_rejects_private_and_unsafe_paths(tmp_path, name):
    manifest(tmp_path, [name])
    with pytest.raises(ValueError):
        release_paths(tmp_path)


def test_release_list_rejects_password_in_the_example_config(tmp_path):
    (tmp_path / ".env.example").write_text("SEED_ADMIN_PASSWORD=not-for-publishing")
    manifest(tmp_path, [".env.example"])
    with pytest.raises(ValueError, match="private passwords"):
        release_paths(tmp_path)
