/** Local JSCOE snapshot, used only if the API is unreachable. No invented answers. */
import pack from './jscoeKnowledge.json' with { type: 'json' };
import { enrichExamContext, offlineExamAnswer } from './examEngine.js';

export const OFFLINE_NOTICES = pack.entries.map((entry, i) => ({
  ...entry, id: i + 1, doc_uid: entry.id, doc_type: 'faq', version: pack.revision,
  source_page: entry.source.page, status: 'published', publication_date: null,
  source_url: entry.source.url, source_format: entry.source.format,
  checked_on: entry.source.checked_on, is_sample_data: false,
  source_status: entry.source.historical ? 'historical' : 'snapshot',
}));

const STOP = new Set(('a an the is are was were be am do does did my me i you your we our it its of to in on at for and or if then this that these those when where what which who how can could will would should shall may might get got need needs please tell about with from by as there here next up out so no not yes college jscoe jspm show give want know required require bring have many much available using').split(' '));
const ALIASES = {
  fees: 'fee', cost: 'fee', amount: 'fee', payable: 'fee', exams: 'exam',
  examination: 'exam', examinations: 'exam', documents: 'document', papers: 'document',
  certificates: 'certificate', photographs: 'photo', photos: 'photo', photograph: 'photo',
  pictures: 'photo', dates: 'date', classes: 'class', submissions: 'submission',
  results: 'result', declared: 'declaration', starts: 'start', begin: 'start',
  commence: 'commencement', timetables: 'timetable', notices: 'notice', circulars: 'notice',
  latest: 'current', applying: 'apply', admissions: 'admission', girl: 'girls',
  female: 'girls', boys: 'male', boy: 'male', ka: '', ki: '', ke: '', hai: '',
  kya: '', kab: '', kitna: '', kitni: '', chahiye: '', batao: '', bro: '',
};
function terms(text) {
  const normalized = text.toLowerCase().replace(/\bb\s*\.?\s*(?:tech|e)\b/g, 'btech')
    .replace(/\bend[ -]?(?:sem|semester)\b/g, 'endsem');
  return new Set((normalized.match(/[a-z0-9]+/g) || [])
    .map(t => ALIASES[t] ?? t).filter(t => t && !STOP.has(t))
    .map(t => /^\d+$/.test(t) ? String(Number(t)) : t));
}
function matches(term, haystack) {
  return haystack.has(term) || (term.length >= 4 && [...haystack].some(t =>
    t.length >= 4 && (t.startsWith(term) || term.startsWith(t))));
}
export function canonicalProgramme(value) {
  if (!value?.trim()) return null;
  const clean = value.toLowerCase().replace(/[^a-z0-9]/g, '');
  if (['be', 'btech', 'fe', 'fybtech', 'firstyear', 'firstyearengineering',
    'computerengineering', 'informationtechnology', 'electricalengineering',
    'mechanicalengineering', 'entc', 'electronicsandtelecommunication',
    'artificialintelligenceanddatascience'].includes(clean)) return 'B.Tech';
  if (['me', 'mtech', 'masterofengineering'].includes(clean)) return 'M.E';
  if (['mba', 'mca'].includes(clean)) return clean.toUpperCase();
  return value.trim();
}
export function inferContext(question, context = {}) {
  const result = {...context, programme: canonicalProgramme(context.programme)};
  const q = question.toLowerCase();
  const options = [
    ['MBA', /\bmba\b/], ['MCA', /\bmca\b/], ['M.E', /\bm\s*\.?\s*(?:e|tech)\b/],
    ['B.Tech', /\bb\s*\.?\s*(?:e|tech)\b|\bf\.?\s*y\.?\s*b\.?\s*tech\b|\bfirst[ -]year\b|\bfe\b|\b(?:computer|electrical|mechanical) engineering\b|\binformation technology\b|\bentc\b/],
  ];
  for (const [programme, pattern] of options) if (pattern.test(q)) {
    result.programme = programme; break;
  }
  const year = q.match(/\b(20\d{2})\s*[-/–]\s*(20\d{2}|\d{2})\b/);
  if (year) result.academic_year = `${year[1]}-${year[2].slice(-2)}`;
  else if (/\b20\d{2}\b/.test(q) && q.includes('fee')) {
    const start = q.match(/\b(20\d{2})\b/)[1];
    result.academic_year = `${start}-${String((Number(start) + 1) % 100).padStart(2, '0')}`;
  }
  const sem = q.match(/\bsem(?:ester)?\s*[-:]?\s*([1-8])\b/);
  if (sem) result.semester = sem[1];
  return enrichExamContext(question,result);
}
function categoryFor(question) {
  const q = question.toLowerCase();
  if (/\b(fee|fees|tuition|refund|scholarship)\b/.test(q)) return 'Fees';
  if (/academic calendar|\bcce\b|\binduction\b|project competition/.test(q)) return 'Timetables';
  if (/\b(exam|exams|examination|examinations|retest|result|results|viva)\b|hall ticket/.test(q)) return 'Examinations';
  if (/\b(admission|admissions|document|documents|eligibility)\b/.test(q)) return 'Admissions';
  if (/\b(calendar|timetable|class|classes|lecture)\b|preparation leave|open day/.test(q)) return 'Timetables';
  if (/\b(event|club|activity|competition)\b/.test(q)) return 'College activities';
  return null;
}
function citation(doc) {
  return {
    document_id: doc.doc_uid, document_title: doc.title, page: doc.source.page,
    publication_date: null, version: pack.revision, status: 'published',
    source_status: doc.source.historical ? 'historical' : 'snapshot', category: doc.category,
    excerpt: doc.answer.slice(0, 280), open_url: doc.source.url,
    source_format: doc.source.format, checked_on: doc.source.checked_on, is_sample_data: false,
  };
}

