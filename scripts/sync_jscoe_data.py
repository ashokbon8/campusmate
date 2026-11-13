"""After reviewing the canonical JSON, copy it into the standalone frontend build."""
from pathlib import Path
import html
import json

root = Path(__file__).resolve().parents[1]
source = root / 'backend/app/data/jscoe_knowledge.json'
target = root / 'frontend/src/lib/jscoeKnowledge.json'
target.write_bytes(source.read_bytes())
print('Frontend JSCOE knowledge snapshot updated.')

exam_source = root / 'backend/app/data/exam_data.json'
if exam_source.exists():
    (root / 'frontend/src/lib/examData.json').write_bytes(exam_source.read_bytes())
    exam = json.loads(exam_source.read_text(encoding='utf-8'))
    rows = []
    for table in exam['demo_timetables']:
        for row in table['rows']:
            cells = [table['semester'],row['subject'],row['exam_date'],row.get('start_time') or 'Not given',row.get('venue') or 'Not given']
            rows.append('<tr>'+''.join('<td>'+html.escape(str(cell))+'</td>' for cell in cells)+'</tr>')
    content = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>CampusMate DEMO exam timetable — fictional dates</title><style>
body{background:#080a0b;color:white;font:16px/1.6 system-ui,sans-serif;max-width:1100px;margin:40px auto;padding:0 22px}
h1,strong,a{color:#c6ff00} .banner{border:2px solid #c6ff00;padding:20px;border-radius:14px}table{width:100%;border-collapse:collapse;font-size:14px}td,th{text-align:left;padding:12px;border-bottom:1px solid #333}th{color:#c6ff00}.table{overflow:auto}
</style><h1>DEMO EXAM TIMETABLE</h1><p class="banner"><strong>ALL dates, times and rooms below are fictional examples.</strong><br>Do not use these dates to attend an actual college examination.</p>
<p>Example programme: B.Tech · Academic year 2026–27. Your own dates can be entered in Admin Login → Exam timetable.</p>
<div class="table"><table><thead><tr><th>Semester</th><th>Subject</th><th>Example date</th><th>Example time</th><th>Example room</th></tr></thead><tbody>'''+''.join(rows)+'''</tbody></table></div>
<p>Subject names/codes are based on the college's <a href="'''+html.escape(exam['source_url'],quote=True)+'''">FY 2026 syllabus</a>. The example dates are invented by CampusMate and do not come from that syllabus. Shared subjects/group arrangements and assessment types must be checked with your college.</p></html>'''
    folder = root / 'frontend/public'
    folder.mkdir(exist_ok=True)
    (folder / 'demo-exam-timetable.html').write_text(content,encoding='utf-8')
    print('Exam aliases, explicit demo snapshot and demo source page updated.')
