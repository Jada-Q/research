#!/usr/bin/env python3
"""Tests for merge_banks.py — run: python3 test_merge_banks.py

merge_banks.py is a CLI script that reads banks/banks-all.json relative to
cwd, so each test runs it via subprocess inside a temp working directory.
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "merge_banks.py")


def make_item(kind, tag):
    if kind == "vocab":
        return {"en": f"word-{tag}", "ja": f"訳-{tag}"}
    if kind == "reading":
        return {"title": f"Title {tag}", "body": "x"}
    if kind == "speaking":
        return {"passage": f"passage {tag} one two three four five"}
    return {"prompt": f"prompt {tag} one two three four five six seven eight"}


def empty_level():
    return {"vocab": [], "reading": [], "speaking": [], "writing": []}


def run_merge(banks, add):
    """Run merge_banks.py in a temp cwd; return (merged_banks, stdout)."""
    with tempfile.TemporaryDirectory() as tmp:
        os.mkdir(os.path.join(tmp, "banks"))
        banks_path = os.path.join(tmp, "banks", "banks-all.json")
        with open(banks_path, "w") as f:
            json.dump(banks, f, ensure_ascii=False)
        add_path = os.path.join(tmp, "add.json")
        with open(add_path, "w") as f:
            json.dump(add, f, ensure_ascii=False)
        proc = subprocess.run(
            [sys.executable, SCRIPT, add_path],
            cwd=tmp, capture_output=True, text=True,
        )
        if proc.returncode != 0:
            raise AssertionError(f"merge_banks.py failed:\n{proc.stderr}")
        with open(banks_path) as f:
            return json.load(f), proc.stdout


class TestAllLevels(unittest.TestCase):
    """The script must merge every level present in the banks file,
    not a hardcoded (3級, 4級) list."""

    def test_merges_jun2kyu_and_2kyu(self):
        banks = {lvl: empty_level() for lvl in ("3級", "4級", "準2級", "2級")}
        add = {
            "準2級": {"vocab": [make_item("vocab", "j2")]},
            "2級": {"vocab": [make_item("vocab", "n2")]},
        }
        merged, out = run_merge(banks, add)
        self.assertEqual(len(merged["準2級"]["vocab"]), 1, "準2級 vocab not merged")
        self.assertEqual(len(merged["2級"]["vocab"]), 1, "2級 vocab not merged")
        self.assertIn("準2級/vocab", out)
        self.assertIn("2級/vocab", out)

    def test_still_merges_3kyu_and_4kyu(self):
        banks = {lvl: empty_level() for lvl in ("3級", "4級", "準2級", "2級")}
        add = {
            "3級": {"reading": [make_item("reading", "a")]},
            "4級": {"writing": [make_item("writing", "b")]},
        }
        merged, out = run_merge(banks, add)
        self.assertEqual(len(merged["3級"]["reading"]), 1)
        self.assertEqual(len(merged["4級"]["writing"]), 1)

    def test_level_only_in_add_is_ignored(self):
        """A level in the workflow output but absent from banks must not crash
        and must not be merged (no bank bucket to merge into)."""
        banks = {"3級": empty_level()}
        add = {"1級": {"vocab": [make_item("vocab", "x")]}}
        merged, out = run_merge(banks, add)
        self.assertNotIn("1級", merged)
        self.assertNotIn("1級", out)


class TestDedupUnchanged(unittest.TestCase):
    """Dedup rules must stay identical for every level."""

    def test_vocab_dedup_by_en_lower(self):
        banks = {"準2級": empty_level()}
        banks["準2級"]["vocab"] = [{"en": "Apple", "ja": "りんご"}]
        add = {"準2級": {"vocab": [
            {"en": "apple ", "ja": "dup"},          # dup of existing (case/space)
            {"en": "banana", "ja": "new"},
            {"en": "BANANA", "ja": "dup-within-batch"},
        ]}}
        merged, out = run_merge(banks, add)
        ens = [it["en"] for it in merged["準2級"]["vocab"]]
        self.assertEqual(ens, ["Apple", "banana"])
        self.assertIn("準2級/vocab 1 -> 2 (+1, dup-dropped 2)", out)

    def test_speaking_dedup_by_first5_words(self):
        banks = {"2級": empty_level()}
        banks["2級"]["speaking"] = [{"passage": "The quick brown fox jumps over"}]
        add = {"2級": {"speaking": [
            {"passage": "The quick  brown fox JUMPS elsewhere entirely"},  # same first 5 words
            {"passage": "A totally different passage here now"},
        ]}}
        merged, out = run_merge(banks, add)
        self.assertEqual(len(merged["2級"]["speaking"]), 2)
        self.assertIn("2級/speaking 1 -> 2 (+1, dup-dropped 1)", out)

    def test_reading_dedup_by_title(self):
        banks = {"4級": empty_level()}
        banks["4級"]["reading"] = [{"title": "My Day"}]
        add = {"4級": {"reading": [{"title": "my day "}, {"title": "Other"}]}}
        merged, out = run_merge(banks, add)
        self.assertEqual(len(merged["4級"]["reading"]), 2)

    def test_writing_dedup_by_first8_words(self):
        banks = {"3級": empty_level()}
        p = "Do you like to play sports on weekends"
        banks["3級"]["writing"] = [{"prompt": p + " maybe"}]
        add = {"3級": {"writing": [{"prompt": p + " sometimes"}]}}
        merged, out = run_merge(banks, add)
        self.assertEqual(len(merged["3級"]["writing"]), 1)
        self.assertIn("3級/writing 1 -> 1 (+0, dup-dropped 1)", out)


class TestReportFormat(unittest.TestCase):
    def test_report_line_format(self):
        banks = {"準2級": empty_level()}
        add = {"準2級": {"vocab": [make_item("vocab", "1"), make_item("vocab", "2")]}}
        merged, out = run_merge(banks, add)
        self.assertIn("準2級/vocab 0 -> 2 (+2, dup-dropped 0)", out)

    def test_empty_kind_not_reported(self):
        banks = {"3級": empty_level()}
        add = {"3級": {"vocab": [], "reading": [make_item("reading", "r")]}}
        merged, out = run_merge(banks, add)
        self.assertNotIn("3級/vocab", out)
        self.assertIn("3級/reading", out)

    def test_result_wrapper_unwrapped(self):
        """Workflow output may wrap payload in {"result": {...}}."""
        banks = {"2級": empty_level()}
        add = {"result": {"2級": {"vocab": [make_item("vocab", "w")]}}}
        merged, out = run_merge(banks, add)
        self.assertEqual(len(merged["2級"]["vocab"]), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