export function offlineAnswer(question, context = {}) {
  const ctx = inferContext(question, context);
  const exam = offlineExamAnswer(question,ctx,OFFLINE_NOTICES,citation);
  if (exam) return exam;
  const category = categoryFor(question);
  const base = {category, knowledge_version: `jscoe-${pack.checked_on}-offline`,
    is_sample_data: false, citations: [], clarification_question: null, ticket_suggested: false};
  let missing = [];
  if (category === 'Fees' && !ctx.programme && !/\b(structure|all programmes|all programs|overview)\b/i.test(question)) missing = ['programme'];
  if (category === 'Examinations' && /\bmy (?:exam|paper)\b/i.test(question)) missing = ['programme', 'semester'].filter(k => !ctx[k]);
  if (missing.length) return {...base, state: 'needs_context',
    answer: 'I need a little more information to find the right source.',
    clarification_question: `Could you tell me your ${missing.join(' and ')}?`};

  let retrievalQuestion = question;
  if (category === 'Examinations' && ctx.subject && !/\b(window|calendar|end.sem|general)\b/i.test(question)) retrievalQuestion += ` ${ctx.subject}`;
  const query = terms(retrievalQuestion);
  const candidates = OFFLINE_NOTICES.filter(doc =>
    !(doc.category === 'Fees' && /\b(hostel|bus|transport|mess|laundry|refund|instalment|installment|deadline|balance|outstanding)\b/i.test(retrievalQuestion)) &&
    !(doc.source.format === 'image' && /\b(room|hall|venue|time|timing|clock|mathematics|physics|chemistry|weekly)\b|\bwhere\b.*\bclass\b|\bnext class\b/i.test(retrievalQuestion)) &&
    (!category || doc.category === category) &&
    (!ctx.programme || !doc.programme || canonicalProgramme(doc.programme) === ctx.programme) &&
    (!ctx.semester || !doc.semester || ctx.semester === doc.semester) &&
    (!ctx.academic_year || !doc.academic_year || ctx.academic_year === doc.academic_year)
  ).map(doc => {
    const haystack = terms([doc.answer, doc.title, doc.category, doc.programme,
      doc.academic_year, doc.semester, ...doc.questions].filter(Boolean).join(' '));
    const matched = [...query].filter(t => matches(t, haystack)).length;
    const coverage = matched / Math.max(query.size, 1);
    const similarity = Math.max(...doc.questions.map(q => {
      const other = terms(q);
      return [...query].filter(t => other.has(t)).length / Math.max(new Set([...query, ...other]).size, 1);
    }));
    return {doc, coverage, score: 0.55 * coverage + 0.25 * matched / haystack.size +
      0.3 * similarity + (ctx.programme && doc.programme ? 0.08 : 0)};
  }).filter(item => item.coverage >= 0.75).sort((a, b) => b.score - a.score);
  if (!candidates.length) return {...base, state: 'escalated', ticket_suggested: true,
    answer: 'The saved JSCOE sources do not confirm that detail. You can ask the relevant college office or raise a ticket when the service is connected.'};
  const doc = candidates[0].doc;
  const archivalDeadline = doc.source.historical && /deadline|last date|when.*(?:form|fill)|hall.ticket|my exam|my paper|\bdate\b|\btime\b/i.test(question);
  return {...base, category: doc.category, state: archivalDeadline ? 'escalated' : 'answered',
    answer: doc.answer, citations: [citation(doc)], ticket_suggested: archivalDeadline};
}
