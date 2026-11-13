"""Real college pack: correct facts, no sample leakage, and safe unknowns."""
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.config import settings
from app.database import Base, get_db
from app.main import create_app
from app.models import Document, Ticket
from app.services.college_data import knowledge_pack, seed_jscoe_data
from app.services.seed import seed_demo_data


@pytest.fixture
def college(monkeypatch):
    monkeypatch.setattr(settings, 'campusmate_dataset', 'jscoe')
    engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        seed_jscoe_data(db)
    app = create_app()
    def session():
        with Session(engine) as db:
            yield db
    app.dependency_overrides[get_db] = session
    # No lifespan here: the isolated database was seeded above.
    client = TestClient(app)
    yield client, engine
    client.close()
    engine.dispose()


def ask(college, question, context=None):
    response = college[0].post('/chat', json={'question': question, 'context': context or {}})
    assert response.status_code == 200, response.text
    return response.json()


@pytest.mark.parametrize('question,doc_id,fragment', [
    ('Which documents are required for admission?', 'jscoe-admission-checklist', 'Two colour photographs'),
    ('How do I apply for engineering admission?', 'jscoe-admission-process', 'document verification'),
    ('What are the B.Tech fees for 2026-27?', 'jscoe-fees-engineering', '1,20,000'),
    ('How much is MCA tuition?', 'jscoe-fees-mca', '74,783'),
    ('What are MBA OBC male fees?', 'jscoe-fees-mba', '50,304'),
    ('Show the first year academic calendar', 'jscoe-calendar', '21 September 2026'),
    ('When is CCE 4 submission?', 'jscoe-calendar-cce4', '20 November 2026'),
    ('When is CCE 5 submission?', 'jscoe-calendar-cce5', '04 December 2026'),
    ('When are first year end semester exams?', 'jscoe-calendar-endsem', '07 January 2027'),
    ('When are retest results declared?', 'jscoe-calendar-retest-result', '30 January 2027'),
    ('When does semester 2 start?', 'jscoe-calendar-next-semester', '01 February 2027'),
    ('Where can I find examination notices?', 'jscoe-exam-notices', 'historical'),
])
def test_sourced_answers(college, question, doc_id, fragment):
    body = ask(college, question)
    assert body['state'] == 'answered', body
    assert fragment.lower() in body['answer'].lower()
    citation = body['citations'][0]
    assert citation['document_id'] == doc_id
    assert citation['open_url'].startswith('https://jspmjscoe.edu.in/')
    assert citation['checked_on'] == '2026-11-13'
    assert not body['is_sample_data']


def test_full_checklist_is_retained_and_formatted(college):
    answer = ask(college, 'Which documents do I need?')['answer']
    for phrase in ['CET/JEE', 'Class 10 passing', 'Leaving certificate', 'MKB', 'gap certificate']:
        assert phrase.lower() in answer.lower()
    assert answer.count('\n') >= 4


@pytest.mark.parametrize('question,context', [
    ('What are the B.Tech fees for 2027-28?', {}),
    ('What is the fee structure?', {'academic_year': '2025-26'}),
    ('What is the B.Tech hostel fee?', {}),
    ('Can I pay MBA fees in instalments?', {}),
    ('Where is the next B.Tech class?', {'semester': '1'}),
    ('What is the college canteen menu?', {}),
])
def test_unverified_details_are_not_answered(college, question, context):
    body = ask(college, question, context)
    assert body['state'] == 'escalated', body
    assert body['ticket_suggested']


def test_fee_clarification_continues_with_programme(college):
    assert ask(college, 'What are the fees?')['state'] == 'needs_context'
    body = ask(college, 'What are the fees? B.Tech', {'programme': 'B.Tech'})
    assert body['state'] == 'answered'
    assert body['citations'][0]['document_id'] == 'jscoe-fees-engineering'


def test_sources_keep_their_actual_formats(college):
    client = college[0]
    notices = {doc['doc_uid']: doc for doc in client.get('/documents').json()}
    assert notices['jscoe-admission-checklist']['source_format'] == 'html'
    assert notices['jscoe-fees-engineering']['source_format'] == 'pdf'
    assert notices['jscoe-calendar']['source_format'] == 'image'
    assert notices['jscoe-exam-notices']['source_status'] == 'historical'
    response = client.get('/documents/jscoe-calendar/source', follow_redirects=False)
    assert response.status_code == 307
    assert response.headers['location'].endswith('.jpg')


