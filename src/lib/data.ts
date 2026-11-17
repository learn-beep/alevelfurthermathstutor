import questions from '../data/questions.json';
import papers from '../data/papers.json';
import topics from '../data/topics.json';
import booklet from '../data/booklet.json';

export type Q = (typeof questions)[number];
export type Paper = (typeof papers)[number];
export type Topic = (typeof topics)[number];

export const allQuestions: Q[] = questions as Q[];
export const allPapers: Paper[] = papers as Paper[];
export const allTopics: Topic[] = topics as Topic[];
export const bookletNote = (slug: string): string | undefined => (booklet as Record<string, string>)[slug];

export const byId = new Map(allQuestions.map((q) => [q.id, q]));
export const topicByslug = new Map(allTopics.map((t) => [t.slug, t]));

export function questionsForTopic(slug: string): Q[] {
  return allQuestions.filter((q) => q.topics.includes(slug)).sort((a, b) => b.year - a.year || a.paper.localeCompare(b.paper) || a.question.localeCompare(b.question, undefined, { numeric: true }));
}

export const PEARSON_MATERIALS = 'https://qualifications.pearson.com/en/qualifications/edexcel-a-levels/mathematics-2017.coursematerials.html#filterQuery=category:Pearson-UK:Category%2FExam-materials';

export const STRANDS = ['Core Pure', 'Further Pure 1', 'Further Pure 2', 'Further Statistics 1', 'Further Statistics 2', 'Further Mechanics 1', 'Further Mechanics 2', 'Decision 1', 'Decision 2'];
export const STRAND_CODE: Record<string, string> = { 'Core Pure': 'CP', 'Further Pure 1': 'FP1', 'Further Pure 2': 'FP2', 'Further Statistics 1': 'FS1', 'Further Statistics 2': 'FS2', 'Further Mechanics 1': 'FM1', 'Further Mechanics 2': 'FM2', 'Decision 1': 'D1', 'Decision 2': 'D2' };
export const strandBadge = (s: string): number => (/Statistics/.test(s) ? 2 : /Mechanics/.test(s) ? 3 : /Decision/.test(s) ? 4 : 1);
export const strandMotif = (s: string, slug = ''): string => (/Statistics/.test(s) ? 'stats' : /Mechanics/.test(s) ? 'mech' : /Decision/.test(s) ? 'graph' : /complex|argand|de-moivre|roots-of-unity|polar|t-formulae/.test(slug) ? 'trig' : /matri|vector|eigen|linear-trans|three-eq/.test(slug) ? 'grid' : 'curve');
/** Which papers a strand is examined in, for topic pages. */
export const STRAND_PAPERS: Record<string, string> = {
  'Core Pure': 'A level Papers 1 and 2; AS Paper 1',
  'Further Pure 1': 'A level Paper 3A; AS Paper 2 (option 21)',
  'Further Pure 2': 'A level Paper 4A; AS Paper 2 (option 22)',
  'Further Statistics 1': 'A level Paper 3B; AS Paper 2 (option 23)',
  'Further Statistics 2': 'A level Paper 4B; AS Paper 2 (option 24)',
  'Further Mechanics 1': 'A level Paper 3C; AS Paper 2 (option 25)',
  'Further Mechanics 2': 'A level Paper 4C; AS Paper 2 (option 26)',
  'Decision 1': 'A level Paper 3D; AS Paper 2 (option 27)',
  'Decision 2': 'A level Paper 4D; AS Paper 2 (option 28)',
};
