#!/usr/bin/env python3
"""Merge expansion output into banks-all.json with a mechanical dedup pass.
Usage: python3 merge_banks.py <workflow-output.json>
Dedup keys: vocab by en(lower); reading by title(lower); speaking by first 5 words
of passage; writing by first 8 words of prompt. Prints before/after counts."""
import json, sys

raw = json.load(open(sys.argv[1]))
add = raw.get("result", raw)
banks = json.load(open("banks/banks-all.json"))

def key_of(kind, item):
    if kind == "vocab": return item["en"].strip().lower()
    if kind == "reading": return item["title"].strip().lower()
    if kind == "speaking": return " ".join(item["passage"].split()[:5]).lower()
    return " ".join(item["prompt"].split()[:8]).lower()

report = {}
for lvl in banks:  # every level present in the banks file, no hardcoded list
    if lvl not in add: continue
    for kind in ("vocab", "reading", "speaking", "writing"):
        new_items = add[lvl].get(kind, [])
        if not new_items: continue
        existing = banks[lvl][kind]
        seen = {key_of(kind, it) for it in existing}
        kept, dropped = [], 0
        for it in new_items:
            k = key_of(kind, it)
            if k in seen: dropped += 1; continue
            seen.add(k); kept.append(it)
        before = len(existing)
        existing.extend(kept)
        report[f"{lvl}/{kind}"] = f"{before} -> {len(existing)} (+{len(kept)}, dup-dropped {dropped})"

json.dump(banks, open("banks/banks-all.json", "w"), ensure_ascii=False)
for k, v in report.items(): print(k, v)
