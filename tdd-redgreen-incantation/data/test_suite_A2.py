#!/usr/bin/env python3
"""Test merge_banks.py handles all levels present in banks-all.json.

Runs merge_banks.py in an isolated temp dir with a synthetic banks file
(4 levels) and a synthetic expansion input covering:
- new items merged in for every level (incl. 準2級 / 2級)
- dedup vs existing bank items (vocab en, reading title, speaking first-5,
  writing first-8)
- dedup within the new batch itself
- a level present in input format wrapped in {"result": ...}
- report line format unchanged: "L/kind B -> A (+K, dup-dropped D)"
"""
import json, os, shutil, subprocess, sys, tempfile

SRC = os.path.dirname(os.path.abspath(__file__))

def vocab(en): return {"en": en, "ja": "x"}
def reading(title): return {"title": title, "body": "x"}
def speaking(passage): return {"passage": passage}
def writing(prompt): return {"prompt": prompt}

LEVELS = ["3級", "4級", "準2級", "2級"]

banks = {
    lvl: {
        "vocab": [vocab(f"apple-{lvl}")],
        "reading": [reading(f"Old Title {lvl}")],
        "speaking": [speaking(f"one two three four five six {lvl}")],
        "writing": [writing(f"w1 w2 w3 w4 w5 w6 w7 w8 tail {lvl}")],
    }
    for lvl in LEVELS
}

add = {"result": {
    lvl: {
        # 1 dup-vs-bank (case-insensitive), 1 new, 1 in-batch dup of the new one
        "vocab": [vocab(f"APPLE-{lvl}"), vocab(f"banana-{lvl}"), vocab(f"Banana-{lvl}")],
        # dup by title vs bank + 1 new
        "reading": [reading(f"old title {lvl}"), reading(f"New Title {lvl}")],
        # dup by first 5 words (rest differs) + 1 new
        "speaking": [speaking(f"one two three four five DIFFERENT {lvl}"),
                     speaking(f"a b c d e fresh {lvl}")],
        # dup by first 8 words (9th differs) + 1 new
        "writing": [writing(f"w1 w2 w3 w4 w5 w6 w7 w8 OTHER {lvl}"),
                    writing(f"p1 p2 p3 p4 p5 p6 p7 p8 new {lvl}")],
    }
    for lvl in LEVELS
}}

tmp = tempfile.mkdtemp(prefix="merge-banks-test-")
try:
    os.makedirs(os.path.join(tmp, "banks"))
    json.dump(banks, open(os.path.join(tmp, "banks/banks-all.json"), "w"), ensure_ascii=False)
    json.dump(add, open(os.path.join(tmp, "add.json"), "w"), ensure_ascii=False)
    shutil.copy(os.path.join(SRC, "merge_banks.py"), tmp)

    out = subprocess.run([sys.executable, "merge_banks.py", "add.json"],
                         cwd=tmp, capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    lines = out.stdout.strip().splitlines()

    # Every level x kind must be reported: 4 levels * 4 kinds = 16 lines
    assert len(lines) == 16, f"expected 16 report lines, got {len(lines)}:\n{out.stdout}"

    expected = {
        "vocab":    "1 -> 2 (+1, dup-dropped 2)",  # bank-dup + in-batch dup
        "reading":  "1 -> 2 (+1, dup-dropped 1)",
        "speaking": "1 -> 2 (+1, dup-dropped 1)",
        "writing":  "1 -> 2 (+1, dup-dropped 1)",
    }
    got = dict(l.split(" ", 1) for l in lines)
    for lvl in LEVELS:
        for kind, val in expected.items():
            key = f"{lvl}/{kind}"
            assert got.get(key) == val, f"{key}: expected {val!r}, got {got.get(key)!r}"

    # Merged file: each level/kind has exactly 2 items, kept item is the new one
    merged = json.load(open(os.path.join(tmp, "banks/banks-all.json")))
    assert list(merged.keys()) == LEVELS
    for lvl in LEVELS:
        assert merged[lvl]["vocab"][1]["en"] == f"banana-{lvl}"
        assert merged[lvl]["reading"][1]["title"] == f"New Title {lvl}"
        assert merged[lvl]["speaking"][1]["passage"].startswith("a b c d e")
        assert merged[lvl]["writing"][1]["prompt"].startswith("p1 p2")
        for kind in expected:
            assert len(merged[lvl][kind]) == 2

    # Level in banks but absent from input -> skipped silently, bank untouched
    add2 = {"3級": {"vocab": [vocab("cherry-3級")]}}
    json.dump(add2, open(os.path.join(tmp, "add2.json"), "w"), ensure_ascii=False)
    out2 = subprocess.run([sys.executable, "merge_banks.py", "add2.json"],
                          cwd=tmp, capture_output=True, text=True)
    assert out2.returncode == 0, out2.stderr
    lines2 = out2.stdout.strip().splitlines()
    assert lines2 == ["3級/vocab 2 -> 3 (+1, dup-dropped 0)"], lines2
    merged2 = json.load(open(os.path.join(tmp, "banks/banks-all.json")))
    assert len(merged2["2級"]["vocab"]) == 2  # untouched

    print("ALL TESTS PASSED")
finally:
    shutil.rmtree(tmp)
