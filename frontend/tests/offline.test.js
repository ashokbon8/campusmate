import assert from 'node:assert/strict';
import test from 'node:test';
import { offlineAnswer } from '../src/lib/offlineEngine.js';

const cases = [
  ['Which documents are required for admission?', 'jscoe-admission-checklist', 'Two colour photographs'],
  ['What are the B.Tech fees for 2026-27?', 'jscoe-fees-engineering', '1,20,000'],
  ['What are MBA OBC male fees?', 'jscoe-fees-mba', '50,304'],
  ['How much is MCA tuition?', 'jscoe-fees-mca', '74,783'],
  ['Show the first year academic calendar', 'jscoe-calendar', '21 September 2026'],
  ['When is CCE 4 submission?', 'jscoe-calendar-cce4', '20 November 2026'],
  ['When are first year end semester exams?', 'jscoe-calendar-endsem', '07 January 2027'],
  ['When are retest results declared?', 'jscoe-calendar-retest-result', '30 January 2027'],
  ['When does semester 2 start?', 'jscoe-calendar-next-semester', '01 February 2027'],
];
for (const [question, id, fact] of cases) test(question, () => {
  const result = offlineAnswer(question);
  assert.equal(result.state, 'answered');
  assert.equal(result.citations[0].document_id, id);
  assert.ok(result.answer.includes(fact));
  assert.equal(result.is_sample_data, false);
});
for (const question of ['What are the B.Tech fees for 2027-28?', 'What is the B.Tech hostel fee?',
  'What is the canteen menu?', 'Can I pay MBA fees in instalments?']) test(`Unknown: ${question}`, () => {
  assert.equal(offlineAnswer(question).state, 'escalated');
});
test('Specific subject date is not inferred from calendar window', () => {
  const result=offlineAnswer('When is my exam?', {programme: 'B.Tech', semester: '1', subject: 'Mathematics'});
  assert.equal(result.state, 'needs_context');
  assert.equal(result.ticket_suggested,false);
  assert.ok(result.answer.includes('not specified'));
});
test('Next classroom location is not inferred from teaching start date', () => {
  assert.equal(offlineAnswer('Where is the next B.Tech class?', {semester: '1'}).state, 'escalated');
});
