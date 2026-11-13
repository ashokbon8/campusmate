import {useEffect,useState} from 'react';
import {CalendarDays,Plus,Save,Trash2} from 'lucide-react';
import {adminExamTimetables,adminSaveExamTimetable} from '../lib/api.js';
import {EXAM_SUBJECTS} from '../lib/examEngine.js';

const emptyRow=()=>({subject:'',exam_date:'',start_time:'',venue:'',aliases:''});
export default function ExamTimetableEditor() {
  const [form,setForm]=useState({programme:'B.Tech',semester:'1',academic_year:'2026-27',division:'',exam_kind:'end_sem'});
  const [rows,setRows]=useState([emptyRow()]);
  const [tables,setTables]=useState([]);
  const [error,setError]=useState('');
  const [message,setMessage]=useState('');
  const [busy,setBusy]=useState(false);
  const load=()=>adminExamTimetables().then(setTables).catch(error=>setError(error.message));
  useEffect(()=>{load();},[]);
  const field=key=>event=>setForm({...form,[key]:event.target.value});
  const rowField=(index,key)=>event=>setRows(old=>old.map((row,i)=>i===index?{...row,[key]:event.target.value}:row));
  function edit(id) {
    const table=tables.find(item=>String(item.document_id)===id);
    if (!table) return;
    setForm({programme:table.programme,semester:table.semester,academic_year:table.academic_year,division:table.division||'',exam_kind:table.exam_kind});
    setRows(table.rows.map(row=>({...row,start_time:row.start_time||'',venue:row.venue||'',aliases:(row.aliases||[]).join(', ')})));
    setMessage('Timetable loaded. Edit the dates and save to publish a replacement.');
  }
  async function submit(event) {
    event.preventDefault();setBusy(true);setError('');setMessage('');
    try {
      await adminSaveExamTimetable({...form,division:form.division.trim()||null,
        rows:rows.map(row=>({...row,start_time:row.start_time||null,venue:row.venue.trim()||null,
          aliases:row.aliases.split(',').map(value=>value.trim()).filter(Boolean)}))});
      setMessage('Timetable published. Students can now ask for any listed subject, or all exam dates.');
      await load();
    } catch(error) {setError(error.message);} finally {setBusy(false);}
  }
  return <section>
    <div className="notice-banner"><CalendarDays size={18}/><span>Enter your own subject-wise dates here. Answers label these as an admin-entered timetable; demo examples stay separate.</span></div>
    {tables.length>0&&<label className="exam-load">Edit an existing timetable
      <select defaultValue="" onChange={event=>edit(event.target.value)}><option value="">Choose a timetable…</option>
        {tables.map(table=><option key={table.document_id} value={table.document_id}>{table.programme} · Sem {table.semester} · {table.academic_year}{table.division?` · ${table.division}`:''} · {table.exam_kind}</option>)}
      </select></label>}
    <form className="upload-form exam-editor" onSubmit={submit}>
      <h2 className="admin-subhead"><CalendarDays size={18}/> Exam timetable</h2>
      <div className="field-grid">
        <label>Programme<input value={form.programme} onChange={field('programme')} required maxLength={64}/></label>
        <label>Semester<select value={form.semester} onChange={field('semester')}>{[1,2,3,4,5,6,7,8].map(value=><option key={value} value={String(value)}>{value}</option>)}</select></label>
        <label>Academic year<input value={form.academic_year} onChange={field('academic_year')} placeholder="2026-27" pattern="20[0-9]{2}-[0-9]{2}" required/></label>
        <label>Division / group (optional)<input value={form.division} onChange={field('division')} maxLength={32} placeholder="e.g. A"/></label>
        <label>Exam type<select value={form.exam_kind} onChange={field('exam_kind')}>
          <option value="end_sem">End-semester exam</option><option value="in_sem">In-semester test</option><option value="practical">Practical / viva</option><option value="retest">Retest</option>
        </select></label>
      </div>
      <p className="form-lead">Add any subject, including subjects in later semesters. The first-year subject list is a starting point; remove courses that do not apply to your class.</p>
      <div className="exam-editor-actions">
        <button className="btn btn-outline btn-small" type="button" disabled={Number(form.semester)>2||busy} onClick={()=>setRows(EXAM_SUBJECTS.filter(course=>!course.semester||String(course.semester)===form.semester).map(course=>({...emptyRow(),subject:course.name,aliases:course.aliases.slice(0,10).join(', ')})))}>Load first-year subject names</button>
        <button className="btn btn-outline btn-small" type="button" disabled={busy} onClick={()=>setRows([...rows,emptyRow()])}><Plus size={15}/> Add subject</button>
      </div>
      <datalist id="exam-subject-options">{EXAM_SUBJECTS.map(course=><option value={course.name} key={course.code}/>)}</datalist>
      <div className="exam-rows">
        {rows.map((row,index)=><fieldset className="exam-row" key={index} disabled={busy}>
          <legend>Subject {index+1}</legend>
          <div className="field-grid">
            <label>Subject name<input list="exam-subject-options" value={row.subject} onChange={rowField(index,'subject')} required maxLength={128} placeholder="e.g. Engineering Physics"/></label>
            <label>Exam date<input type="date" value={row.exam_date} onChange={rowField(index,'exam_date')} required/></label>
            <label>Start time (optional)<input type="time" value={row.start_time} onChange={rowField(index,'start_time')}/></label>
            <label>Room / venue (optional)<input value={row.venue} onChange={rowField(index,'venue')} maxLength={128}/></label>
            <label>Other names, separated by commas<input value={row.aliases} onChange={rowField(index,'aliases')} maxLength={300} placeholder="e.g. Physics, EP"/></label>
          </div>
          <button type="button" className="btn btn-small btn-outline" disabled={rows.length===1} onClick={()=>setRows(rows.filter((_,i)=>i!==index))}><Trash2 size={14}/> Remove subject</button>
        </fieldset>)}
      </div>
      <p className="form-lead">Saving publishes these dates and replaces an existing timetable for the same programme, semester, year, division and exam type.</p>
      {error&&<p role="alert" className="form-error">{error}</p>}
      {message&&<p role="status" className="flash success">{message}</p>}
      <button className="btn btn-primary" type="submit" disabled={busy}><Save size={16}/>{busy?'Publishing…':'Save and publish timetable'}</button>
    </form>
  </section>;
}
