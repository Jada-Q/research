#!/usr/bin/env python3
"""Tests for merge_banks.py multi-level support.

Runs merge_banks.py as a subprocess in a sandbox dir (it hardcodes
banks/banks-all.json relative to cwd) against a synthetic bank with the
real 4 levels, checking:
- every level present in banks gets merged (no hardcoded level list)
- dedup rules unchanged (vocab en / reading title / speaking first-5 / writing first-8)
- report line format unchanged
- levels in the input but absent from banks are ignored (old behavior for unknown keys)
"""
import json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
LEVELS = ["3級", "4級", "準2級", "2級"]

def make_bank():
    bank = {}
    for i, lvl in enumerate(LEVELS):
        bank[lvl] = {
            "vocab": [{"en": f"apple{i}", "ja": "x"}],
            "reading": [{"title": f"Old Title {i}", "body": "x"}],
            "speaking": [{"passage": f"one two three four five{i} tail tail"}],
            "writing": [{"prompt": f"a b c d e f g h{i} tail tail"}],
        }
    return bank

def make_addition():
    add = {}
    for i, lvl in enumerate(LEVELS):
        add[lvl] = {
            # 1 dup (same en, different case/space) + 1 new
            "vocab": [{"en": f" Apple{i} ", "ja": "dup"}, {"en": f"banana{i}", "ja": "new"}],
            # 1 dup by title (case-insensitive) + 1 new
            "reading": [{"title": f"old title {i}", "body": "dup"},
                        {"title": f"New Title {i}", "body": "new"}],
            # dup: same first 5 words, different tail; new: differs within first 5
            "speaking": [{"passage": f"one two three four five{i} DIFFERENT tail"},
                         {"passage": f"six seven eight nine ten{i} tail"}],
            # dup: same first 8 words; new: differs within first 8
            "writing": [{"prompt": f"a b c d e f g h{i} DIFFERENT"},
                        {"prompt": f"p q r s t u v w{i} tail"}],
        }
    # a level that does not exist in banks must be ignored, not crash
    add["1級"] = {"vocab": [{"en": "zebra", "ja": "x"}]}
    return add

def main():
    tmp = tempfile.mkdtemp(prefix="merge-banks-test-")
    try:
        os.makedirs(os.path.join(tmp, "banks"))
        shutil.copy(os.path.join(HERE, "merge_banks.py"), tmp)
        json.dump(make_bank(), open(os.path.join(tmp, "banks/banks-all.json"), "w"),
                  ensure_ascii=False)
        json.dump({"result": make_addition()}, open(os.path.join(tmp, "add.json"), "w"),
                  ensure_ascii=False)

        r = subprocess.run([sys.executable, "merge_banks.py", "add.json"],
                           cwd=tmp, capture_output=True, text=True)
        assert r.returncode == 0, f"merge_banks.py failed:\n{r.stderr}"
        out_lines = r.stdout.strip().splitlines()

        merged = json.load(open(os.path.join(tmp, "banks/banks-all.json")))

        # 1. all 4 real levels merged, unknown level ignored
        assert set(merged.keys()) == set(LEVELS), merged.keys()
        for i, lvl in enumerate(LEVELS):
            for kind in ("vocab", "reading", "speaking", "writing"):
                items = merged[lvl][kind]
                assert len(items) == 2, f"{lvl}/{kind}: expected 2, got {len(items)}"
            # dedup kept the ORIGINAL item, not the dup variant
            assert merged[lvl]["vocab"][0]["ja"] == "x"
            assert {v["en"] for v in merged[lvl]["vocab"]} == {f"apple{i}", f"banana{i}"}
        assert not any(v.get("en") == "zebra"
                       for lvl in merged.values() for v in lvl["vocab"])

        # 2. report format unchanged: "<lvl>/<kind> <b> -> <a> (+k, dup-dropped d)"
        assert len(out_lines) == 16, f"expected 16 report lines, got {len(out_lines)}:\n{r.stdout}"
        expected = {f"{lvl}/{kind} 1 -> 2 (+1, dup-dropped 1)"
                    for lvl in LEVELS for kind in ("vocab", "reading", "speaking", "writing")}
        assert set(out_lines) == expected, f"report mismatch:\n{r.stdout}"

        print("OK: all assertions passed (4 levels merged, dedup + report format intact)")
    finally:
        shutil.rmtree(tmp)

if __name__ == "__main__":
    main()
