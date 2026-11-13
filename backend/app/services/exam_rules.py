"""Subject aliases and everyday semester wording, independent of the database."""
import json
import re
from functools import lru_cache
from pathlib import Path


@lru_cache
def exam_data() -> dict:
    return json.loads((Path(__file__).resolve().parents[1] / 'data/exam_data.json').read_text(encoding='utf-8'))


def words(value: str) -> str:
    value = value.lower().replace('c++', 'cplusplus').replace('&', ' and ')
    roman = {'i':'1','ii':'2','iii':'3','iv':'4','v':'5','vi':'6','vii':'7','viii':'8'}
    value = re.sub(r'\bmath(?:s|ematics)?\s*[- ]?\s*(viii|vii|vi|iv|iii|ii|v|i|[1-8])\b',
                   lambda match:'mathematics '+roman.get(match[1],match[1]),value)
    return ' '.join(re.findall(r'[a-z0-9]+', value))


def semester_number(value: str | None) -> str | None:
    if not value:
        return None
    value = value.lower().strip()
    names = {'first':'1','second':'2','third':'3','fourth':'4','fifth':'5','sixth':'6','seventh':'7','eighth':'8',
             'i':'1','ii':'2','iii':'3','iv':'4','v':'5','vi':'6','vii':'7','viii':'8'}
    if value in names:
        return names[value]
    match = re.fullmatch(r'([1-8])(?:st|nd|rd|th)?', value)
    return match[1] if match else None


def canonical_subject(value: str | None, semester: str | None = None) -> str | None:
    if not value or not value.strip():
        return None
    key = words(value)
    indexed_math = re.fullmatch(r'(?:engineering )?mathematics ([1-8])',key)
    if indexed_math:
        return 'Engineering Mathematics '+['I','II','III','IV','V','VI','VII','VIII'][int(indexed_math[1])-1]
    if key in {'math','maths','mathematics','engineering mathematics','engineering maths'}:
        return 'Engineering Mathematics II' if semester == '2' else 'Engineering Mathematics I'
    if semester == '2' and key in {'beee','bee','basic electrical','basic electronics','electrical','electronics'}:
        return 'Basic Electrical and Electronics Engineering II'
    if semester == '2' and key in {'exploration lab','eee lab','electrical lab','electronics lab'}:
        return 'Electrical and Electronics Exploration Lab II'
    for course in exam_data()['courses']:
        if key in {words(x) for x in [course['name'], course['code'], *course['aliases']]}:
            return course['name']
    return value.strip()


def mentioned_subjects(question: str, semester: str | None = None) -> list[str]:
    q = words(question)
    found = []
    for match in re.finditer(r'\b(?:engineering )?mathematics ([1-8])\b',q):
        found.append((match.start(),match.end(),match[0],canonical_subject(match[0],semester)))
    for course in exam_data()['courses']:
        for alias in [course['name'], course['code'], *course['aliases']]:
            for match in re.finditer(r'\b' + re.escape(words(alias)) + r'\b', q):
                found.append((match.start(), match.end(), alias, course['name']))
    # Longest phrases win over overlapping short aliases (e.g. electronics lab).
    chosen = []
    for start, end, alias, name in sorted(found, key=lambda item: item[1]-item[0], reverse=True):
        if not any(start < b and end > a for a,b,_ in chosen):
            chosen.append((start,end,canonical_subject(alias,semester) or name))
    return list(dict.fromkeys(name for _,_,name in sorted(chosen)))


def enrich_exam_context(question: str, context: dict) -> dict:
    result = dict(context)
    result['semester'] = semester_number(context.get('semester')) or context.get('semester')
    q = question.lower()
    value = r'(first|second|third|fourth|fifth|sixth|seventh|eighth|viii|vii|vi|iv|iii|ii|v|i|[1-8](?:st|nd|rd|th)?)'
    match = re.search(r'\bsem(?:ester)?\s*[-.:]?\s*'+value+r'\b',q)
    if not match:
        match = re.search(r'\b'+value+r'\s*[- ]?\s*(?:semester|sem)\b',q)
    if match:
        result['semester'] = semester_number(match[1])
    division = re.search(r'\b(?:division|div|group)\s*[-:]?\s*([a-z0-9]{1,8})\b',q)
    if division:
        result['division'] = division[1].upper()
    subjects = mentioned_subjects(question,result.get('semester'))
    if subjects:
        result['requested_subjects'] = subjects
        result['subject'] = subjects[0] if len(subjects) == 1 else None
    elif (is_exam_date_question(question) and re.search(r'\ball\b',q)) or re.search(r'\bfull (?:exam )?timetable\b',q):
        result['subject'] = None
        result['requested_subjects'] = []
    else:
        # A newly named, uncatalogued subject must replace stale chat context.
        fragment = re.sub(r'\bsem(?:ester)?\s*[-.:]?\s*'+value+r'\b',' ',q)
        fragment = re.sub(r'\b'+value+r'\s*[- ]?\s*(?:semester|sem)\b',' ',fragment)
        stop = set('when what where how much many until days is was were are will be can i my the for at on of a an exam exams examination examinations paper papers date dates time timetable timing schedule semester sem end endsem endsemester first second third fourth year academic b tech btech be mba mca all subject subjects please tell me in and practical viva room hall venue start starts'.split())
        unknown = [token for token in words(fragment).split() if token not in stop and not token.isdigit()]
        if is_exam_date_question(question) and unknown:
            result['subject'] = ' '.join(unknown)
        else:
            result['subject'] = canonical_subject(context.get('subject'),result.get('semester'))
        result['requested_subjects'] = [result['subject']] if result.get('subject') else []
    return result


def is_exam_date_question(question: str) -> bool:
    q = question.lower()
    if re.search(r'\b(fees?|admissions?|results?|forms?|registrations?|hall ticket|eligibility|marks?|syllabus|questions?|notes|weightage)\b',q):
        return False
    return bool(re.search(r'\b(exam(?:s|ination|inations)?|paper|end.sem|ese|retest|practical|viva)\b',q)
                and re.search(r'\b(when|date|day|time|timing|schedule|timetable|time table|all|start|kab|show|give)\b',q))


def exam_kind(question: str) -> str:
    q = question.lower()
    if re.search(r'\bretest|backlog|re.exam\b',q): return 'retest'
    if re.search(r'\bpractical|viva|termwork\b',q): return 'practical'
    if re.search(r'\bmid.sem|in.sem|internal|unit test\b',q): return 'in_sem'
    return 'end_sem'


def subject_matches(subject: str, requested: str | None, query: str = '', aliases: list[str] | None = None) -> bool:
    options = [subject, *(aliases or [])]
    if requested:
        target = words(canonical_subject(requested) or requested)
        if any(words(canonical_subject(option) or option) == target for option in options):
            return True
    q = words(query)
    return any(re.search(r'\b'+re.escape(words(option))+r'\b',q) for option in options if words(option))
