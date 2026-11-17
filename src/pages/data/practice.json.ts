import { allQuestions, allTopics } from '../../lib/data';
// Slim question list for the client-side tools (player, mock builder, question of the day).
export function GET() {
  const q = allQuestions.map((x) => ({
    id: x.id, t: x.topics, s: x.series, y: x.year, p: x.paper, l: x.level, q: x.question, m: x.marks,
    d: x.difficulty, c: x.crop, ms: x.msCrop, mb: x.msBands, e: x.erText && x.erText.length > 280 ? x.erText.slice(0, 277).replace(/\s+\S*$/, '') + '…' : x.erText, a: x.area,
  }));
  const topics = allTopics.map((t) => ({ slug: t.slug, name: t.name, strand: t.strand, parts: t.parts }));
  return new Response(JSON.stringify({ q, topics }), { headers: { 'Content-Type': 'application/json' } });
}
