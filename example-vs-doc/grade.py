#!/usr/bin/env python3
"""Grade example-vs-doc arm outputs against the 10 written-convention markers.
Usage: python3 grade.py arms/EX1 arms/EX2 arms/DOC1 arms/DOC2
Each arm dir needs duration.js + duration.test.js.
v2: M3 accepts both `export function durX` and `export const durX =` —
v1's function-only regex false-flagged the DOC arms (lesson: verify the verifier)."""
import re, sys, os

for d in sys.argv[1:]:
    src = open(os.path.join(d, "duration.js")).read()
    tst = open(os.path.join(d, "duration.test.js")).read()
    exports = re.findall(r"export (?:function|const) (\w+)", src)
    checks = {
        "M1 header(src)":    bool(re.match(r"^// module: duration — ", src)),
        "M1b header(test)":  bool(re.match(r"^// module: duration\.test — ", tst)),
        "M2 outcome import": "lib/outcome.js" in src and "ok(" in src and "fail(" in src,
        "M3 dur prefix":     len(exports) >= 2 and all(n.startswith("dur") for n in exports),
        "M4 no throw":       "throw" not in src,
        "M5 @spec per export": len(re.findall(r"@spec ", src)) >= 2,
        "M6 [caseNN]+node:test": "node:test" in tst and len(re.findall(r"\[case\d\d\]", tst)) >= 4,
        "M6b deepEqual":     "deepEqual" in tst,
        "M6c kebab reasons": bool(re.findall(r"fail\('[a-z]+(-[a-z]+)+'\)", src)),
        "M3b named export only": "export default" not in src,
    }
    passed = sum(checks.values())
    fails = [k for k, v in checks.items() if not v]
    print(f"{d}: {passed}/{len(checks)}" + ("" if not fails else "  FAIL: " + ", ".join(fails)))
