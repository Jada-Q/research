#!/usr/bin/env python3
"""Red/green tests for merge_banks.py multi-level support.

Runs merge_banks.py as a subprocess against a temp banks/banks-all.json
containing four levels (3級/4級/準2級/2級), asserting that:
  1. items for 準2級/2級 are merged (not silently ignored),
  2. dedup rules are unchanged (vocab by en.lower, reading by title.lower,
     speaking by first-5-words, writing by first-8-words),
  3. report line format is unchanged: "LVL/kind before -> after (+kept, dup-dropped N)",
  4. no level list is hardcoded: a banks file with an extra level still works.
"""
import json, os, shutil, subprocess, sys, tempfile, unittest

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "merge_banks.py")


def make_banks(levels):
    """Minimal banks dict: each level has the 4 kinds with one seed item."""
    banks = {}
    for lvl in levels:
        banks[lvl] = {
            "vocab": [{"en": f"seed-{lvl}", "ja": "x"}],
            "reading": [{"title": f"Seed Title {lvl}", "passage": "p"}],
            "speaking": [{"passage": f"seed passage words for level {lvl} here"}],
            "writing": [{"prompt": f"seed prompt words one two three four five {lvl}"}],
        }
    return banks


def run_merge(banks, add):
    """Write banks + add into a temp cwd, run merge_banks.py, return (banks_after, stdout)."""
    tmp = tempfile.mkdtemp(prefix="merge-banks-test-")
    try:
        os.makedirs(os.path.join(tmp, "banks"))
        with open(os.path.join(tmp, "banks", "banks-all.json"), "w") as f:
            json.dump(banks, f, ensure_ascii=False)
        addfile = os.path.join(tmp, "add.json")
        with open(addfile, "w") as f:
            json.dump(add, f, ensure_ascii=False)
        proc = subprocess.run(
            [sys.executable, SCRIPT, addfile],
            cwd=tmp, capture_output=True, text=True,
        )
        if proc.returncode != 0:
            raise AssertionError(f"merge_banks.py failed:\n{proc.stderr}")
        with open(os.path.join(tmp, "banks", "banks-all.json")) as f:
            after = json.load(f)
        return after, proc.stdout
    finally:
        shutil.rmtree(tmp)


LEVELS4 = ["3級", "4級", "準2級", "2級"]


class TestMultiLevelMerge(unittest.TestCase):
    def test_pre2kyu_and_2kyu_are_merged(self):
        add = {
            "準2級": {"vocab": [{"en": "brand-new", "ja": "y"}]},
            "2級": {"writing": [{"prompt": "totally new prompt with eight unique words here"}]},
        }
        after, out = run_merge(make_banks(LEVELS4), add)
        self.assertEqual(len(after["準2級"]["vocab"]), 2, "準2級 vocab item was not merged")
        self.assertEqual(len(after["2級"]["writing"]), 2, "2級 writing item was not merged")
        self.assertIn("準2級/vocab 1 -> 2 (+1, dup-dropped 0)", out)
        self.assertIn("2級/writing 1 -> 2 (+1, dup-dropped 0)", out)

    def test_existing_levels_still_merge(self):
        add = {"3級": {"vocab": [{"en": "new-3kyu-word", "ja": "z"}]},
               "4級": {"reading": [{"title": "New 4kyu Title", "passage": "p"}]}}
        after, out = run_merge(make_banks(LEVELS4), add)
        self.assertEqual(len(after["3級"]["vocab"]), 2)
        self.assertEqual(len(after["4級"]["reading"]), 2)
        self.assertIn("3級/vocab 1 -> 2 (+1, dup-dropped 0)", out)
        self.assertIn("4級/reading 1 -> 2 (+1, dup-dropped 0)", out)

    def test_dedup_rules_unchanged_on_new_levels(self):
        banks = make_banks(LEVELS4)
        add = {"準2級": {
            # duplicate of seed vocab (case-insensitive en) + one new
            "vocab": [{"en": "SEED-準2級", "ja": "dup"}, {"en": "fresh", "ja": "n"}],
            # duplicate of seed reading title (case-insensitive)
            "reading": [{"title": "seed title 準2級", "passage": "dup"}],
            # duplicate speaking: same first 5 words as seed
            "speaking": [{"passage": "seed passage words for level DIFFERENT tail entirely"}],
            # duplicate writing: same first 8 words as seed
            "writing": [{"prompt": "seed prompt words one two three four five EXTRA-TAIL"}],
        }}
        after, out = run_merge(banks, add)
        self.assertEqual(len(after["準2級"]["vocab"]), 2)  # 1 seed + 1 fresh, dup dropped
        self.assertEqual(len(after["準2級"]["reading"]), 1)
        self.assertEqual(len(after["準2級"]["speaking"]), 1)
        self.assertEqual(len(after["準2級"]["writing"]), 1)
        self.assertIn("準2級/vocab 1 -> 2 (+1, dup-dropped 1)", out)
        self.assertIn("準2級/reading 1 -> 1 (+0, dup-dropped 1)", out)
        self.assertIn("準2級/speaking 1 -> 1 (+0, dup-dropped 1)", out)
        self.assertIn("準2級/writing 1 -> 1 (+0, dup-dropped 1)", out)

    def test_no_hardcoded_level_list(self):
        # A hypothetical extra level in the banks file must also be handled.
        levels = LEVELS4 + ["1級"]
        add = {"1級": {"vocab": [{"en": "advanced-word", "ja": "a"}]}}
        after, out = run_merge(make_banks(levels), add)
        self.assertEqual(len(after["1級"]["vocab"]), 2, "level list appears hardcoded")
        self.assertIn("1級/vocab 1 -> 2 (+1, dup-dropped 0)", out)

    def test_intra_batch_dedup_and_result_wrapper(self):
        # {"result": {...}} wrapper + duplicate inside the new batch itself
        add = {"result": {"2級": {"vocab": [
            {"en": "twice", "ja": "1"}, {"en": "TWICE", "ja": "2"},
        ]}}}
        after, out = run_merge(make_banks(LEVELS4), add)
        self.assertEqual(len(after["2級"]["vocab"]), 2)  # seed + one "twice"
        self.assertIn("2級/vocab 1 -> 2 (+1, dup-dropped 1)", out)

    def test_level_in_add_missing_from_banks_does_not_crash(self):
        # add contains a level the banks file doesn't have -> skipped, no crash
        add = {"5級": {"vocab": [{"en": "nope", "ja": "x"}]},
               "3級": {"vocab": [{"en": "ok", "ja": "y"}]}}
        after, out = run_merge(make_banks(LEVELS4), add)
        self.assertNotIn("5級", after)
        self.assertEqual(len(after["3級"]["vocab"]), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
