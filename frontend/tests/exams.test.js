import assert from 'node:assert/strict';
import test from 'node:test';
import {offlineAnswer} from '../src/lib/offlineEngine.js';
import {DEMO_TIMETABLES,enrichExamContext,prettyExamDate} from '../src/lib/examEngine.js';

for (const subject of ['math','maths1','M1','physics','chemistry','mechanics','graphics','BEEE','C programming','FMPP','DTI','PCS']) {
  test(`College calendar help without a ticket: ${subject}`,()=>{
    const result=offlineAnswer(`when was my sem 1 ${subject} exam`);
    assert.equal(result.state,'needs_context');
    assert.equal(result.ticket_suggested,false);
    assert.ok(result.answer.includes('23 December 2026'));
    assert.ok(result.answer.includes('not specified'));
  });
}
for (const table of DEMO_TIMETABLES) for (const row of table.rows) {
  test(`Explicit demo, semester ${table.semester}: ${row.subject}`,()=>{
    const result=offlineAnswer(`When is my semester ${table.semester} ${row.subject} exam?`,{programme:'B.Tech',academic_year:'2026-27',exam_data_mode:'demo'});
    assert.equal(result.state,'answered');
    assert.equal(result.is_sample_data,true);
    assert.equal(result.data_origin,'demo');
    assert.ok(result.answer.includes('NOT official'));
    assert.ok(result.answer.includes(prettyExamDate(row.exam_date)));
  });
}
test('Demo dates and rooms never appear in college mode',()=>{
  const result=offlineAnswer('When is my sem1 maths exam?',{programme:'B.Tech',academic_year:'2026-27'});
  assert.equal(result.data_origin,'college');
  assert.equal(result.is_sample_data,false);
  assert.ok(!result.answer.includes('Example Room'));
});
test('Semester words, numerals and subject changes are understood',()=>{
  assert.equal(enrichExamContext('When is my first semester EP exam?',{}).semester,'1');
  assert.equal(enrichExamContext('When is my semester II maths exam?',{}).subject,'Engineering Mathematics II');
  assert.equal(enrichExamContext('When is my sem2 cpp exam?',{}).subject,'Programming in C++');
  assert.equal(enrichExamContext('When is my Biology exam?',{subject:'Maths'}).subject,'biology');
});
test('All-subject request clears a previous individual subject',()=>{
  const ctx=enrichExamContext('Show all first year exams',{subject:'Maths'});
  assert.equal(ctx.subject,null);
});
