from pathlib import Path
import pytest
from scripts.apply_exam_update import apply_update, find_project


def test_updater_keeps_login_database_and_backs_up_old_code(tmp_path):
    project = tmp_path/'campusmate'
    (project/'backend/app').mkdir(parents=True)
    (project/'frontend').mkdir()
    (project/'backend/app/main.py').write_text('original code')
    (project/'frontend/package.json').write_text('{}')
    (project/'backend/.env').write_text('PRIVATE_CONFIGURATION=retain')
    (project/'backend/campusmate.db').write_bytes(b'existing-data')
    payload = tmp_path/'payload'
    (payload/'backend/app').mkdir(parents=True)
    (payload/'backend/app/main.py').write_text('updated code')
    (payload/'backend/app/exams.py').write_text('new code')
    backup = apply_update(project,payload,['backend/app/main.py','backend/app/exams.py'])
    assert (project/'backend/app/main.py').read_text() == 'updated code'
    assert (backup/'backend/app/main.py').read_text() == 'original code'
    assert (project/'backend/.env').read_text() == 'PRIVATE_CONFIGURATION=retain'
    assert (project/'backend/campusmate.db').read_bytes() == b'existing-data'
    assert find_project(project/'some/nested/update') == project


def test_updater_refuses_private_config_changes(tmp_path):
    project = tmp_path/'campusmate'
    (project/'backend/app').mkdir(parents=True)
    (project/'frontend').mkdir()
    (project/'backend/app/main.py').write_text('original')
    (project/'frontend/package.json').write_text('{}')
    payload = tmp_path/'payload'
    (payload/'backend').mkdir(parents=True)
    for name in ['.env','.ENV']:
        (project/'backend'/name).write_text('private-original')
        (payload/'backend'/name).write_text('must-not-be-installed')
        with pytest.raises(ValueError,match='private'):
            apply_update(project,payload,['backend/'+name])
        assert (project/'backend'/name).read_text() == 'private-original'
