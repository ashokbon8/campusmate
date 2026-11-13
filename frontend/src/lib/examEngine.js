/** Exam wording and explicitly labelled sample schedules; no guessed college dates. */
import data from './examData.json' with {type:'json'};
export const EXAM_SUBJECTS = data.courses;
export const DEMO_TIMETABLES = data.demo_timetables;
const romanNumbers={i:'1',ii:'2',iii:'3',iv:'4',v:'5',vi:'6',vii:'7',viii:'8'};
const words = value => (value || '').toLowerCase().replaceAll('c++','cplusplus').replaceAll('&',' and ')
  .replace(/\bmath(?:s|ematics)?\s*[- ]?\s*(viii|vii|vi|iv|iii|ii|v|i|[1-8])\b/g,(_,number)=>`mathematics ${romanNumbers[number]||number}`)
  .match(/[a-z0-9]+/g)?.join(' ') || '';
const escape = value => value.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
const includesPhrase = (text,phrase) => phrase && new RegExp(`\\b${escape(words(phrase))}\\b`).test(words(text));
const semesterNames = {first:'1',second:'2',third:'3',fourth:'4',fifth:'5',sixth:'6',seventh:'7',eighth:'8',i:'1',ii:'2',iii:'3',iv:'4',v:'5',vi:'6',vii:'7',viii:'8'};
function semesterNumber(value) {
  if (!value) return null;
  const key=String(value).toLowerCase().trim();
  return semesterNames[key] || key.match(/^([1-8])(?:st|nd|rd|th)?$/)?.[1] || null;
}
export function canonicalSubject(value,semester) {
  if (!value?.trim()) return null;
  const key=words(value);
  const indexedMath=key.match(/^(?:engineering )?mathematics ([1-8])$/);
  if (indexedMath) return `Engineering Mathematics ${['I','II','III','IV','V','VI','VII','VIII'][Number(indexedMath[1])-1]}`;
  if (['math','maths','mathematics','engineering mathematics','engineering maths'].includes(key)) return `Engineering Mathematics ${semester==='2'?'II':'I'}`;
  if (semester==='2' && ['beee','bee','basic electrical','basic electronics','electrical','electronics'].includes(key)) return 'Basic Electrical and Electronics Engineering II';
  if (semester==='2' && ['exploration lab','eee lab','electrical lab','electronics lab'].includes(key)) return 'Electrical and Electronics Exploration Lab II';
  const course=data.courses.find(course=>[course.name,course.code,...course.aliases].some(alias=>words(alias)===key));
  return course?.name || value.trim();
}
function mentionedSubjects(question,semester) {
  const q=words(question), matches=[];
  for (const hit of q.matchAll(/\b(?:engineering )?mathematics ([1-8])\b/g)) matches.push({start:hit.index,end:hit.index+hit[0].length,name:canonicalSubject(hit[0],semester)});
  for (const course of data.courses) for (const alias of [course.name,course.code,...course.aliases]) {
    const pattern=new RegExp(`\\b${escape(words(alias))}\\b`,'g');
    for (const hit of q.matchAll(pattern)) matches.push({start:hit.index,end:hit.index+hit[0].length,name:canonicalSubject(alias,semester)});
  }
  const selected=[];
  for (const item of matches.sort((a,b)=>(b.end-b.start)-(a.end-a.start))) {
    if (!selected.some(other=>item.start<other.end && item.end>other.start)) selected.push(item);
  }
  return [...new Set(selected.sort((a,b)=>a.start-b.start).map(item=>item.name))];
}
export function isExamDateQuestion(question) {
  if (/\b(fees?|admissions?|results?|forms?|registrations?|hall ticket|eligibility|marks?|syllabus|questions?|notes|weightage)\b/i.test(question)) return false;
  return /\b(exam(?:s|ination|inations)?|paper|end.sem|ese|retest|practical|viva)\b/i.test(question)
    && /\b(when|date|day|time|timing|schedule|timetable|time table|all|start|kab|show|give)\b/i.test(question);
}
export function enrichExamContext(question,context={}) {
  const result={...context,semester:semesterNumber(context.semester)||context.semester};
  const q=question.toLowerCase();
  const value='(first|second|third|fourth|fifth|sixth|seventh|eighth|viii|vii|vi|iv|iii|ii|v|i|[1-8](?:st|nd|rd|th)?)';
  const suffix=new RegExp(`\\bsem(?:ester)?\\s*[-.:]?\\s*${value}\\b`);
  const prefix=new RegExp(`\\b${value}\\s*[- ]?\\s*(?:semester|sem)\\b`);
  const sem=q.match(suffix)||q.match(prefix);
  if (sem) result.semester=semesterNumber(sem[1]);
  const division=q.match(/\b(?:division|div|group)\s*[-:]?\s*([a-z0-9]{1,8})\b/);
  if (division) result.division=division[1].toUpperCase();
  const subjects=mentionedSubjects(question,result.semester);
  if (subjects.length) {
    result.requested_subjects=subjects;
    result.subject=subjects.length===1?subjects[0]:null;
  } else if ((isExamDateQuestion(question)&&/\ball\b/.test(q))||/\bfull (?:exam )?timetable\b/.test(q)) {
    result.subject=null; result.requested_subjects=[];
  } else {
    const stop=new Set('when what where how much many until days is was were are will be can i my the for at on of a an exam exams examination examinations paper papers date dates time timetable timing schedule semester sem end endsem endsemester first second third fourth year academic b tech btech be mba mca all subject subjects please tell me in and practical viva room hall venue start starts'.split(' '));
    const fragment=q.replace(suffix,' ').replace(prefix,' ');
    const unknown=words(fragment).split(' ').filter(word=>word && !stop.has(word) && !/^\d+$/.test(word));
    result.subject=isExamDateQuestion(question)&&unknown.length?unknown.join(' '):canonicalSubject(context.subject,result.semester);
    result.requested_subjects=result.subject?[result.subject]:[];
  }
  return result;
}
export function prettyExamDate(value) {
  const [year,month,day]=value.split('-');
  const months=['January','February','March','April','May','June','July','August','September','October','November','December'];
  return `${Number(day)} ${months[Number(month)-1]} ${year}`;
}
function formatRow(row) {
  let text=`${row.subject}: ${prettyExamDate(row.exam_date)}`;
  if (row.start_time) {const [hour,minute]=row.start_time.split(':').map(Number);text+=` at ${hour%12||12}:${String(minute).padStart(2,'0')} ${hour<12?'AM':'PM'}`;}
  if (row.venue) text+=` — ${row.venue}`;
  return text;
}
function kindFor(question) {
  if (/\bretest|backlog|re.exam\b/i.test(question)) return 'retest';
  if (/\bpractical|viva|termwork\b/i.test(question)) return 'practical';
  if (/\bmid.sem|in.sem|internal|unit test\b/i.test(question)) return 'in_sem';
  return 'end_sem';
}
export function offlineExamAnswer(question,context,notices,makeCitation) {
  if (!isExamDateQuestion(question)) return null;
  const ctx=enrichExamContext(question,context), demo=ctx.exam_data_mode==='demo', kind=kindFor(question);
  const base={category:'Examinations',knowledge_version:`jscoe-${data.checked_on}-offline`,is_sample_data:demo,
    ticket_suggested:false,data_origin:demo?'demo':'college',citations:[],clarification_question:null};
  const scopeMatches=table=>['programme','semester','academic_year','division'].every(key=>
    !ctx[key] || (key==='division'&&!table[key]) || table[key]===ctx[key]);
  if (demo) {
    const tables=data.demo_timetables.filter(table=>table.exam_kind===kind&&scopeMatches(table));
    const ambiguous=['programme','semester','academic_year','division'].filter(key=>!ctx[key]&&new Set(tables.map(table=>table[key])).size>1);
    if (ambiguous.length) return {...base,state:'needs_context',answer:'I found more than one matching demo exam timetable.',clarification_question:`Please tell me your ${ambiguous.join(', ')}.`};
    if (!tables.length) return {...base,state:'needs_context',answer:'The sample contains B.Tech first-year Semester 1 and 2 example dates.',clarification_question:'Select B.Tech, Semester 1 or 2, academic year 2026-27, then choose a subject.'};
    const table=tables[0], requested=ctx.requested_subjects||[];
    let selected=table.rows.filter(row=>requested.some(subject=>canonicalSubject(subject)===canonicalSubject(row.subject)||row.aliases?.some(alias=>canonicalSubject(alias)===canonicalSubject(subject))));
    if (!selected.length) selected=table.rows.filter(row=>[row.subject,...(row.aliases||[])].some(alias=>includesPhrase(question,alias)));
    if (!selected.length&&!requested.length&&/\ball\b|\btimetable\b|\bschedule\b|\bexams\b|\bexaminations\b/i.test(question)) selected=table.rows;
    if (!selected.length) return {...base,state:'needs_context',answer:'That subject is not in the selected demo timetable.',clarification_question:'Choose a subject from the demo table, or ask for all exam dates.'};
    const body=selected.toSorted((a,b)=>a.exam_date.localeCompare(b.exam_date)).map(formatRow).join('\n');
    return {...base,state:'answered',answer:`DEMO — fictional example dates. These are NOT official college exam dates.\n${table.programme}, Semester ${table.semester}, AY ${table.academic_year}\n\n${body}`,
      citations:[{document_id:table.id,document_title:table.title,page:1,version:1,status:'published',source_status:'demo',category:'Examinations',excerpt:body.slice(0,280),open_url:'/demo-exam-timetable.html',source_format:'html',is_sample_data:true}]};
  }
  const uid={end_sem:'jscoe-calendar-endsem',practical:'jscoe-calendar-practical',retest:'jscoe-calendar-retest'}[kind];
  const document=notices.find(doc=>doc.doc_uid===uid&&scopeMatches(doc));
  let answer='I do not have a published subject-wise timetable matching those details. Admin-entered dates require the connected backend.';
  if (document) {
    const target=(ctx.requested_subjects?.length?ctx.requested_subjects:[ctx.subject||'each subject']).join(', ');
    answer=`For ${document.programme}, Semester ${document.semester}, AY ${document.academic_year}:\n${document.answer}\nThe exact paper date/time for ${target} is not specified in this calendar. It must come from a subject-wise timetable.`;
    base.citations=[makeCitation(document)];
  }
  const missing=document&&!ctx.subject&&!/\bmy\b/i.test(question)?[]:['programme','semester','academic_year'].filter(key=>!ctx[key]);
  if (missing.length) return {...base,state:'needs_context',answer,clarification_question:`Please tell me your ${missing.join(', ')} (for example: B.Tech, semester 1, 2026-27).`};
  return {...base,state:'answered',answer:`${answer} Your admin can add exact dates in Admin Login → Exam timetable.`};
}