def test_import_is_safe_on_an_existing_demo_database(college):
    with Session(college[1]) as db:
        seed_demo_data(db)
        ticket = Ticket(reference='CM-KEEP', category='Admissions', description='Keep this existing ticket')
        db.add(ticket)
        custom = Document(doc_uid='staff-keep', title='Staff-uploaded FAQ', category='Admissions',
            doc_type='faq', status='draft', version=1)
        db.add(custom)
        db.commit()
        seed_jscoe_data(db)
        assert db.scalar(select(Ticket).where(Ticket.reference == 'CM-KEEP'))
        assert db.scalar(select(Document).where(Document.doc_uid == 'staff-keep')).status == 'draft'
        assert not any(d.is_sample_data for d in db.scalars(select(Document).where(Document.status == 'published')))
        target = db.scalar(select(Document).where(Document.doc_uid == 'jscoe-calendar'))
        target.status = 'retired'
        db.commit()
        count = len(list(db.scalars(select(Document))))
        seed_jscoe_data(db)
        assert target.status == 'retired'
        assert len(list(db.scalars(select(Document)))) == count


def test_frontend_and_backend_use_the_same_reviewed_snapshot():
    path = Path(__file__).resolve().parents[1] / 'frontend/src/lib/jscoeKnowledge.json'
    assert json.loads(path.read_text()) == knowledge_pack()


@pytest.fixture
def college_admin(college):
    from app.models import Admin
    from app.security import create_access_token
    with Session(college[1]) as db:
        admin = db.scalar(select(Admin))
        return {'Authorization':'Bearer '+create_access_token(admin.email,admin.role)}


@pytest.mark.parametrize('subject',['math','maths1','M1','physics','chemistry','mechanics','graphics','BEEE','C programming','FMPP','DTI','PCS'])
def test_subject_queries_give_scoped_calendar_help_without_ticket(college,subject):
    body = ask(college,f'when was my sem 1 {subject} exam')
    assert body['state'] == 'needs_context', body
    assert not body['ticket_suggested']
    assert '23 December 2026' in body['answer']
    assert 'exact' in body['answer'].lower() and 'not specified' in body['answer'].lower()
    assert body['citations'][0]['document_id'] == 'jscoe-calendar-endsem'


def test_complete_context_does_not_turn_window_into_a_subject_date(college):
    body = ask(college,'When is the Mathematics exam?',{'programme':'B.Tech','semester':'1','academic_year':'2026-27','subject':'Maths'})
    assert body['state'] == 'answered'
    assert body['data_origin'] == 'college'
    assert not body['ticket_suggested']
    assert 'not specified' in body['answer']


def test_demo_rows_are_available_for_all_catalogued_subjects_and_never_leak(college):
    from app.services.exam_rules import exam_data
    for table in exam_data()['demo_timetables']:
        for row in table['rows']:
            body = ask(college,f"When is my sem{table['semester']} {row['subject']} exam?",{'programme':'B.Tech','academic_year':'2026-27','exam_data_mode':'demo'})
            assert body['state'] == 'answered', (row,body)
            assert 'DEMO' in body['answer'] and body['is_sample_data']
            assert body['data_origin'] == 'demo'
            assert body['citations'][0]['source_status'] == 'demo'
    body = ask(college,'When is my sem 1 maths exam?',{'programme':'B.Tech','academic_year':'2026-27'})
    assert body['data_origin'] == 'college'
    assert 'Example Room' not in body['answer']
    assert not body['is_sample_data']


def timetable_payload():
    return {'programme':'B.Tech','semester':'1','academic_year':'2026-27','exam_kind':'end_sem','rows':[
        {'subject':'Maths','exam_date':'2026-12-27','start_time':'09:30','venue':'Room 204','aliases':['M1']},
        {'subject':'Physics','exam_date':'2027-01-03','aliases':['EP']},
        {'subject':'Chemistry','exam_date':'2027-01-05','aliases':['EC']},
    ]}


def test_admin_dates_answer_every_subject_and_replace_old_dates(college,college_admin):
    client = college[0]
    payload = timetable_payload()
    response = client.post('/admin/exam-timetables',json=payload,headers=college_admin)
    assert response.status_code == 201, response.text
    old = response.json()
    for subject,expected in [('math','27 December 2026'),('EP','3 January 2027'),('chem','5 January 2027')]:
        body = ask(college,f'when was my sem1 {subject} exam',{'programme':'B.Tech','academic_year':'2026-27'})
        assert body['state'] == 'answered', body
        assert expected in body['answer'] and body['data_origin'] == 'admin'
        assert body['citations'][0]['source_status'] == 'custom'
        assert not body['ticket_suggested']
    body = ask(college,'Show all sem1 exam dates',{'programme':'B.Tech','academic_year':'2026-27','subject':'Maths'})
    assert all(name in body['answer'] for name in ['Mathematics','Physics','Chemistry'])
    source = client.get('/documents/'+old['doc_uid']+'/source')
    assert source.status_code == 200 and source.content.startswith(b'%PDF')
    payload['rows'][0]['exam_date'] = '2027-01-07'
    new = client.post('/admin/exam-timetables',json=payload,headers=college_admin)
    assert new.status_code == 201 and new.json()['version'] == 2
    body = ask(college,'When is my sem1 maths exam?',{'programme':'B.Tech','academic_year':'2026-27'})
    assert '7 January 2027' in body['answer'] and '27 December 2026' not in body['answer']
    assert client.get('/documents/'+old['doc_uid']).json()['status'] == 'replaced'


