#!/usr/bin/env python3
"""
export.py — build the site's data files (and optionally WebP crops) from the Further Maths question bank export.

Usage, from the repo root:
    python scripts/export.py --bank "C:/Users/twhit/Dropbox/Teaching/Further Maths/Question Bank"
    python scripts/export.py --bank "<same>" --images            # also converts crops to public/img/<bundle>/*.webp
    python scripts/export.py --bank "<same>" --images --only JUN24_9FM001   # one bundle, for testing (rewrites data with one paper)
Writes src/data/questions.json, papers.json, topics.json, spec.json, weighting.json.
Topic map: scripts/topics_fm.py.
"""
import argparse, base64, io, json, pathlib, re, sys
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from topics_fm import TOPICS, D2SEC, AREA_STRAND

SHORT = {"CP": "Core Pure", "FP1": "Further Pure 1", "FP2": "Further Pure 2", "FS1": "Further Statistics 1", "FS2": "Further Statistics 2",
         "FM1": "Further Mechanics 1", "FM2": "Further Mechanics 2", "D1": "Decision 1", "D2": "Decision 2"}

def paper_label(p):
    code = p["paper"]
    if p["spec"] == "9FM0":
        if code == "01": return "Paper 1 (Core Pure 1)"
        if code == "02": return "Paper 2 (Core Pure 2)"
        return f"Paper {code} ({SHORT[p['area']]})"
    if code == "01": return "Paper 1 (Core Pure)"
    return f"Paper 2 ({SHORT[p['area']]})"

def label(l):
    m = re.match(r"^0*(\d+)(.*)$", l)
    if not m: return l
    n, rest = m.group(1), m.group(2)
    if rest and not rest.startswith("("): rest = "(" + rest + ")"
    return n + rest

def load_qb(bank):
    js = (bank / "data" / "index.js").read_text(encoding="utf-8")
    assert js.startswith("window.QB="), "unexpected index.js"
    return json.loads(js[len("window.QB="):].rstrip(";\n"))

def img_path(prefix, name):
    # The bank dedupes identical crops across papers, so a file can live in another paper's bundle: take the bundle from the file name.
    if not name: return None
    return f"/img/{'_'.join(name.split('_')[:2])}/{pathlib.Path(name).stem}.webp"

