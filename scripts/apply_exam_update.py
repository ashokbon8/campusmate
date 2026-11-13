"""Apply the exam update to an existing CampusMate folder, preserving user data."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import sys
import tempfile


def is_project(folder: Path) -> bool:
    return (folder/'backend/app/main.py').is_file() and (folder/'frontend/package.json').is_file()


def find_project(*starts: Path) -> Path | None:
    for start in starts:
        for folder in [start.resolve(),*start.resolve().parents]:
            if is_project(folder):
                return folder
    return None


def apply_update(project: Path, payload: Path, filenames: list[str]) -> Path:
    project, payload = project.resolve(), payload.resolve()
    if not is_project(project):
        raise ValueError('Select the existing campusmate folder that contains backend and frontend.')
    pairs = []
    for name in filenames:
        relative = Path(name)
        if relative.is_absolute() or '..' in relative.parts or any(
            part.lower() in {'.git','.venv','node_modules','storage'} or part.lower().startswith('.env') for part in relative.parts
        ) or relative.suffix.lower() in {'.db','.sqlite','.sqlite3'}:
            raise ValueError('This update may contain only project code, not private settings or user data.')
        source, target = (payload/relative).resolve(), (project/relative).resolve()
        if not source.is_relative_to(payload) or not target.is_relative_to(project) or not source.is_file():
            raise ValueError('An update file is missing or outside the update folder.')
        pairs.append((relative,source,target))
    backup = Path(tempfile.mkdtemp(prefix='exam-update-backup-',dir=project))
    for relative,_,target in pairs:
        if target.exists():
            saved = backup/relative
            saved.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(target,saved)
    changed = []
    try:
        for relative,source,target in pairs:
            target.parent.mkdir(parents=True,exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=target.parent,delete=False) as stream:
                temporary = Path(stream.name)
            try:
                shutil.copy2(source,temporary)
                os.replace(temporary,target)
            finally:
                temporary.unlink(missing_ok=True)
            changed.append((relative,target))
    except OSError:
        for relative,target in reversed(changed):
            original = backup/relative
            if original.exists(): shutil.copy2(original,target)
            else: target.unlink(missing_ok=True)
        raise
    return backup


def main() -> int:
    bundle = Path(__file__).resolve().parent
    manifest = bundle/'update-files.json'
    if not manifest.is_file():
        print('Extract the complete exam update ZIP and keep its files together.')
        return 1
    try:
        project = find_project(bundle,Path.cwd())
        while project is None:
            value = input('Paste the path to your existing campusmate folder: ').strip().strip('"')
            chosen = Path(os.path.expandvars(value)).expanduser()
            if is_project(chosen): project = chosen
            else: print('That folder must contain both backend and frontend. Please try again.')
        print('Updating:',project)
        backup = apply_update(project,bundle/'update',json.loads(manifest.read_text(encoding='utf-8')))
        print('Exam update installed. Login settings, database and uploaded files were retained.')
        print('Previous code backup:',backup)
        print('Start/restart CampusMate with START_CAMPUSMATE.cmd, then refresh the website.')
        return 0
    except (EOFError,KeyboardInterrupt):
        print('\nUpdate cancelled.')
        return 1
    except (OSError,ValueError) as error:
        print('The update could not be completed:',error)
        return 1


if __name__=='__main__':
    raise SystemExit(main())