def test_exam_editor_rejects_unauthorised_writes_and_duplicate_subjects(college,college_admin):
    client = college[0]
    assert client.post('/admin/exam-timetables',json=timetable_payload()).status_code == 401
    payload = timetable_payload()
    payload['rows'].append({'subject':'M1','exam_date':'2026-12-28'})
    response = client.post('/admin/exam-timetables',json=payload,headers=college_admin)
    assert response.status_code == 400
    assert client.get('/admin/exam-timetables',headers=college_admin).json() == []


def test_division_and_year_are_not_silently_guessed(college,college_admin):
    client = college[0]
    for division,day in [('A','2026-12-27'),('B','2027-01-04')]:
        payload = timetable_payload()
        payload['division'] = division
        payload['rows'][0]['exam_date'] = day
        assert client.post('/admin/exam-timetables',json=payload,headers=college_admin).status_code == 201
    body = ask(college,'When is my sem1 maths exam?',{'programme':'B.Tech','academic_year':'2026-27'})
    assert body['state'] == 'needs_context' and 'division' in body['clarification_question']
    body = ask(college,'When is my sem1 maths exam for division B?',{'programme':'B.Tech','academic_year':'2026-27'})
    assert '4 January 2027' in body['answer']
    body = ask(college,'When is my sem1 maths exam?',{'programme':'B.Tech','academic_year':'2025-26','division':'B'})
    assert '4 January 2027' not in body['answer']


def test_existing_staff_faq_dates_match_maths_alias(college,college_admin):
    client = college[0]
    response = client.post('/admin/notices',headers=college_admin,data={
        'title':'Uploaded mathematics examination date','category':'Examinations','doc_type':'faq',
        'programme':'B.Tech','semester':'1','academic_year':'2026-27','subject':'Maths',
        'body':'The Mathematics examination is on 29 December 2026 at 09:00 AM in Room 301.'})
    assert response.status_code == 201, response.text
    assert client.post('/admin/notices/'+str(response.json()['id'])+'/publish',headers=college_admin).status_code == 200
    body = ask(college,'When was my sem1 math exam?',{'programme':'B.Tech','academic_year':'2026-27'})
    assert body['state'] == 'answered' and '29 December 2026' in body['answer']


def test_exam_data_and_static_demo_source_are_synced():
    from app.services.exam_rules import exam_data
    root = Path(__file__).resolve().parents[1]
    assert json.loads((root/'frontend/src/lib/examData.json').read_text()) == exam_data()
    page = (root/'frontend/public/demo-exam-timetable.html').read_text()
    assert 'fictional examples' in page and 'Do not use these dates' in page


def test_any_admin_subject_and_later_semester_can_be_answered(college,college_admin):
    payload = {'programme':'B.Tech','semester':'3','academic_year':'2026-27','rows':[
        {'subject':'Operating Systems','exam_date':'2027-01-20','aliases':['OS']},
        {'subject':'Data Structures and Algorithms','exam_date':'2027-01-21','aliases':['DSA']},
        {'subject':'Engineering Mathematics III','exam_date':'2027-01-22'},
    ]}
    response = college[0].post('/admin/exam-timetables',json=payload,headers=college_admin)
    assert response.status_code == 201, response.text
    for subject,day in [('OS','20 January 2027'),('DSA','21 January 2027'),('math III','22 January 2027')]:
        body = ask(college,f'When is my sem3 {subject} exam?',{'programme':'B.Tech','academic_year':'2026-27'})
        assert body['state'] == 'answered' and day in body['answer'], body
        assert body['data_origin'] == 'admin' and not body['ticket_suggested']


def test_calendar_help_does_not_use_an_inactive_knowledge_version(college):
    from app.models import KnowledgeVersion
    with Session(college[1]) as db:
        for version in db.scalars(select(KnowledgeVersion)):
            version.is_active = False
        db.add(KnowledgeVersion(label='kv-empty-check',is_active=True))
        db.commit()
    body = ask(college,'When is my sem1 maths exam?',{'programme':'B.Tech','academic_year':'2026-27'})
    assert body['citations'] == []
    assert '23 December 2026' not in body['answer']
