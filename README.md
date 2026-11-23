# Tool Harness Regression Check

Independent work sample for Trexo Global's AI Engineering Intern role, not affiliated with Trexo. Standard-library Python harness for three synthetic tool traces: successful lookup, no match, and unavailable tool. Compares a safe baseline with an intentionally regressed candidate using explicit expected outputs, argument schema, allowed tools, retry budgets and latency budgets.

Run `python harness.py --test` for 12 tests. Run `python harness.py` to reproduce results.json. Open index.html for a static results view. Fictional inputs only. No credentials, model calls, MCP server calls, AWS benchmarks or intellectual property data. The fixture latency is simulated, not a performance claim. A production system needs live transport tests, richer schemas, calibrated quality metrics and repeatable actual inference measurements.
