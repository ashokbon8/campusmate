from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from scripts import first_run


@pytest.fixture
def private_config(tmp_path,monkeypatch):
    monkeypatch.delenv('SEED_ADMIN_EMAIL',raising=False)
    monkeypatch.delenv('SEED_ADMIN_PASSWORD',raising=False)
    path=tmp_path/'.env'
    return path


def test_final_run_keeps_an_existing_admin(private_config,monkeypatch):
    private_config.write_text('SEED_ADMIN_EMAIL=local@example.com\nSEED_ADMIN_PASSWORD=existing-private-password\n')
    original=private_config.read_bytes()
    def unexpected(*args,**kwargs):
        raise AssertionError('Existing admin setup must not run again.')
    monkeypatch.setattr(first_run,'setup_admin',unexpected)
    assert first_run.main([],env_file=private_config)==0
    assert private_config.read_bytes()==original


def test_final_run_integrates_visible_first_time_setup(private_config,monkeypatch):
    calls=[]
    monkeypatch.setattr(first_run,'setup_admin',lambda args,**kwargs:calls.append((args,kwargs['env_file'])) or 0)
    assert first_run.main([],env_file=private_config)==0
    assert calls==[(['--show-password'],private_config)]


def test_reset_admin_is_explicit(private_config,monkeypatch):
    private_config.write_text('SEED_ADMIN_EMAIL=local@example.com\nSEED_ADMIN_PASSWORD=existing-private-password\n')
    calls=[]
    monkeypatch.setattr(first_run,'setup_admin',lambda args,**kwargs:calls.append(args) or 0)
    assert first_run.main(['--reset-admin'],env_file=private_config)==0
    assert calls==[['--show-password']]


def test_built_website_and_api_work_on_one_origin(tmp_path):
    from app.local import create_local_app
    (tmp_path/'index.html').write_text('<h1>CampusMate final website</h1>')
    (tmp_path/'demo-exam-timetable.html').write_text('DEMO fictional dates')
    with TestClient(create_local_app(tmp_path)) as client:
        assert 'CampusMate final website' in client.get('/').text
        assert client.get('/api/health').json()['status']=='ok'
        assert len(client.get('/api/meta/categories').json()['categories'])==5
        response=client.post('/api/chat',json={'question':'When is my exam?'})
        assert response.status_code==200
        assert response.json()['state']=='needs_context'
        assert 'DEMO fictional' in client.get('/demo-exam-timetable.html').text


def test_missing_built_website_has_a_clear_error(tmp_path):
    from app.local import create_local_app
    with pytest.raises(RuntimeError,match='built website is missing'):
        create_local_app(tmp_path)
