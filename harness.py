"""Offline synthetic harness for Trexo's AI Engineering Intern role.
Not affiliated with Trexo. No model, MCP or AWS integration or real IP data.
Run: python harness.py; python harness.py --test
"""
import copy
import json
import sys
import unittest

CASES = [
    {"id": "lookup", "allowed": ["lookup"], "expected": "SYN-101", "max_attempts": 2, "budget_ms": 500},
    {"id": "no_match", "allowed": ["lookup"], "expected": "NO_MATCH", "max_attempts": 2, "budget_ms": 500},
    {"id": "timeout", "allowed": ["lookup"], "expected": "UNAVAILABLE", "max_attempts": 2, "budget_ms": 500},
]
BASELINE = [
    {"tool": "lookup", "args": {"query": "synthetic patent"}, "attempts": 1, "result": "SYN-101", "latency_ms": 120},
    {"tool": "lookup", "args": {"query": "unknown"}, "attempts": 1, "result": "NO_MATCH", "latency_ms": 90},
    {"tool": "lookup", "args": {"query": "unavailable"}, "attempts": 2, "result": "UNAVAILABLE", "latency_ms": 480},
]
CANDIDATE = copy.deepcopy(BASELINE)
CANDIDATE[0]["args"] = {"query": ""}
CANDIDATE[1]["result"] = "INVENTED-MATCH"
CANDIDATE[2].update(attempts=5, latency_ms=1200)


def grade(case, trace):
    errors = []
    if not isinstance(trace, dict):
        return ["invalid trace"]
    if trace.get("tool") not in case["allowed"]:
        errors.append("unexpected tool")
    args = trace.get("args")
    if not isinstance(args, dict) or set(args) != {"query"} or not isinstance(args.get("query"), str) or not args["query"].strip():
        errors.append("invalid tool arguments")
    attempts = trace.get("attempts")
    if type(attempts) is not int or not 1 <= attempts <= case["max_attempts"]:
        errors.append("retry budget exceeded or invalid")
    latency = trace.get("latency_ms")
    if type(latency) not in (int, float) or not 0 <= latency <= case["budget_ms"]:
        errors.append("latency budget exceeded or invalid")
    if trace.get("result") != case["expected"]:
        errors.append("result mismatch")
    return errors


def compare():
    results = []
    for case, base, candidate in zip(CASES, BASELINE, CANDIDATE):
        results.append({"case": case["id"], "baseline_errors": grade(case, base), "candidate_errors": grade(case, candidate)})
    return {"dataset": "synthetic-v1", "baseline": "fixture-v1", "candidate": "fixture-v2", "release": "BLOCK" if any(r["candidate_errors"] for r in results) else "PASS", "results": results, "limits": "Fictional traces and latency. No live model, MCP transport, AWS performance or patent correctness validated."}


class HarnessTests(unittest.TestCase):
    def test_baseline(self):
        self.assertTrue(all(not grade(c, t) for c, t in zip(CASES, BASELINE)))
    def test_candidate(self):
        self.assertTrue(all(grade(c, t) for c, t in zip(CASES, CANDIDATE)))
    def test_invalid_trace(self):
        self.assertEqual(grade(CASES[0], None), ["invalid trace"])
    def test_extra_arg(self):
        self.assertIn("invalid tool arguments", grade(CASES[0], dict(BASELINE[0], args={"query": "x", "delete": True})))
    def test_non_string_query(self):
        self.assertIn("invalid tool arguments", grade(CASES[0], dict(BASELINE[0], args={"query": 1})))
    def test_unknown_tool(self):
        self.assertIn("unexpected tool", grade(CASES[0], dict(BASELINE[0], tool="delete")))
    def test_bool_retries(self):
        self.assertIn("retry budget exceeded or invalid", grade(CASES[0], dict(BASELINE[0], attempts=True)))
    def test_zero_retries(self):
        self.assertIn("retry budget exceeded or invalid", grade(CASES[0], dict(BASELINE[0], attempts=0)))
    def test_boundary(self):
        self.assertEqual(grade(CASES[0], dict(BASELINE[0], attempts=2, latency_ms=500)), [])
    def test_nan(self):
        self.assertIn("latency budget exceeded or invalid", grade(CASES[0], dict(BASELINE[0], latency_ms=float("nan"))))
    def test_missing_result(self):
        t = copy.deepcopy(BASELINE[0]); del t["result"]
        self.assertIn("result mismatch", grade(CASES[0], t))
    def test_immutable(self):
        before = copy.deepcopy(BASELINE); compare()
        self.assertEqual(before, BASELINE)


if __name__ == "__main__":
    if "--test" in sys.argv:
        unittest.main(argv=[sys.argv[0]])
    else:
        print(json.dumps(compare(), indent=2))
