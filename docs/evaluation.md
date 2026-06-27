# Evaluation

The eval set is structural: it tests that the validator catches the specific
malformed-definition cases that block tenant provisioning. Each case is a tiny
inline JSON definition + the validation outcome it should produce.

## What it does

[evals/run.py](../evals/run.py) loads [evals/golden.json](../evals/golden.json),
calls `validate(definition)` on each case, and checks whether the result
matches `expect.valid` and contains any required error substrings. Exit code
is 0 if all pass — suitable for CI gating.

```text
Eval: 14/14 passed (100%)
```

On failure you get the specific mismatch:

```text
Eval: 13/14 passed (93%)

1 failed:
  [duplicate-section-keys]
       missing expected error substring "duplicate section key 'hr'"
```

## Case format

Each case in `golden.json`:

```json
{
  "id": "nav-points-at-undefined-section",
  "definition": {
    "org": "Acme", "tenant": "acme.sharepoint.com", "hub": {"title": "x"},
    "sites": [{"key": "hr", "title": "HR"}],
    "navigation": {"global": [{"label": "Policies", "page": "policies"}]}
  },
  "expect": {
    "valid": false,
    "errors_contain": ["referenced in nav but not defined"]
  }
}
```

| Expect field | Meaning |
|--------------|---------|
| `valid` | `true` if the definition should pass validation; `false` if at least one blocking error is expected. |
| `errors_contain` | List of substrings the blocking errors must include (order-independent). |
| `warnings_contain` | Same, but for warnings (non-blocking). |

The eval intentionally inlines the definitions in JSON so a non-engineer can
read or extend the set without touching Python.

## Adding cases

Three patterns:

**1. Capture every real-world malformed definition.** When you onboard a
client and they hand you a broken JSON, add it (minimally trimmed) as a case
with the right `errors_contain` before changing any validator code. The eval
set is your regression net.

**2. Add the positive case alongside the negative.** For every "X is invalid"
case, add an "X is valid" case so the validator can't drift into rejecting
everything. (Look at `minimal-valid` for the template.)

**3. Add a case the moment you tighten a rule.** A new rule is a contract;
the eval case is the proof. Without it, six months later someone will relax
the rule "because it was flaky" without noticing the regression.

## Workflow when tuning

1. Add the failing case(s) to `golden.json`.
2. Run `python evals/run.py` and see them fail.
3. Change the validation rule in [validate.py](../intranet_gen/validate.py).
4. Re-run. Iterate until 100% pass and existing cases didn't regress.

## What an eval set is not

- **Not a JSON schema replacement.** The eval set tests *behaviour*, not
  *structure*. A proper JSON Schema would catch type mismatches as a separate
  layer; the validator here catches the semantic rules schema alone can't.
- **Not coverage for the renderer.** The unit tests in [tests/](../tests/)
  cover render output (FAQ accordion, person card, HTML escaping, etc).
  Validation evals don't render anything.
- **Not exhaustive.** 14 cases here are illustrative. A serious deployment
  with custom validation rules typically has 30+.
