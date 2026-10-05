import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent
CONTENT = ROOT / "content"

ERAS = ["نشأة الدولة", "مصر القديمة", "العصر الوسيط", "العصر الحديث"]

KEYS = [
    ("3200 ق.م", "توحيد القُطرين على يد الملك مينا (نعارمر) وبداية عصر الدولة القديمة"),
    ("332 ق.م", "دخول الإسكندر الأكبر مصر"),
    ("30 ق.م", "دخول مصر تحت الحكم الروماني"),
    ("641م", "الفتح الإسلامي لمصر"),
    ("1517م", "دخول مصر تحت الحكم العثماني"),
    ("1798م", "الحملة الفرنسية على مصر"),
    ("1805م", "تولي محمد علي حكم مصر وبداية بناء الدولة الحديثة"),
    ("1882م", "الاحتلال البريطاني لمصر"),
    ("1919م", "ثورة الشعب المصري ضد الاحتلال البريطاني"),
    ("1952م", "ثورة يوليو وبناء الجمهورية"),
    ("1973م", "حرب أكتوبر واستعادة الكرامة الوطنية"),
]

EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿]")


def strings(o):
    if isinstance(o, str):
        yield o
    elif isinstance(o, dict):
        for v in o.values():
            yield from strings(v)
    elif isinstance(o, list):
        for v in o:
            yield from strings(v)


def check_q(q, where, errs):
    t = q.get("type")
    w = f"{where} [{t}] {str(q.get('q', ''))[:40]}"
    if t in ("mcq", "fill", "who"):
        o = q.get("options", [])
        if not (3 <= len(o) <= 5) or len(set(o)) != len(o):
            errs.append(f"{w}: options")
        if not isinstance(q.get("answer"), int) or not 0 <= q["answer"] < len(o):
            errs.append(f"{w}: answer")
        if t == "fill" and (q["q"].count("____") != 1 or "_____" in q["q"]):
            errs.append(f"{w}: blank")
        if t == "who" and len(q.get("clues", [])) < 2:
            errs.append(f"{w}: clues")
    elif t == "tf":
        if not isinstance(q.get("answer"), bool):
            errs.append(f"{w}: tf answer")
    elif t == "order":
        it = q.get("items", [])
        if not (2 <= len(it) <= 6) or len(set(it)) != len(it):
            errs.append(f"{w}: items")
    elif t == "match":
        p = q.get("pairs", [])
        if not (2 <= len(p) <= 6) or any(len(x) != 2 for x in p):
            errs.append(f"{w}: pairs")
        elif len({x[0] for x in p}) != len(p) or len({x[1] for x in p}) != len(p):
            errs.append(f"{w}: duplicate pair side")
    elif t == "sort":
        b = q.get("buckets", [])
        it = q.get("items", [])
        if not (2 <= len(b) <= 3) or len(it) < 3:
            errs.append(f"{w}: sort size")
        if any(len(x) != 2 or not isinstance(x[1], int) or not 0 <= x[1] < len(b) for x in it):
            errs.append(f"{w}: sort items")
    else:
        errs.append(f"{w}: unknown type")


def main():
    lessons = [json.loads((CONTENT / f"lesson{i}.json").read_text(encoding="utf-8")) for i in range(1, 5)]
    mapping = json.loads((ROOT / "keys.json").read_text(encoding="utf-8"))
    errs = []
    sids = set()
    for i, l in enumerate(lessons):
        l["era"] = ERAS[i]
        for s in l["sections"]:
            if s["id"] in sids:
                errs.append(f"dup section {s['id']}")
            sids.add(s["id"])
            if not s.get("cards") or not s.get("quiz"):
                errs.append(f"{s['id']}: empty")
            for c in s["cards"]:
                if c.get("kind") not in ("concept", "date", "person", "place", "cause", "result", "fact", "quote"):
                    errs.append(f"{s['id']}: card kind {c.get('kind')}")
            for q in s["quiz"]:
                check_q(q, s["id"], errs)
    for txt in strings(lessons):
        if EMOJI.search(txt):
            errs.append(f"emoji: {txt[:50]}")
        if txt.count("**") % 2:
            errs.append(f"unbalanced bold: {txt[:60]}")
    keys = []
    for (d, e), sid in zip(KEYS, mapping):
        if sid not in sids and sid != "boss":
            errs.append(f"key {d} -> unknown section {sid}")
        keys.append({"d": d, "e": e, "sid": sid})
    if len(mapping) != len(KEYS):
        errs.append("keys.json must list 11 section ids")
    if errs:
        print("\n".join(errs))
        sys.exit(1)
    data = json.dumps({"lessons": lessons, "keys": keys}, ensure_ascii=False, separators=(",", ":"))
    data = data.replace("</", "<\\/")
    html = (ROOT / "template.html").read_text(encoding="utf-8").replace("__DATA__", data)
    (ROOT.parent / "index.html").write_text(html, encoding="utf-8")
    nq = sum(len(s["quiz"]) for l in lessons for s in l["sections"])
    nc = sum(len(s["cards"]) for l in lessons for s in l["sections"])
    print(f"built index.html: {len(html) // 1024} KB, {len(sids)} sections, {nc} cards, {nq} questions")


main()
