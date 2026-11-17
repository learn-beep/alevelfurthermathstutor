# alevelfurthermathstutor.com

Static Astro site for Pearson Edexcel A-level Further Maths (9FM0) and AS (8FM0), deployed on Netlify. Built from the Further Maths question bank (133 papers, 2,433 parts, June 2018 to June 2025) using the Maths site as the template.

## Run locally
    npm install
    npm run dev        # http://localhost:4321
    npm run build      # writes dist/

## Deploy
Push to `main` of the linked GitHub repo; Netlify builds with `npm run build` and publishes `dist/` (settings in `netlify.toml`). Set `CROPS=off` to replace every Pearson crop with a link to Pearson's site.

## Data
- `scripts/export.py --bank "C:/Users/twhit/Dropbox/Teaching/Further Maths/Question Bank" [--images]` writes `src/data/questions.json`, `papers.json`, `topics.json`, `spec.json`, `weighting.json`, and with `--images` the WebP crops in `public/img/<paper>/`.
- `scripts/topics_fm.py` is the topic map (75 topics: Core Pure split finely, options by specification section).
- `src/data/booklet.json` is the per-topic formulae-booklet line; `src/data/boundaries.json` and `exams.json` are Pearson's published figures (June 2024–2026 and October 2020 boundaries, Summer 2027 final timetable).
- `src/lib/data.ts` holds the strand list, badges and which papers each strand is examined in.

## Pages
Topics (`/questions/<slug>/`), papers (`/past-papers/<series>-<spec>-<code>/`), spec statements (`/spec/<id>/`), options guide, practice player, mock builder (by option), spec checklist, analysis heat maps by strand, timeline, grade boundaries by option combination with calculator, exam dates, formula booklet, planner, question of the day, hardest questions, tutor page (Emma, £110/h).
