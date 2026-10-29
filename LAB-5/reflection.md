# Reflection — Lab 5: Static Code Analysis

## 1. Which issues were the easiest to fix, and which were the hardest? Why?

**Easiest:** the Flake8 and style findings, such as a missing trailing newline, `== None` → `is None`, the unused `math` import, long lines and missing docstrings. Each one has a single obvious mechanical fix, the tool gives the exact line and column, and the fix cannot change behaviour.

**Hardest:** `eval(promo_expr)` (Bandit B307). Deleting `eval` breaks the feature, so I had to work out what the code was *meant* to do, which is apply a promotional discount. I then changed the function's interface to take a numeric `discount_percent` with range validation. The `os.system` call needed similar thinking, because the real requirement was only to tell the user the ticket had been sent and a shell was never needed for that. Renaming the camelCase functions was simple but touched every call site, so I had to rerun the program to confirm nothing broke.

## 2. Did the static analysis tools report any false positives? If so, describe one example.

There were no outright false positives, but some findings depend on context:

- **Bandit B311 (`random.randint`)** is only a real problem because the value is a POS **PIN**. If the same call shuffled a demo menu, it would be a false positive, and suppressing it with `# nosec` would be reasonable.
- **Bandit B324 (MD5)** fires because MD5 *could* be used for security. If the ticket hash were only a non-security checksum, `hashlib.md5(..., usedforsecurity=False)` would also satisfy Bandit. I chose SHA-256 because ticket identifiers should not be forgeable.

The opposite problem, **false negatives**, mattered more. No tool flagged the hard-coded `POS_TERMINAL_SECRET_TOKEN_2026` that was printed to the console. Bandit's B105 check looks for variable names such as `password`/`secret`/`token`, and `pos_terminal_key` did not match. No tool flagged the out-of-order output caused by `os.system` writing to the console outside Python's print buffer either. I only found it by running the program. Static analysis supplements code review and testing but does not replace them.

## 3. How would you integrate static analysis tools into your actual software development workflow?

- **Locally:** run Flake8 and Pylint in the editor (VS Code extensions) for instant feedback, and add a **pre-commit hook** (`pre-commit` framework) that runs `flake8`, `pylint --fail-under=9.5` and `bandit -q -r .` before every commit.
- **In CI (e.g. GitHub Actions):** run all three tools on every push and pull request, and fail the build on any Bandit Medium/High finding, any Flake8 error or a Pylint score below the threshold. Upload the reports as build artefacts.
- **Configuration:** keep a shared `.pylintrc` / `setup.cfg` / `.bandit` in the repo so every developer and CI run use the same rules. Only allow justified, commented suppressions (`# nosec`, `# pylint: disable=...`).
- **Legacy code:** introduce the tools gradually, by checking only changed files or setting a baseline and ratcheting the threshold upwards.

## 4. What tangible improvements did you observe in code quality, readability, or robustness after applying the fixes?

- **Security:** all five Bandit findings, including two High, went to **zero**. The program can no longer execute arbitrary code (`eval`) or shell commands (`os.system`), and the secret is no longer in source code or console output.
- **Correctness:** the output now prints in the correct order. Log entries no longer leak between calls through the shared mutable default. `void_table_order` reports whether it actually removed anything instead of silently swallowing all errors. The export file is always closed, even on error, and is written as UTF-8.
- **Readability:** PEP 8 function names, docstrings on every function, f-strings, a one-line `return not ...` and a `sum()` generator make the code shorter and easier to follow.
- **Reusability/testability:** the `if __name__ == "__main__":` guard means the module can be imported and unit-tested without side effects.
- **Measured result:** Pylint went from **4.81 → 10.00/10** and Flake8 from **9 → 0** violations, and the program produces the same business results as before (discounted bill 40.5, 3 pending tables).