def convert(args):
    f, img_out, quality = args
    from PIL import Image
    prefix = pathlib.Path(f).stem
    txt = pathlib.Path(f).read_text(encoding="utf-8")
    m = re.match(r'QBIMG_LOADED\("([^"]+)",\s*(\{.*\})\);?\s*$', txt, re.S)
    if not m: return prefix, -1
    bundle = json.loads(m.group(2))
    dest = pathlib.Path(img_out) / prefix; dest.mkdir(parents=True, exist_ok=True)
    for name, data in bundle.items():
        target = dest / (pathlib.Path(name).stem + ".webp")
        if target.exists(): continue
        raw = base64.b64decode(data.split(",", 1)[1])
        im = Image.open(io.BytesIO(raw)).convert("RGB")
        im.save(target, "WEBP", quality=quality, method=6)
    return prefix, len(bundle)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bank", required=True)
    ap.add_argument("--out", default="src/data")
    ap.add_argument("--img-out", default="public/img")
    ap.add_argument("--images", action="store_true")
    ap.add_argument("--only")
    ap.add_argument("--quality", type=int, default=72)
    a = ap.parse_args()
    bank, out = pathlib.Path(a.bank), pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    QB = load_qb(bank)
    papers = {p["id"]: p for p in QB["papers"]}
    sec_ids = {s["code"]: [st["id"] for st in s["st"]] for s in QB["spec"]}
    topics = [(slug, name, strand, ids if ids is not None else sec_ids[D2SEC[slug]]) for slug, name, strand, ids in TOPICS]
    stmt_to_slugs = defaultdict(list)
    for slug, _, _, ids in topics:
        for i in ids: stmt_to_slugs[i].append(slug)
    all_ids = {st["id"] for s in QB["spec"] for st in s["st"]}
    missing = all_ids - set(stmt_to_slugs)
    if missing: print("statements with no topic:", sorted(missing))
    area_title = {k: v for k, v in SHORT.items()}
    stmt_area = {st["id"]: s["area"] for s in QB["spec"] for st in s["st"]}
    stmt_text = {st["id"]: st["t"] for s in QB["spec"] for st in s["st"]}
    stmt_level = {st["id"]: st.get("lv") for s in QB["spec"] for st in s["st"]}

    questions, per_paper = [], defaultdict(list)
    weighting = defaultdict(lambda: defaultdict(int))
    tc_all = defaultdict(lambda: {"parts": 0, "marks": 0, "papers": set(), "levels": set()})
    for q in QB["q"]:
        p = papers[q["p"]]
        if a.only and p["prefix"] != a.only: continue
        st = q.get("st", [])
        prim = [s for s, r in st if r == "A"] or [s for s, _ in st]
        slugs = []
        for sid in prim:
            for s in stmt_to_slugs.get(sid, []):
                if s not in slugs: slugs.append(s)
        level = "AS" if p["qual"] == "AS" else "A level"
        rec = {
            "id": q["id"], "paperId": p["id"], "bundle": p["prefix"], "series": p["series"], "year": p["year"],
            "spec": p["spec"], "paperCode": p["paper"], "paper": paper_label(p), "paperName": p["name"],
            "area": p["area"], "strand": AREA_STRAND[p["area"]], "question": label(q["l"]), "marks": q["m"], "level": level,
            "difficulty": None if q["d"] == "Not rated" else q["d"], "topics": slugs,
            "statements": [s for s, _ in st], "ao": q.get("ao"), "commands": q.get("cmd", []),
            "mistakes": q.get("mc", []), "text": q.get("qt", ""), "erText": q.get("et") or "",
            "crop": img_path(p["prefix"], q.get("qi")), "msCrop": img_path(p["prefix"], q.get("mi")),
            "erCrop": img_path(p["prefix"], q.get("ei")), "msBands": q.get("mb") or [],
        }
        questions.append(rec)
        per_paper[p["id"]].append(rec["id"])
        for sid, role in st:
            if role == "A":
                sec = sid.rsplit(".", 1)[0]
                weighting[p["id"]][sec] += q["m"]
        for s in slugs:
            t = tc_all[s]; t["parts"] += 1; t["marks"] += q["m"]; t["papers"].add(rec["paper"]); t["levels"].add(level)

    (out / "questions.json").write_text(json.dumps(questions, ensure_ascii=False), encoding="utf-8")

    paper_recs = []
    for pid, p in papers.items():
        if a.only and p["prefix"] != a.only: continue
        paper_recs.append({"id": pid, "bundle": p["prefix"], "series": p["series"], "year": p["year"], "qual": p["qual"],
            "spec": p["spec"], "code": p["paper"], "paper": paper_label(p), "name": p["name"], "area": p["area"],
            "strand": AREA_STRAND[p["area"]], "total": p["total"],
            "slug": f"{p['series'].lower().replace(' ', '-')}-{p['spec'].lower()}-{p['paper'].lower()}",
            "questions": per_paper[pid]})
    order = {"01": 0, "02": 1, "3A": 2, "3B": 3, "3C": 4, "3D": 5, "4A": 6, "4B": 7, "4C": 8, "4D": 9}
    paper_recs.sort(key=lambda r: (-r["year"], r["series"], r["spec"] != "9FM0", order.get(r["code"], int(r["code"]) if r["code"].isdigit() else 99)))
    (out / "papers.json").write_text(json.dumps(paper_recs, ensure_ascii=False, indent=0), encoding="utf-8")

    topic_recs = []
    for slug, name, strand, ids in topics:
        t = tc_all[slug]
        topic_recs.append({"slug": slug, "name": name, "strand": strand, "statements": ids,
            "statementText": {i: stmt_text.get(i, "") for i in ids}, "levels": {i: stmt_level.get(i) for i in ids},
            "parts": t["parts"], "marks": t["marks"], "papers": sorted(t["papers"]),
            "asOrA": "AS and A level" if "AS" in t["levels"] else "A level only"})
    (out / "topics.json").write_text(json.dumps(topic_recs, ensure_ascii=False, indent=0), encoding="utf-8")

    spec_recs = []
    for sec in QB["spec"]:
        spec_recs.append({"code": sec["code"], "title": sec["title"], "area": sec.get("area"), "strand": AREA_STRAND[sec["area"]],
            "statements": [{"id": st["id"], "short": st.get("sh") or "", "text": st["t"], "guidance": st.get("g") or "",
                            "level": st.get("lv") or "", "aLevelPart": st.get("ap") or "",
                            "topics": stmt_to_slugs.get(st["id"], [])} for st in sec["st"]]})
    (out / "spec.json").write_text(json.dumps(spec_recs, ensure_ascii=False, indent=0), encoding="utf-8")
    sections = {s["code"]: f"{s['code']} {s['title']}" for s in QB["spec"]}
    (out / "weighting.json").write_text(json.dumps({"areas": area_title, "sections": sections, "byPaper": {k: dict(v) for k, v in weighting.items()}}, ensure_ascii=False), encoding="utf-8")
    print(f"questions {len(questions)}, papers {len(paper_recs)}, topics {len(topic_recs)} -> {out}")
    print("no topic:", sum(1 for q in questions if not q["topics"]))

    if a.images:
        files = sorted(str(f) for f in (bank / "data" / "img").glob("*.js") if not a.only or f.stem == a.only)
        n = 0
        with ProcessPoolExecutor() as ex:
            for prefix, k in ex.map(convert, [(f, a.img_out, a.quality) for f in files]):
                print(prefix, k); n += max(k, 0)
        print("images:", n)

if __name__ == "__main__":
    main()
